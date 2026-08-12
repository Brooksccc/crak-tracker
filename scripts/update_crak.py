import json
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Use Selenium to handle JavaScript-rendered content
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)

try:
    driver.get(URL)
    
    # Wait for and dismiss the modal dialog by clicking "I agree"
    wait = WebDriverWait(driver, 10)
    try:
        agree_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I agree')]"))
        )
        agree_button.click()
        print("Dismissed modal dialog")
    except:
        print("No modal dialog found or already dismissed")
    
    # Wait for holdings table to load
    wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
    )
    
    html = driver.page_source
finally:
    driver.quit()

print(f"Downloaded {len(html):,} bytes.")

soup = BeautifulSoup(html, "html.parser")

holdings = []

lines = [
    clean_text(line)
    for line in soup.get_text("\n", strip=True).splitlines()
    if clean_text(line)
]

start = None

# Search for the holdings table headers with flexible matching
for i in range(len(lines) - 3):
    headers = [x.lower() for x in lines[i:i + 4]]
    # Try multiple header variations
    if (headers == [
        "ticker",
        "holding name",
        "% of net assets",
        "market value (us$)",
    ] or headers == [
        "ticker",
        "company name",
        "weight %",
        "value",
    ] or headers == [
        "symbol",
        "company",
        "% weighting",
        "market value",
    ]):
        start = i + 4
        print(f"Found holdings table at line {i}")
        break

if start is None:
    print("DEBUG: First 50 lines of content:")
    for idx, line in enumerate(lines[:50]):
        print(f"  {idx}: {line}")
    raise RuntimeError("Could not find CRAK holdings section on the VanEck page.")

row_pattern = re.compile(
    r"^(?P<ticker>[A-Z0-9][A-Z0-9-]*(?:\s+[A-Z]{2,3})?|-[A-Z]+ [A-Z]+-|--)\s+"
    r"(?P<name>.*?)\s+"
    r"(?P<weight>-?\d+(?:\.\d+)?)\s+"
    r"(?P<value>-?\d[\d,]*)$"
)

i = start

while i < len(lines):
    if lines[i].lower().startswith(
        ("scroll for more information", "these are not recommendations")
    ):
        break

    match = row_pattern.match(lines[i])

    if match:
        holding = {
            "ticker": match.group("ticker"),
            "name": match.group("name"),
            "weight": number_from_text(match.group("weight")),
            "market_value": number_from_text(match.group("value")),
        }
        holdings.append(holding)
        i += 1
        continue

    if i + 3 < len(lines):
        weight = lines[i + 2].replace(",", "")
        value = lines[i + 3].replace(",", "")

        if (
            re.fullmatch(r"-?\d+(?:\.\d+)?", weight)
            and re.fullmatch(r"-?\d+(?:\.\d+)?", value)
        ):
            holding = {
                "ticker": lines[i],
                "name": lines[i + 1],
                "weight": number_from_text(weight),
                "market_value": number_from_text(value),
            }
            holdings.append(holding)
            i += 4
            continue

    i += 1

if not holdings:
    raise RuntimeError("Could not parse CRAK holdings from the VanEck page.")

# Remove duplicate tickers while preserving order.
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
    "holdings": holdings,
}

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Updated CRAK holdings: {len(holdings)} holdings")
print(f"Saved to: {DATA}")
