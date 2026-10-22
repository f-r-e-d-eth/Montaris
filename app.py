"""Montaris V0.2: read-only local application monitoring."""
from flask import Flask, render_template_string, jsonify
from pathlib import Path
import socket

app = Flask(__name__)

SERVICES = [
    ("Cramaris", "Encrypted editor", 5000),
    ("Memaris", "Personal logbook", 5001),
    ("Screenshot Logger", "Background capture", None),
    ("Lumaris", "Screenshot viewer", 5002),
    ("Backaris", "Backup management", 5003),
    ("Thinkaris", "Local AI apps", 5004),
    ("Valuaris", "Value investing", 5005),
]


def listening(port):
    """Check whether any service accepts TCP connections on localhost:port."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def screenshot_running():
    """Find a Python process running screenlog.py from ~/screenshot.

    This avoids matching an unrelated process whose command mentions screenlog.py.
    Linux /proc is used without any third-party dependencies.
    """
    expected = Path.home() / "screenshot"
    proc = Path("/proc")
    if not proc.is_dir():
        return False
    for item in proc.iterdir():
        if not item.name.isdigit():
            continue
        try:
            args = (item / "cmdline").read_bytes().split(b"\0")
            if not any(Path(a.decode("utf-8", "replace")).name == "screenlog.py" for a in args[1:] if a):
                continue
            cwd = (item / "cwd").resolve()
            if cwd == expected.resolve():
                return True
        except (OSError, PermissionError):
            continue
    return False


@app.get("/api/status")
def status():
    result = []
    for name, description, port in SERVICES:
        running = screenshot_running() if port is None else listening(port)
        result.append({"name": name, "description": description,
                       "port": port, "running": running})
    return jsonify({"applications": result, "mode": "read-only"})


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
<header><div><h1>Montaris</h1><div class="muted">Aris application control center</div></div><span class="pill">● LIVE STATUS · READ ONLY</span></header>
<div class="stats">
<div class="stat"><small>Running</small><strong id="running">—</strong></div>
<div class="stat"><small>Stopped</small><strong id="stopped">—</strong></div>
<div class="stat"><small>Monitored</small><strong>7</strong></div>
</div>
<section class="panel"><h2>Applications</h2><div id="apps"></div></section>
<section class="panel"><h2>Screenshot Logger</h2><div class="stats">
<div><small>Process</small><p id="shotstatus">Running (demo)</p></div>
<div><small>Last screenshot</small><p>Not yet monitored</p></div>
<div><small>USB device</small><p>Not checked</p></div>
</div><small>Future health check: use a heartbeat instead of requiring a newly saved image when the screen has not changed.</small></section>
<footer>Montaris V0.2 · Live status, simulated controls · Localhost:5010</footer>
</main>
<script>
let apps = [];
async function poll(){
 try{
  const response=await fetch("/api/status",{cache:"no-store"});
  if(!response.ok)throw new Error("HTTP "+response.status);
  const data=await response.json();
  apps=data.applications;
  render();
 }catch(err){
  document.getElementById("apps").textContent="Status unavailable: "+err.message;
  document.getElementById("running").textContent="—";
  document.getElementById("stopped").textContent="—";
 }
}
function render(){
 const root=document.getElementById("apps");root.replaceChildren();
 for(const app of apps){
  const row=document.createElement("div");row.className="app"+(app.running?"":" stopped");
  const name=document.createElement("div");name.innerHTML='<div class="appname"></div><div class="detail"></div>';
  name.querySelector(".appname").textContent=app.name;
  name.querySelector(".detail").textContent=app.description;
  const port=document.createElement("div");port.className="detailcol muted";port.textContent=app.port===null?"Background process":"Port "+app.port+" · TCP check";
  const status=document.createElement("div");status.className="status";
  status.innerHTML='<span class="dot"></span>'+(app.running?(app.port===null?"Process found":"Listening"):"Not detected");
  const buttons=document.createElement("div");buttons.className="actions";
  for(const label of ["Start","Stop","Restart"]){
   const button=document.createElement("button");button.textContent=label;
   button.disabled=true;button.title="Coming later — controls are not enabled";
   buttons.append(button);
  }
  if(app.port!==null){
   const open=document.createElement("a");open.className="btn";open.href="http://127.0.0.1:"+app.port+"/";
   open.target="_blank";open.rel="noopener noreferrer";open.textContent="Open";buttons.append(open);
  }
  row.append(name,port,status,buttons);root.append(row);
 }
 document.getElementById("running").textContent=apps.filter(a=>a.running).length;
 document.getElementById("stopped").textContent=apps.filter(a=>!a.running).length;
 const shot=apps.find(a=>a.name==="Screenshot Logger");
 document.getElementById("shotstatus").textContent=shot?(shot.running?"Process found":"Not detected"):"Unknown";
}
poll();
setInterval(poll,5000);
</script>
</body></html>
"""

@app.get("/")
def index():
    return render_template_string(PAGE)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010, debug=False)
