import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="
HTML_FILE = "page.html"


def get_html():
    # If we already saved the page, reuse it (no need to download again)
    if os.path.exists(HTML_FILE):
        print("Using saved file:", HTML_FILE)
        with open(HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    print("Downloading page...")
    headers = {"User-Agent": "Mozilla/5.0 (student learning project)"}
    response = requests.get(URL, headers=headers, timeout=30)
    print("Status code:", response.status_code)
    response.raise_for_status()  # stops with an error if the download failed

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved page to", HTML_FILE)
    return response.text


html = get_html()
soup = BeautifulSoup(html, "html.parser")

print("\n===== PAGE SUMMARY =====")
print("Title:", soup.title.get_text(strip=True) if soup.title else "none")
print("Headings (h1-h3):", len(soup.find_all(["h1", "h2", "h3"])))

tables = soup.find_all("table")
print("Tables:", len(tables))
for i, table in enumerate(tables[:2]):
    print(f"\n--- Table {i + 1}: first 4 rows ---")
    for row in table.find_all("tr")[:4]:
        cells = [c.get_text(" ", strip=True)[:60] for c in row.find_all(["th", "td"])]
        print(cells)

links = soup.find_all("a", href=True)
print("\nTotal links:", len(links))
print("--- First 15 links that mention 'scheme' ---")
shown = 0
for a in links:
    if "scheme" in a["href"].lower() or "scheme" in a.get_text().lower():
        print(a.get_text(" ", strip=True)[:70], "->", a["href"])
        shown += 1
        if shown == 15:
            break

print("\n--- First 700 characters of visible text ---")
print(soup.get_text(" ", strip=True)[:700])