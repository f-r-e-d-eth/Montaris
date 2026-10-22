"""Montaris V0.1: mock dashboard. No process control is implemented."""
from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Montaris</title>
<style>
:root {color-scheme:dark;--bg:#111418;--panel:#1b2026;--border:#343b45;--text:#f0f2f5;--muted:#a0aab7;--green:#40c99b;--red:#ee7777;--amber:#f2bb65}
*{box-sizing:border-box}body{background:var(--bg);color:var(--text);font:15px system-ui,sans-serif;margin:0}
main{max-width:1000px;margin:36px auto;padding:0 20px}header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:20px}
h1{margin:0;font-size:29px}h2{font-size:17px;margin:0 0 14px}.muted,small{color:var(--muted)}
.pill{border:1px solid var(--border);padding:7px 11px;border-radius:30px;font-size:12px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0}
.panel,.stat{border:1px solid var(--border);border-radius:13px;background:var(--panel)}
.stat{padding:17px}.stat strong{display:block;font-size:27px;margin-top:6px}
.panel{padding:18px;margin:14px 0}.app{display:grid;grid-template-columns:minmax(150px,1.5fr) minmax(100px,1fr) auto auto;align-items:center;gap:12px;padding:15px 0;border-top:1px solid var(--border)}
.app:first-of-type{border-top:0}.appname{font-weight:650}.detail{font-size:12px;color:var(--muted);margin-top:4px}
.status{font-size:13px;white-space:nowrap}.dot{display:inline-block;width:9px;height:9px;border-radius:100%;margin-right:7px;background:var(--green)}
.stopped .dot{background:var(--red)}.warning .dot{background:var(--amber)}
.actions{display:flex;gap:7px}button,a.btn{background:#2d3540;color:var(--text);border:1px solid #46505c;border-radius:8px;padding:8px 11px;cursor:pointer;font:inherit;font-size:13px;text-decoration:none}
button:hover,a.btn:hover{background:#3c4654}.primary{background:#315b50;border-color:#497d6c}.danger{background:#59353b}
footer{color:var(--muted);font-size:12px;text-align:center;padding:18px}
@media(max-width:650px){.stats{grid-template-columns:repeat(3,1fr)}.app{grid-template-columns:1fr auto}.app .detailcol{display:none}.actions{grid-column:1/-1}.actions button{flex:1}header{align-items:flex-start}}
</style>
</head>
<body>
<main>
<header><div><h1>Montaris</h1><div class="muted">Aris application control center</div></div><span class="pill">● MOCKUP MODE</span></header>
<div class="stats">
<div class="stat"><small>Running</small><strong id="running">4</strong></div>
<div class="stat"><small>Stopped</small><strong id="stopped">1</strong></div>
<div class="stat"><small>Monitored</small><strong>5</strong></div>
</div>
<section class="panel"><h2>Applications</h2><div id="apps"></div></section>
<section class="panel"><h2>Screenshot Logger</h2><div class="stats">
<div><small>Process</small><p id="shotstatus">Running (demo)</p></div>
<div><small>Last screenshot</small><p>Not connected</p></div>
<div><small>USB device</small><p>Not checked</p></div>
</div><small>Future health check: use a heartbeat instead of requiring a newly saved image when the screen has not changed.</small></section>
<footer>Montaris V0.1 · Mock statuses and controls only · Localhost:5010</footer>
</main>
<script>
const apps=[
{name:"Cramaris",description:"Encrypted editor",port:5000,running:true},
{name:"Memaris",description:"Personal logbook",port:5001,running:true},
{name:"Screenshot Logger",description:"Background capture",port:null,running:true},
{name:"Lumaris",description:"Screenshot viewer",port:5002,running:true},
{name:"Backaris",description:"Backup management",port:5003,running:false}
];
function render(){
const root=document.getElementById("apps");root.replaceChildren();
for(const [index,app] of apps.entries()){
const row=document.createElement("div");row.className="app"+(app.running?"":" stopped");
const name=document.createElement("div");name.innerHTML='<div class="appname"></div><div class="detail"></div>';
name.querySelector(".appname").textContent=app.name;
name.querySelector(".detail").textContent=app.description;
const port=document.createElement("div");port.className="detailcol muted";port.textContent=app.port===null?"Background service":"Port "+app.port;
const status=document.createElement("div");status.className="status";status.innerHTML='<span class="dot"></span>'+(app.running?"Running":"Stopped");
const buttons=document.createElement("div");buttons.className="actions";
const toggle=document.createElement("button");toggle.textContent=app.running?"Stop":"Start";
toggle.className=app.running?"danger":"primary";toggle.onclick=()=>{app.running=!app.running;render()};
const restart=document.createElement("button");restart.textContent="Restart";restart.onclick=()=>{app.running=true;render()};
buttons.append(toggle,restart);
if(app.port!==null){const open=document.createElement("a");open.className="btn";open.href="http://127.0.0.1:"+app.port;open.target="_blank";open.rel="noopener noreferrer";open.textContent="Open";buttons.append(open)}
row.append(name,port,status,buttons);root.append(row);
}
document.getElementById("running").textContent=apps.filter(a=>a.running).length;
document.getElementById("stopped").textContent=apps.filter(a=>!a.running).length;
document.getElementById("shotstatus").textContent=apps[2].running?"Running (demo)":"Stopped (demo)";
}
render();
</script>
</body></html>
"""

@app.get("/")
def index():
    return render_template_string(PAGE)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010, debug=False)
