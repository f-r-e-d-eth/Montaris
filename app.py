"""Montaris V0.2: read-only local application monitoring."""
from flask import Flask, render_template_string, jsonify, request, abort
from pathlib import Path
import socket
import subprocess
import secrets
import time
from datetime import datetime

CONTROL_TOKEN = secrets.token_urlsafe(32)
UNIT = "montaris-screenshot.service"
CRAMARIS_UNIT = "montaris-cramaris.service"
HEARTBEAT = Path.home() / ".local" / "state" / "montaris" / "screenshot.heartbeat"
HEARTBEAT_MAX_AGE = 11 * 60  # screenshot interval ~5 min; warn after two missed cycles + 1 min

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


def systemd_active(unit=UNIT):
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "--quiet", unit],
            timeout=3, check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def heartbeat_status(running):
    if not running:
        return {"health": "stopped", "heartbeat_age_seconds": None, "last_heartbeat": None}
    try:
        mtime = HEARTBEAT.stat().st_mtime
    except OSError:
        return {"health": "no heartbeat", "heartbeat_age_seconds": None, "last_heartbeat": None}
    age = max(0, round(time.time() - mtime))
    return {"health": "healthy" if age <= HEARTBEAT_MAX_AGE else "stale",
            "heartbeat_age_seconds": age,
            "last_heartbeat": datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="seconds")}


def screenshot_control_state():
    running = screenshot_running()
    managed = systemd_active()
    return {"running": running, "managed": managed,
            "unmanaged": running and not managed}


@app.post("/api/screenshot/<action>")
def control_screenshot(action):
    if action not in ("start", "stop", "restart"):
        abort(404)
    # Bind-only-local is not sufficient protection against cross-site POSTs.
    if request.headers.get("Origin") != "http://127.0.0.1:5010":
        abort(403)
    if request.headers.get("X-Montaris-Token") != CONTROL_TOKEN:
        abort(403)
    if request.mimetype != "application/json":
        abort(415)
    state = screenshot_control_state()
    if state["unmanaged"]:
        return jsonify(error="Logger is running outside systemd. Stop its terminal process first; Montaris will not interfere."), 409
    if action in ("stop", "restart") and not state["managed"]:
        return jsonify(error="Screenshot service is not active."), 409
    try:
        cmd = subprocess.run(
            ["systemctl", "--user", action, UNIT],
            capture_output=True, text=True, timeout=12, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return jsonify(error=str(exc)), 503
    if cmd.returncode != 0:
        return jsonify(error=(cmd.stderr or cmd.stdout).strip()[:500]), 503
    return jsonify(ok=True, state=screenshot_control_state())


@app.post("/api/cramaris/<action>")
def control_cramaris(action):
    if action not in ("start", "stop", "restart"):
        abort(404)
    if request.headers.get("Origin") != "http://127.0.0.1:5010":
        abort(403)
    if request.headers.get("X-Montaris-Token") != CONTROL_TOKEN:
        abort(403)
    if request.mimetype != "application/json":
        abort(415)

    managed = systemd_active(CRAMARIS_UNIT)
    port_open = listening(5000)
    if action == "start":
        if managed:
            return jsonify(error="Cramaris is already managed and running."), 409
        if port_open:
            return jsonify(error="Port 5000 is already occupied. Stop the manually launched Cramaris before starting the service."), 409
    else:
        if not managed:
            return jsonify(error="Cramaris is not running as a Montaris-managed service."), 409
        # If a second process binds 5000 while our service is active, do not claim to control it.
    try:
        cmd = subprocess.run(
            ["systemctl", "--user", action, CRAMARIS_UNIT],
            capture_output=True, text=True, timeout=12, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return jsonify(error=str(exc)), 503
    if cmd.returncode:
        return jsonify(error=(cmd.stderr or cmd.stdout).strip()[:500]), 503
    return jsonify(ok=True)


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
        entry = {"name": name, "description": description,
                 "port": port, "running": running}
        if port is None:
            entry.update(screenshot_control_state())
            entry.update(heartbeat_status(running))
        if name == "Cramaris":
            entry["managed"] = systemd_active(CRAMARIS_UNIT)
            entry["unmanaged"] = running and not entry["managed"]
        result.append(entry)
    return jsonify({"applications": result, "mode": "screenshot control"})


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
<header><div><h1>Montaris</h1><div class="muted">Aris application control center</div></div><span class="pill">● LIVE STATUS · HEARTBEAT</span></header>
<div class="stats">
<div class="stat"><small>Running</small><strong id="running">—</strong></div>
<div class="stat"><small>Stopped</small><strong id="stopped">—</strong></div>
<div class="stat"><small>Monitored</small><strong>7</strong></div>
</div>
<div class="muted" id="message" role="status" aria-live="polite"></div><section class="panel"><h2>Applications</h2><div id="apps"></div></section>
<section class="panel"><h2>Screenshot Logger</h2><div class="stats">
<div><small>Process</small><p id="shotstatus">Running (demo)</p></div>
<div><small>Last heartbeat</small><p id="lastbeat">Waiting for heartbeat</p></div>
<div><small>USB device</small><p>Not checked</p></div>
</div><small>Future health check: use a heartbeat instead of requiring a newly saved image when the screen has not changed.</small></section>
<footer>Montaris V0.5 · Cramaris control · Localhost:5010</footer>
</main>
<script>
let apps = [];
const controlToken = {{ control_token | tojson }};
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
  status.innerHTML='<span class="dot"></span>'+(app.running?(app.port===null?(app.health==="healthy"?"Healthy":app.health==="stale"?"Heartbeat stale":"Heartbeat missing"):"Listening"):"Not detected");
  if(app.port===null && app.running && app.health!=="healthy")row.classList.add("warning");
  const buttons=document.createElement("div");buttons.className="actions";
  for(const label of ["Start","Stop","Restart"]){
   const button=document.createElement("button");button.textContent=label;
   const enabled=app.name==="Screenshot Logger" || app.name==="Cramaris";
   button.disabled=!enabled || (label==="Start" && (app.running || app.managed)) ||
     (label!=="Start" && !app.managed);
   button.title=!enabled?"Controls coming later":app.unmanaged?"Stop the manually launched process first":"Managed by systemd";
   button.onclick=async()=>{
    button.disabled=true;
    const notice=document.getElementById("message");
    notice.textContent="Sending "+label.toLowerCase()+" command…";
    try{
     const response=await fetch("/api/"+(app.name==="Cramaris"?"cramaris":"screenshot")+"/"+label.toLowerCase(),{
       method:"POST",headers:{"Content-Type":"application/json","X-Montaris-Token":controlToken},
       body:"{}"
     });
     const result=await response.json();
     notice.textContent=response.ok?app.name+": "+label+" command completed":(result.error||"Command failed");
    }catch(error){notice.textContent="Request failed: "+error.message}
    await poll();
   };
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
 document.getElementById("lastbeat").textContent=shot&&shot.last_heartbeat?
   new Date(shot.last_heartbeat).toLocaleString()+" ("+shot.heartbeat_age_seconds+" s ago)":
   "No heartbeat received";
}
poll();
setInterval(poll,5000);
</script>
</body></html>
"""

@app.get("/")
def index():
    return render_template_string(PAGE, control_token=CONTROL_TOKEN)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010, debug=False)
