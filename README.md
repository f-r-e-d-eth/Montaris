# Montaris

Local dashboard for monitoring and eventually controlling the Aris applications.

## V0.1 mockup

- Dark responsive dashboard
- Cramaris, Memaris, Screenshot Logger, Lumaris, and Backaris
- Simulated start, stop, restart, and status indicators
- Open links for web applications
- Screenshot Logger placeholder for heartbeat, USB, and screenshot timestamp
- **No actual process management yet**

## Run

```bash
cd "$HOME/Montaris"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open http://127.0.0.1:5010

The dashboard binds to localhost only. The controls in V0.1 do not affect running processes.

## Next steps

Migrate individual applications to systemd user services; then add read-only real status monitoring before enabling process-control buttons.

## License

MIT.
