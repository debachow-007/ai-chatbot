import asyncio
import httpx
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from datetime import datetime, UTC
import trafilatura

SITEMAP_URL = "https://vibescom.in/sitemap.xml"
OUTPUT_FILE = Path("harvested/harvested_latest.jsonl")
OUTPUT_FILE.parent.mkdir(exist_ok=True)


async def fetch(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def parse_sitemap(xml_content: str) -> list[str]:
    urls = []
    root = ET.fromstring(xml_content)

    # namespace fix
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    for loc in root.findall(".//sm:loc", ns):
        urls.append(loc.text.strip())

    return urls


async def process_page(url: str) -> dict | None:
    try:
        html = await fetch(url)
        text = trafilatura.extract(html, include_comments=False)
        if not text:
            return None

        print(f"Extracted: {url}")

        return {
            "url": url,
            "content": text,
        }

    except Exception as e:
        print(f"Failed: {url} — {e}")
        return None


async def run_crawler():
    print("Fetching sitemap...")
    sitemap_xml = await fetch(SITEMAP_URL)
    urls = parse_sitemap(sitemap_xml)

    print(f"Found {len(urls)} URLs in sitemap")

    results = []
    for url in urls:
        page_data = await process_page(url)
        if page_data:
            results.append(page_data)

    # Write output file
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(results)} pages → {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(run_crawler())
