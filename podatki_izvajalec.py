import re
import requests
import unicodedata
from bs4 import BeautifulSoup


from uporabniski_posrednik import SEJA


def prenesi_html(url, timeout=10):
    """Prenese HTML strani izvajalca."""
    try:
        r = SEJA.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[OPOZORILO] Neuspešen prenos strani izvajalca: {e}")
        return None


def poisci_vrednost_v_infoboxu(infobox, kljuci):
    """
    Vrne besedilo iz <td> v vrstici infoboxa, kjer <th> vsebuje katerokoli
    izmed besed v 'kljuci'. Če ni zadetkov, vrne None.
    """
    if not infobox:
        return None

    for th in infobox.find_all("th"):
        naslov = th.get_text(" ", strip=True).lower()
        if any(k in naslov for k in kljuci):
            td = th.find_next_sibling("td")
            if not td:
                return None
            return td.get_text(" ", strip=True) or None
    return None



def zadnji_segment_po_vejici(tekst=None):
    """
    Vzame zadnji segment po ločilih (vejica, podpičje, pika-sredina, dolgi pomišljaji).
    Vrne stripan niz ali None.
    """
    if not tekst:
        return None

    # poenotenje ločil v vejice
    zamenjave = {
        "—": ",", "–": ",",  
        "·": ",", ";": ","
    }
    for k, v in zamenjave.items():
        tekst = tekst.replace(k, v)

    # razreži, očisti, filtriraj prazne
    deli = [d.strip(" \t\n\r-") for d in tekst.split(",")]
    deli = [d for d in deli if d]

    if not deli:
        return None
    return deli[-1]


def normaliziraj_drzavo(n):
    """Normalizira različice imen držav (robustnejša različica, brez odvisnosti od mreže)."""
    if not n:
        return None

    # Osnovno čiščenje
    x = n.strip()
    x = unicodedata.normalize("NFKD", x)
    x = re.sub(r"[’‘`]", "'", x)
    x = re.sub(r"[.,]", "", x)
    x = re.sub(r"\s+", " ", x).strip()

    low = x.lower()
    if low.startswith("the "):
        low = low[4:].strip()

    MAP = {
        # --- ZDA ---
        "us": "United States", "u s": "United States",
        "usa": "United States", "u s a": "United States",
        "united states": "United States",
        "united states of america": "United States",
        "america": "United States",
        "u.s": "United States", "u.s.a": "United States",
        "alabama": "United States",
        "alaska": "United States",
        "arizona": "United States",
        "arkansas": "United States",
        "california": "United States",
        "colorado": "United States",
        "connecticut": "United States",
        "delaware": "United States",
        "florida": "United States",
        "georgia": "United States",
        "hawaii": "United States",
        "idaho": "United States",
        "illinois": "United States",
        "indiana": "United States",
        "iowa": "United States",
        "kansas": "United States",
        "kentucky": "United States",
        "louisiana": "United States",
        "maine": "United States",
        "maryland": "United States",
        "massachusetts": "United States",
        "michigan": "United States",
        "minnesota": "United States",
        "mississippi": "United States",
        "missouri": "United States",
        "montana": "United States",
        "nebraska": "United States",
        "nevada": "United States",
        "new hampshire": "United States",
        "new jersey": "United States",
        "new mexico": "United States",
        "new york": "United States",
        "north carolina": "United States",
        "north dakota": "United States",
        "ohio": "United States",
        "oklahoma": "United States",
        "oregon": "United States",
        "pennsylvania": "United States",
        "rhode island": "United States",
        "south carolina": "United States",
        "south dakota": "United States",
        "tennessee": "United States",
        "texas": "United States",
        "utah": "United States",
        "vermont": "United States",
        "virginia": "United States",
        "washington": "United States",
        "west virginia": "United States",
        "wisconsin": "United States",
        "wyoming": "United States",


        # --- Združeno kraljestvo ---
        "uk": "United Kingdom", "u k": "United Kingdom",
        "united kingdom": "United Kingdom",
        "great britain": "United Kingdom", "britain": "United Kingdom",
        "england": "United Kingdom", "scotland": "United Kingdom",
        "wales": "United Kingdom", "northern ireland": "United Kingdom",

        # --- Koreji ---
        "south korea": "South Korea", "republic of korea": "South Korea",
        "korea south": "South Korea",
        "north korea": "North Korea", "dprk": "North Korea",
        "korea north": "North Korea",

        # --- Druge države ---
        "netherlands": "Netherlands", "the netherlands": "Netherlands",
        "czech republic": "Czechia", "czechia": "Czechia",
        "czech rep": "Czechia",
        "russian federation": "Russia", "russia": "Russia",
        "uae": "United Arab Emirates", "united arab emirates": "United Arab Emirates",
        "emirates": "United Arab Emirates",
        "côte d’ivoire": "Ivory Coast", "cote d'ivoire": "Ivory Coast",
        "ivory coast": "Ivory Coast",
        "republic of ireland": "Ireland",
        "viet nam": "Vietnam", "vietnam": "Vietnam",
    }

    # Natančno ujemanje
    if low in MAP:
        return MAP[low]

    # Delno ujemanje (če niz vsebuje znan ključ)
    for k, v in MAP.items():
        if k in low:
            return v

    # Privzeto normalizirano ime
    return x.title() if " " in x else x.capitalize()

def drzava_iz_polja(tekst):
    """
    Iz besedila iz infoboxaposkusi izluščiti državo.

    Uporabi zadnji segment po vejici in ga normalizira.
    Če rezultat izgleda kot datum (vsebuje številke), vrne None.
    """
    if not tekst:
        return None

    kandidat = zadnji_segment_po_vejici(tekst)
    if not kandidat:
        return None

    # Če vsebuje številke, zelo verjetno ni država, ampak datum (npr. '1 January 1990')
    if any(ch.isdigit() for ch in kandidat):
        return None

    return normaliziraj_drzavo(kandidat)

def izlusci_leto_rojstva(tekst):
    """
    Iz besedila vzame prvo 4 mestno stevilo ki izgleda kot leto
    """
    if not tekst:
        return None

    m = re.search(r"\b(19[0-9]{2}|20[0-2][0-9])\b", tekst) 
    if m:
        return m.group(1)

    return None


def pridobi_podatke_izvajalca(url_izvajalec):
    """
    izlusci drzavo in leto rojstva iz strani izvajalca
    """
    if not url_izvajalec:
        return None, None

    html = prenesi_html(url_izvajalec)
    if not html:
        return None, None

    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_=lambda c: c and "infobox" in c)
    if not infobox:
        return None, None

    origin_txt = poisci_vrednost_v_infoboxu(infobox, {"origin"})
    natcit_txt = poisci_vrednost_v_infoboxu(infobox, {"nationality", "citizenship"})
    born_txt = poisci_vrednost_v_infoboxu(infobox, {"born"})

    leto_rojstva = izlusci_leto_rojstva(born_txt)

    origin = drzava_iz_polja(origin_txt)
    natcit = drzava_iz_polja(natcit_txt)
    born = drzava_iz_polja(born_txt)

    if origin:
        drzava = origin
    elif natcit and born and natcit == born:
        drzava = natcit
    elif born:
        drzava = born
    else:
        drzava = natcit or None

    return drzava, leto_rojstva


