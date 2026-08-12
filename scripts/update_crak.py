import json
import os
import datetime
import requests

URL = "https://www.vaneck.com/us/en/investments/oil-refiners-etf-crak/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "holdings.json")

os.makedirs(os.path.dirname(DATA), exist_ok=True)

headers = {
"User-Agent": "Mozilla/5.0 (CRAK-Tracker)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

html = response.text

# VanEck may change its page structure, so use several patterns
# to find CRAK holdings information.
patterns = [
r'"ticker"\s*:\s*"([^"]+)"[^}]*"name"\s*:\s*"([^"]+)"',
r'"symbol"\s*:\s*"([^"]+)"[^}]*"name"\s*:\s*"([^"]+)"',
r'"ticker"\s*:\s*"([^"]+)"[^}]*"holdingName"\s*:\s*"([^"]+)"',
]

holdings = []

for pattern in patterns:
    import re

    matches = re.findall(pattern, html, re.IGNORECASE)

    for ticker, name in matches:
        ticker = ticker.strip()
        name = name.strip()

        if ticker and name:
            holdings.append({
                "ticker": ticker,
                "name": name
            })

    if holdings:
        break

# Remove duplicates
unique = {}

for holding in holdings:
    unique[holding["ticker"]] = holding

holdings = list(unique.values())

if not holdings:
    raise RuntimeError(
        "Could not find CRAK holdings data on the VanEck page."
    )

# Load existing data
try:
    with open(DATA, "r", encoding="utf-8") as f:
        old_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    old_data = {}

today = datetime.date.today().isoformat()

result = {
    "ticker": "CRAK",
    "date": today,
    "source": URL,
    "holdings": holdings
}

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Updated CRAK holdings: {len(holdings)} holdings")
