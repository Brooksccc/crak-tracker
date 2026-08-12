import json
import os
import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://www.vaneck.com/us/en/investments/oil-refiners-etf-crak/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "holdings.json")

os.makedirs(os.path.dirname(DATA), exist_ok=True)

HEADERS = {
"User-Agent": "Mozilla/5.0 (CRAK-Tracker)"
}

response = requests.get(URL, headers=HEADERS, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

holdings = []

# Find the VanEck holdings table.
for table in soup.find_all("table"):
    rows = table.find_all("tr")
    if not rows:
        continue

    header_cells = rows[0].find_all(["th", "td"])
    headers = [
        cell.get_text(" ", strip=True).lower()
        for cell in header_cells
    ]

    # We are looking specifically for the CRAK holdings table.
    if not any("ticker" in h for h in headers):
        continue

    if not any("holding name" in h for h in headers):
        continue

    ticker_index = next(
        (i for i, h in enumerate(headers) if "ticker" in h),
        None
    )

    name_index = next(
        (i for i, h in enumerate(headers) if "holding name" in h),
        None
    )

    weight_index = next(
        (
            i for i, h in enumerate(headers)
            if "% of net assets" in h
            or "% of net" in h
            or "weight" in h
        ),
        None
    )

    market_value_index = next(
        (
            i for i, h in enumerate(headers)
            if "market value" in h
        ),
        None
    )

    if ticker_index is None or name_index is None:
        continue

    for row in rows[1:]:
        cells = row.find_all(["td", "th"])

        if len(cells) <= max(ticker_index, name_index):
            continue

        ticker = cells[ticker_index].get_text(
            " ", strip=True
        )

        name = cells[name_index].get_text(
            " ", strip=True
        )

        if not ticker or not name:
            continue

        holding = {
            "ticker": ticker,
            "name": name
        }

        if weight_index is not None and len(cells) > weight_index:
            weight_text = cells[weight_index].get_text(
                " ", strip=True
            )

            weight_text = (
                weight_text
                .replace("%", "")
                .replace(",", "")
                .strip()
            )

            try:
                holding["weight"] = float(weight_text)
            except ValueError:
                holding["weight"] = None

        if (
            market_value_index is not None
            and len(cells) > market_value_index
        ):
            market_value_text = cells[
                market_value_index
            ].get_text(" ", strip=True)

            market_value_text = (
                market_value_text
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

            try:
                holding["market_value"] = float(
                    market_value_text
                )
            except ValueError:
                holding["market_value"] = None

        holdings.append(holding)

    if holdings:
        break

if not holdings:
    raise RuntimeError(
        "Could not find CRAK holdings table on the VanEck page."
    )

# Remove duplicate tickers while preserving the first occurrence.
unique = {}

for holding in holdings:
    ticker = holding["ticker"]

    if ticker not in unique:
        unique[ticker] = holding

holdings = list(unique.values())

today = datetime.date.today().isoformat()

result = {
    "ticker": "CRAK",
    "date": today,
    "source": URL,
    "holdings": holdings
}

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(
    f"Updated CRAK holdings: {len(holdings)} holdings"
)
