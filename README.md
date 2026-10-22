# Montaris

Local dashboard for monitoring and eventually controlling the Aris applications.

## V0.3 screenshot service control

- Dark responsive dashboard
- Cramaris, Memaris, Screenshot Logger, Lumaris, Backaris, Thinkaris, and Valuaris
- Live TCP listening checks for web apps, every 5 seconds
- Screenshot Logger process detection via Linux /proc
- Start, stop, and restart controls shown but disabled
- Open links for web applications
- Screenshot Logger placeholder for heartbeat, USB, and screenshot timestamp
- Screenshot Logger Start / Stop / Restart through systemd user service
- Other application controls remain disabled

## Run

```bash
cd "$HOME/Montaris"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open http://127.0.0.1:5010

The dashboard binds to localhost only. In V0.3 the Screenshot Logger can be started/stopped/restarted through systemd; all other app controls remain disabled. A listening port does not prove application identity or health. For Screenshot Logger, process detection does not prove images are actually being captured.

## Next steps

Migrate individual applications to systemd user services; then add read-only real status monitoring before enabling process-control buttons.

## License

MIT.

## Install screenshot user service

**First stop any manually running `screenlog.py`** using Ctrl+C in its terminal.
Then install the unit as your normal login user (no sudo):

```bash
cd /home/rs/Montaris
mkdir -p "$HOME/.config/systemd/user"
cp systemd/montaris-screenshot.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user status montaris-screenshot.service
```

The service is initially stopped. In Montaris, press **Start** for Screenshot Logger.
The app refuses to control an unmanaged running copy.

To view errors:
```bash
journalctl --user -u montaris-screenshot.service -n 50 --no-pager
```

To optionally start it automatically when your user session begins:
```bash
systemctl --user enable montaris-screenshot.service
```

Do not keep a duplicate launch of `screenlog.py` in the old startup script after switching to the service.

The HTTP control endpoint accepts only localhost-origin JSON requests with a per-process token.
The UI remains bound to `127.0.0.1`; do not expose it publicly without authentication.
