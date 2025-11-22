
import csv
import time

from scrapanje_billboarda import pridobi_leto
from podatki_izvajalec import pridobi_podatke_izvajalca

# --------------------NASTAVITVE---------------------------

ZACETNO_LETO = 2015
KONCNO_LETO = 2024


# -------------------POMOŽNE FUNKCIJE----------------------
def shrani_csv(ime, podatki, polja):
    """Shrani seznam slovarjev v CSV datoteko."""
    with open(ime, "w", encoding="utf-8", newline="") as f:
        pisec = csv.DictWriter(f, fieldnames=polja, extrasaction="ignore")
        pisec.writeheader()
        for p in podatki:
            pisec.writerow(p)



# ------------------GLAVNI PROGRAM-------------------------
def main():
    vsi_podatki = []

    # Zajem vseh pesmi za vsa leta
    for leto in range(ZACETNO_LETO, KONCNO_LETO + 1):
        print(f"Zajemam podatke za leto {leto} …")
        leto_podatki = pridobi_leto(leto)
        if leto_podatki:
            vsi_podatki.extend(leto_podatki)
        else:
            print(f"[OPOZORILO] Ni podatkov za leto {leto}.")
        # majhna pavza, da ne preobremenimo Wikipedije
        time.sleep(0.5)

    if not vsi_podatki:
        print("Ni podatkov – preveri povezave ali omrežje.")
        return
    
    shrani_csv(
        "singles.csv",
        vsi_podatki,
        ["leto", "mesto", "naslov", "avtorji"],
    )


    # Zgradimo razširjeno tabelo + velik slovar izvajalcev
    razsirjeno_vrstice = []   # vsaka vrstica: leto, mesto, naslov, izvajalec
    vsi_izvajalci = {}        # ime izvajalca -> en URL (če ga imamo)

    for p in vsi_podatki:
        leto = p["leto"]
        mesto = p["mesto"]
        naslov = p["naslov"]

        # p["izvajalci"] je slovar {ime: url}
        for ime, url in p["izvajalci"].items():
            # Razširjena vrstica: ena vrstica na izvajalca
            razsirjeno_vrstice.append({
                "leto": leto,
                "mesto": mesto,
                "naslov": naslov,
                "izvajalec": ime,
            })

            # Gradimo velik slovar vseh izvajalcev
            if ime not in vsi_izvajalci:
                vsi_izvajalci[ime] = url
            else:
                if vsi_izvajalci[ime] is None and url:
                    vsi_izvajalci[ime] = url

    # Shranimo razširjeno tabelo brez URL-jev
    shrani_csv(
        "razsirjeno.csv",
        razsirjeno_vrstice,
        ["leto", "mesto", "naslov", "izvajalec"],
    )
    print("Shranjena datoteka razsirjeno.csv (leto, mesto, naslov, izvajalec).")

    print("Število različnih izvajalcev:", len(vsi_izvajalci))


    # Za VSE izvajalce poiščemo državo (en klic na izvajalca)
    izvajalci_drzave = []

    for ime, url in vsi_izvajalci.items():
        if not url:
            print(f"[INFO] Preskakujem iskanje države za '{ime}' (brez URL-ja).")
            drzava, leto_rojstva = None, None
        else:
            drzava, leto_rojstva = pridobi_podatke_izvajalca(url)
            # pavza, da ne preobremenimo Wikipedije
            time.sleep(0.5)


        izvajalci_drzave.append({
            "izvajalec": ime,
            "drzava": drzava,
            "leto_rojstva": leto_rojstva,
        })

    # CSV: vsi izvajalci + država + link
    shrani_csv(
        "izvajalci_drzava.csv",
        izvajalci_drzave,
        ["izvajalec", "drzava", "leto_rojstva"],
    )
    print("Shranjena datoteka izvajalci_drzava.csv (izvajalec, drzava, url).")


if __name__ == "__main__":
    main()


