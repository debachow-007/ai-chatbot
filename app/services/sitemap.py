import requests
from bs4 import BeautifulSoup

SITEMAP_URL = "https://vibescom.in/sitemap.xml"

_cached_pages = []

def load_sitemap():
    global _cached_pages
    if _cached_pages:
        return _cached_pages

    res = requests.get(SITEMAP_URL)
    soup = BeautifulSoup(res.text, "xml")
    pages = []

    for loc in soup.find_all("loc"):
        url = loc.text
        name = url.rstrip("/").split("/")[-1] or "home"
        pages.append({"title": name.replace("-", " ").title(), "url": url})

    _cached_pages = pages
    return pages
