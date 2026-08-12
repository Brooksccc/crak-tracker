import json, re, os, datetime, requests
from bs4 import BeautifulSoup
URL="https://www.vaneck.com/us/en/investments/oil-refiners-etf-crak/"
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data"); HIST=os.path.join(DATA,"history"); os.makedirs(HIST,exist_ok=True)
html=requests.get(URL,timeout=30,headers={"User-Agent":"Mozilla/5.0 CRAK-Tracker"}).text
soup=BeautifulSoup(html,"html.parser")
holdings=[]
for table in soup.find_all("table"):
    headers=[x.get_text(" ",strip=True).lower() for x in table.find_all("th")]
    if "ticker" in headers and any("net assets" in h for h in headers):
        for tr in table.find_all("tr")[1:]:
            cells=[x.get_text(" ",strip=True) for x in tr.find_all("td")]
            if len(cells)<3: continue
            try: weight=float(re.sub(r"[^0-9.\-]","",cells[2]))
            except: continue
            holdings.append({"ticker":cells[0],"name":cells[1],"weight":weight,"market_value":cells[-1] if len(cells)>3 else ""})
        if holdings: break
if not holdings: raise SystemExit("Could not parse holdings from official page.")
old_path=os.path.join(DATA,"current.json")
try: old=json.load(open(old_path))
except: old={"holdings":[]}
old_map={x["ticker"]:x for x in old.get("holdings",[])}
new_map={x["ticker"]:x for x in holdings}
added=[new_map[k] for k in new_map.keys()-old_map.keys()]
removed=[old_map[k] for k in old_map.keys()-new_map.keys()]
changes=[]
for k in new_map.keys() & old_map.keys():
    ch=new_map[k]["weight"]-old_map[k]["weight"]
    if abs(ch)>=0.01:
        changes.append({"ticker":k,"name":new_map[k]["name"],"current_weight":new_map[k]["weight"],"previous_weight":old_map[k]["weight"],"change":round(ch,2)})
changes.sort(key=lambda x:abs(x["change"]),reverse=True)
today=datetime.date.today().isoformat()
payload={"as_of":today,"updated_at":datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z","holdings":sorted(holdings,key=lambda x:x["weight"],reverse=True),"comparison":{"added":added,"removed":removed,"changes":changes}}
json.dump(payload,open(old_path,"w"),indent=2)
json.dump(payload,open(os.path.join(HIST,today+".json"),"w"),indent=2)
print("Updated",len(holdings),"holdings")