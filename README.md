# Montaris

Local dashboard for monitoring and eventually controlling the Aris applications.

## V0.2 live read-only monitoring

- Dark responsive dashboard
- Cramaris, Memaris, Screenshot Logger, Lumaris, Backaris, Thinkaris, and Valuaris
- Live TCP listening checks for web apps, every 5 seconds
- Screenshot Logger process detection via Linux /proc
- Start, stop, and restart controls shown but disabled
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

The dashboard binds to localhost only. In V0.2 the status indicators use live local checks; controls remain disabled and do not affect running processes. A listening port does not prove application identity or health. For Screenshot Logger, process detection does not prove images are actually being captured.

## Next steps

Migrate individual applications to systemd user services; then add read-only real status monitoring before enabling process-control buttons.

## License

MIT.
