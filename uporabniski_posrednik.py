import requests

GLAVA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

# Globalna seja (ponovna uporaba povezav za hitrejše poizvedbe)
SEJA = requests.Session()
SEJA.headers.update(GLAVA)