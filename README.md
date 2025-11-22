# README.md

# Seminarska naloga: Scrapanje Billboard lestvic in analiza izvajalcev

Projekt avtomatsko pridobi podatke iz Billboard Year-End Hot 100 lestvic na Wikipediji (za leta 2015–2024) ter zbere dodatne informacije o izvajalcih (država izvora in leto rojstva). Podatki se nato shranijo v več CSV datotek, ki omogočajo nadaljnjo analizo.

## Struktura projekta

```
projekt/
│
├── glavna_datoteka.py
├── scrapanje_billboarda.py
├── podatki_izvajalec.py
├── uporabniski_posrednik.py
│
├── singles.csv
├── razsirjeno.csv
├── izvajalci_drzava.csv
│
└── analiza_billboard.ipynb
```

## Opis delovanja

Najprej sem v datoteki `scrapanje_billboarda.py` sestavila funkcijo, ki je iz posamezne Wikipedijine strani »Billboard Year-End Hot 100« izluščila podatke o pesmih za izbrano leto. To funkcijo sem nato uvozila v osrednjo datoteko `glavna_datoteka.py`, kjer sem z zanko for iterirala skozi leta, ki sem jih želela obdelati. Vanjo sem uvozila tudi funkcije iz datoteke `podatki_izvajalec.py`, ki sem jih uporabila za pridobivanje dodatnih podatkov o izvajalcih (država izvora in leto rojstva) s posameznih Wikipedijinih strani izvajalcev.

V datoteki `uporabniski_posrednik.py` sem definirala uporabniškega posrednika, ki sem ga nato uvozila v ustrezne datoteke, da bi zagotovila stabilnejše povezave in preprečila, da bi me strežnik zaradi številnih zahtevkov začel zavračati.

Zbrane podatke sem s pomočjo skripte `glavna_datoteka.py` shranila v datotekah `singles.csv`, `razsirjeno.csv` in `izvajalci_drzava.csv`, nato pa sem jih uvozila v zvezek `analiza_billboard.ipynb`, kjer sem izvedla analizo ter rezultate grafično predstavila in interpretirala.


## Viri podatkov

1. Billboard Year-End Hot 100 strani na Wikipediji.
2. Wikipedia strani posameznih izvajalcev (infobox podatki).

## Navodila za zagon

Uporabnik zažene `glavna_datotek.py`. Ta ustvari `singles.csv`, `razsirjeno.csv` in `izvajalci_drzava.csv`. Te datoteke so potrebne za analizo. Nato odpre `analiza_billboard.ipynb` in izvede analizo.