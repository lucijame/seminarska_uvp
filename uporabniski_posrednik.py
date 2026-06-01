import requests

GLAVA = {
    "User-Agent": (
        "BillboardResearchBot/1.0 "
        "https://github.com/lucijame/seminarska_uvp "
        "lucija.medja@gmail.com)"
    )
}

# Globalna seja (ponovna uporaba povezav za hitrejše poizvedbe)
SEJA = requests.Session()
SEJA.headers.update(GLAVA)