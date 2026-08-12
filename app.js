let data={holdings:[],comparison:{added:[],removed:[],changes:[]}};
const $=id=>document.getElementById(id);
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function fmt(n){return Number(n||0).toFixed(2)+"%"}
function render(){
 const c=data.comparison||{added:[],removed:[],changes:[]};
 $("count").textContent=data.holdings?.length||0;$("added").textContent=c.added?.length||0;$("removed").textContent=c.removed?.length||0;$("changed").textContent=c.changes?.length||0;
 $("meta").textContent=data.as_of?`Official holdings as of ${data.as_of}. Last tracker update: ${data.updated_at||"—"}.`:"No snapshot yet. Run the GitHub Action or use Actions → Update CRAK holdings → Run workflow.";
 $("addedList").innerHTML=(c.added||[]).map(x=>`<p><b>${esc(x.ticker)}</b> — ${esc(x.name)}</p>`).join("")||"<p>No additions detected.</p>";
 $("removedList").innerHTML=(c.removed||[]).map(x=>`<p><b>${esc(x.ticker)}</b> — ${esc(x.name)}</p>`).join("")||"<p>No removals detected.</p>";
 $("changes").innerHTML=(c.changes||[]).slice(0,20).map(x=>`<tr><td>${esc(x.ticker)}</td><td>${esc(x.name)}</td><td>${fmt(x.current_weight)}</td><td>${fmt(x.previous_weight)}</td><td>${(x.change>=0?"+":"")+Number(x.change).toFixed(2)} pp</td></tr>`).join("")||"<tr><td colspan='5'>No comparison available yet.</td></tr>";
 showHoldings(data.holdings||[]);
}
function showHoldings(rows){$("holdings").innerHTML=rows.map(x=>`<tr><td>${esc(x.ticker)}</td><td>${esc(x.name)}</td><td>${fmt(x.weight)}</td><td>${esc(x.market_value||"—")}</td></tr>`).join("")}
async function load(){try{const r=await fetch("data/current.json?ts="+Date.now());if(!r.ok)throw 0;data=await r.json()}catch(e){data={holdings:[],comparison:{added:[],removed:[],changes:[]}}}render()}
$("refresh").onclick=load;$("search").oninput=e=>{let q=e.target.value.toLowerCase();showHoldings((data.holdings||[]).filter(x=>(x.ticker+" "+x.name).toLowerCase().includes(q)))};
load();