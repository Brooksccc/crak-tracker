import json
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://www.vaneck.com/us/en/investments/oil-refiners-etf-crak/"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "holdings.json")

os.makedirs(os.path.dirname(DATA), exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def number_from_text(value):
    if value is None:
        return None

    text = clean_text(value)
    text = text.replace("$", "")
    text = text.replace(",", "")
    text = text.replace("%", "")

    try:
        return float(text)
    except ValueError:
        return None


print("Downloading CRAK holdings from VanEck...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30,
)

response.raise_for_status()

print(f"Downloaded {len(response.text):,} bytes.")

soup = BeautifulSoup(response.text, "html.parser")

holdings = []

for table in soup.find_all("table"):
    headers = [
        clean_text(x.get_text(" ", strip=True)).lower()
        for x in table.find_all(["th", "td"])
    ]

    if not headers or "ticker" not in headers or "holding name" not in headers:
        continue

    ticker_index = headers.index("ticker")
    name_index = headers.index("holding name")
    weight_index = next((i for i, h in enumerate(headers) if "% of net assets" in h), None)
    market_value_index = next((i for i, h in enumerate(headers) if "market value" in h), None)

    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["td", "th"])

        if len(cells) <= max(ticker_index, name_index):
            continue

        ticker = clean_text(cells[ticker_index].get_text(" ", strip=True))
        name = clean_text(cells[name_index].get_text(" ", strip=True))

        if not ticker or not name:
            continue

        holding = {
            "ticker": ticker,
            "name": name,
        }

        if weight_index is not None and len(cells) > weight_index:
            holding["weight"] = number_from_text(
                cells[weight_index].get_text(" ", strip=True)
            )

        if market_value_index is not None and len(cells) > market_value_index:
            holding["market_value"] = number_from_text(
                cells[market_value_index].get_text(" ", strip=True)
            )

        holdings.append(holding)

    if holdings:
        break

if not holdings:
    raise RuntimeError("Could not find CRAK holdings table on the VanEck page.")

# Remove duplicate tickers while preserving order.
unique = {}

for holding in holdings:
    ticker = holding["ticker"]

    if ticker not in unique:
        unique[ticker] = holding

holdings = list(unique.values())


with open(DATA, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Saved {len(holdings)} CRAK holdings to {DATA}")

today = datetime.date.today().isoformat()

result = {
    "ticker": "CRAK",
    "date": today,
    "source": URL,
    "holdings": holdings,
}


with open(DATA, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)


print(
    f"Updated CRAK holdings: {len(holdings)} holdings"
)

print(f"Saved to: {DATA}")
