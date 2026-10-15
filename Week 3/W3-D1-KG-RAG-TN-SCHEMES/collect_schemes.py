import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.tn.gov.in/"
LIST_FILE = "page.html"          # the list page we saved in Step 3
HEADERS = {"User-Agent": "Mozilla/5.0 (student learning project)"}

# ---------- PART 1: collect all scheme links from the list page ----------
with open(LIST_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

schemes = []
seen = set()
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("scheme_details.php"):
        url = urljoin(BASE_URL, href)      # make the full web address
        if url in seen:                    # skip duplicates
            continue
        seen.add(url)
        name = a.get_text(" ", strip=True)
        if name:
            schemes.append({"name": name, "url": url})

with open("schemes_list.json", "w", encoding="utf-8") as f:
    json.dump(schemes, f, ensure_ascii=False, indent=2)

print("===== LIST PAGE =====")
print("Page heading:", [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2"])][:3])
print("Total schemes found:", len(schemes))
for s in schemes[:5]:
    print(" -", s["name"])

print("\nLinks that look like page numbers / next page:")
for a in soup.find_all("a", href=True):
    h = a["href"].lower()
    if "page" in h or "start" in h or "next" in a.get_text().lower():
        print(" ", a.get_text(" ", strip=True)[:30], "->", a["href"])

# ---------- PART 2: download ONE detail page to see what it contains ----------
first = schemes[0]
print("\n===== SAMPLE DETAIL PAGE =====")
print("Scheme:", first["name"])
response = requests.get(first["url"], headers=HEADERS, timeout=30)
print("Status code:", response.status_code)
response.raise_for_status()

with open("detail_sample.html", "w", encoding="utf-8") as f:
    f.write(response.text)

detail = BeautifulSoup(response.text, "html.parser")
print("Headings:", [h.get_text(" ", strip=True)[:60] for h in detail.find_all(["h1", "h2", "h3", "h4"])][:10])
print("Tables:", len(detail.find_all("table")))

lines = detail.get_text("\n", strip=True).split("\n")
# start printing from where the scheme name first appears (skips the menu text)
start = 0
for i, line in enumerate(lines):
    if first["name"][:20].lower() in line.lower():
        start = i
        break
print("\n--- Page text ---")
for line in lines[start:start + 40]:
    print(line[:150])