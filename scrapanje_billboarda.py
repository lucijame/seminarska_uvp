# -*- coding: utf-8 -*-

"""
Prenos in razčlenjevanje Billboard Year-End Hot 100 iz Wikipedije.
"""
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from uporabniski_posrednik import SEJA

# --------------------------- URL & PRENOS ------------------------------------

def povezava_billboard(leto):
    """Vrne URL do 'Billboard Year-End Hot 100 singles of {leto}'."""
    return f"https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{(leto)}"

def absolutni_wiki_url(href):
    """Pretvori wiki href v absoluten https URL."""
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href.replace("http://", "https://", 1)
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return urljoin("https://en.wikipedia.org", href)
    return href

def prenesi_html(url, poskusi = 3, timeout = 10):
    """Prenese HTML z več poskusi (preprost backoff)."""
    for i in range(1, poskusi + 1):
        try:
            r = r = SEJA.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException as e:
            print(f"[OPOZORILO] Poskus {i}/{poskusi} za {url} ni uspel: {e}")
            if i == poskusi:
                return None
            time.sleep(2 * i)
    return None

# ----------------------- ISKANJE PRAVE TABELE --------------------------------

def izberi_tabelo(soup: BeautifulSoup):
    """Najde tabelo wikitable z rank/title/artist."""
    tabele = soup.find_all("table", class_="wikitable")
    if not tabele:
        return None

    def normalizirano(s):
        return re.sub(r"\s+", " ", s or "").strip().lower()

    kljuci_rank = {"rank", "no.", "position", "№"}
    kljuci_title = {"title", "song", "single"}
    kljuci_artist = {"artist", "performer"}


    for t in tabele:
        head = t.find("tr")
        if not head:
            continue
        thji = [normalizirano(th.get_text(" ", strip=True)) for th in head.find_all("th")]
        if not thji:
            continue
        ima_rank = any(any(k in h for k in kljuci_rank) for h in thji)
        ima_title = any(any(k in h for k in kljuci_title) for h in thji)
        ima_artist = any(any(k in h for k in kljuci_artist) for h in thji)
        if ima_rank and (ima_title or ima_artist):
            return t
        
    
    return None


# ----------------------: IZVOZ VSEH IZVAJALCEV + LINKOV ----------------
def normaliziraj_ime(ime):
    # poseben primeri
    popravki = {
        "P!nk": "Pink",
        "the Weeknd": "The Weeknd",
    }
    if ime in popravki:
        return popravki[ime]

    # odstrani nepotrebne presledke
    ime = ime.strip()

    # naslovni zapis (ne koristi za npr. iLoveMemphis → Ilovememphis!!!)
    # zato ga uporabimo le za normalna imena:
    if " " in ime or "-" in ime:
        ime = ime.title()

    return ime


def izvoz_izvajalcev(td):
    """
    Najde izvajalce iz <td> najprej iz <a> elementov, potem še iz surovega besedila
    """
    if not td:
        return {}, []
    
    avtorji_slovar = {}
    avtorji_seznam = []

    #regex za deljenje imen
    delitelj = re.compile(r'\s*(?:,|and|feat\.|featuring|with)\s*', re.IGNORECASE)

    for element in td.contents:
        if element.name == "a":  
            ime = re.sub(r"\s+", " ", element.get_text(strip=True))
            ime = ime.strip("()[]{}\"'/\\:")
            ime = normaliziraj_ime(ime)
            href = element.get("href", "").strip()
            href = absolutni_wiki_url(href)
            avtorji_slovar[ime] = href
            avtorji_seznam.append(ime)
        elif element.string and element.string.strip():
            parts = delitelj.split(element.string)
            for p in parts:
                ime = p.strip()
                ime = ime.strip("()[]{}\"'/\\:")
                ime = normaliziraj_ime(ime)
                if ime:
                    avtorji_slovar[ime] = None
                    avtorji_seznam.append(ime)


    return avtorji_slovar, avtorji_seznam 


# -------------------------- RAZČLENJEVANJE TABELE ----------------------------

def razcleni_tabelo(tabela, leto):
    """Iz tabele prebere vrstice in vrne podatke o pesmih in izvajalcih."""
    vrstice = []
    glava = tabela.find("tr")
    if not glava:
        return vrstice

    ths = [th.get_text(" ", strip=True).lower() for th in glava.find_all("th")]
    idx_rank = idx_title = idx_artist = None

    kljuci_rank = {"rank", "no.", "position", "№"}
    kljuci_title = {"title", "song", "single"}
    kljuci_artist = {"artist", "performer"}

    for i, h in enumerate(ths):
        if idx_rank is None and any(k in h for k in kljuci_rank):
            idx_rank = i
        if idx_title is None and any(k in h for k in kljuci_title):
            idx_title = i
        if idx_artist is None and any(k in h for k in kljuci_artist):
            idx_artist = i


    trenutni_izvajalci = ({}, [])
    preostanek_rowspan = 0

    
    #za vsako vrstico tabele najde mesto, naslov in avtorje
    for tr in tabela.find_all("tr")[1:]:
        tds = tr.find_all(["td", "th"])
        if not tds:
            continue


        # mesto (rank)
        mesto = None
        if idx_rank is not None and idx_rank < len(tds):
            rank_txt = tds[idx_rank].get_text(" ", strip=True)
            m = re.match(r"\d+", rank_txt or "")
            if m:
                try:
                    mesto = int(m.group(0))
                except ValueError:
                    mesto = None

        # naslov
        naslov = None

        if idx_title is not None and idx_title < len(tds):
            naslov = (tds[idx_title].get_text(" ", strip=True))
            naslov = re.sub(r"\s+", " ", naslov).strip()
            naslov = naslov.strip('“”"\'‘’')


        # izvajalci + linki (uporaba rowspan logike)
        avtorji_slovar, avtorji_seznam = {}, []

        if idx_artist is not None and idx_artist < len(tds):
            # preveri ali ima celica rowspan
            td_artist = tds[idx_artist]
            rowspan = td_artist.get("rowspan")

            if rowspan:
                try:
                    preostanek_rowspan = int(rowspan)
                except:
                    preostanek_rowspan = 1
            else:
                rowspan = None

            avtorji_slovar, avtorji_seznam = izvoz_izvajalcev(td_artist)

            # shrani trenutne izvajalce za naslednje vrstice
            trenutni_izvajalci = (avtorji_slovar, avtorji_seznam)
            preostanek_rowspan -= 1

        else:
            # ni artists td — morda je to vrstica pod rowspanom
            if preostanek_rowspan > 0:
                avtorji_slovar, avtorji_seznam = trenutni_izvajalci
                preostanek_rowspan -= 1
            else:
                avtorji_slovar, avtorji_seznam = {}, []


        if not naslov:
            continue

        vrstice.append({
            "leto": int(leto),
            "mesto": mesto,
            "naslov": naslov,
            "avtorji": " | ".join(avtorji_seznam),
            "izvajalci": avtorji_slovar,
        })

    return vrstice

# ------------------------------ GLAVNI KLIC ----------------------------------

def pridobi_leto(leto):
    """Za dano leto prenese stran, najde tabelo in jo razčleni."""
    url = povezava_billboard(leto)
    html_str = prenesi_html(url)
    if not html_str:
        return []
    soup = BeautifulSoup(html_str, "html.parser")
    tabela = izberi_tabelo(soup)
    if not tabela:
        return []
    return razcleni_tabelo(tabela, leto)
