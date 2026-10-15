import json
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (student learning project)"}

# The labels that appear on every scheme page, and the name we give each one
LABELS = {
    "Associated Scheme": "associated_scheme",
    "Sponsered By": "sponsored_by",
    "Funding Pattern": "funding_pattern",
    "Beneficiaries": "beneficiaries",
    "Types of Benefits": "benefit_type",
    "Eligibility criteria": "eligibility_header",
    "Income": "income",
    "Age From": "age_from",
    "Age To": "age_to",
    "Community": "community",
    "How To avail": "how_to_avail_header",
    "Validity of the Scheme": "validity",
    "Introduced On": "introduced_on",
    "Description": "description",
    "Scheme Type": "scheme_type",
    "Uploaded File": "uploaded_file",
}
EMPTY_VALUES = {"-", "na", "n/a", "nil", ""}


def clean(text):
    """Remove \\r, line breaks and extra spaces."""
    return " ".join(text.split())


def find_label(line):
    """If this line is a label (like 'Funding Pattern:'), return its key name."""
    text = clean(line)
    # this label was being missed before, so we match it by its first words
    if text.lower().startswith("the application is to be submitted"):
        return "submit_to"
    if not text.endswith(":"):
        return None
    text = text.rstrip(":").strip().lower()
    for label, key in LABELS.items():
        if text == label.lower():
            return key
    return None


def parse_detail(html):
    """Turn one scheme page into a dictionary of label -> value."""
    soup = BeautifulSoup(html, "html.parser")
    lines = soup.get_text("\n", strip=True).split("\n")

    data = {}
    current = None
    for line in lines:
        key = find_label(line)
        if key:
            current = key
            data[current] = []
        elif clean(line).startswith("Content owned and Maintained by"):
            break
        elif current:
            data[current].append(clean(line))

    result = {}
    for key, parts in data.items():
        joiner = "; " if key == "submit_to" else " "
        value = joiner.join(p for p in parts if p).strip()
        if value.lower() in EMPTY_VALUES:
            value = ""
        result[key] = value
    # these two are just section titles, not real data
    result.pop("eligibility_header", None)
    result.pop("how_to_avail_header", None)
    return result


with open("schemes_list.json", "r", encoding="utf-8") as f:
    schemes = json.load(f)

all_data = []
for i, scheme in enumerate(schemes, start=1):
    try:
        response = requests.get(scheme["url"], headers=HEADERS, timeout=30)
        response.raise_for_status()
        details = parse_detail(response.text)
        record = {"name": scheme["name"], "url": scheme["url"], **details}
        all_data.append(record)
        filled = sum(1 for v in details.values() if v)
        print(f"[{i}/{len(schemes)}] {scheme['name'][:50]} -> {filled} fields filled")
    except Exception as error:
        print(f"[{i}/{len(schemes)}] FAILED: {scheme['name'][:50]} ({error})")
    time.sleep(1)  # wait 1 second between pages, to be polite to the website

with open("schemes_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("\nSaved", len(all_data), "schemes to schemes_data.json")
print("Schemes with 'submit_to' filled:  ", sum(1 for r in all_data if r.get("submit_to")))
print("Schemes with 'description' filled:", sum(1 for r in all_data if r.get("description")))
print("Schemes with 'validity' filled:   ", sum(1 for r in all_data if r.get("validity")))