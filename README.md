# Montaris

Local dashboard for monitoring and eventually controlling the Aris applications.

## V0.4 screenshot service and heartbeat

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

## Screenshot capture-loop heartbeat (V0.4)

Montaris reads `~/.local/state/montaris/screenshot.heartbeat` every five seconds.
The heartbeat is **healthy** at age <= 35 seconds, **stale** thereafter, and
**missing** if no heartbeat file exists. A stopped logger is shown as stopped.

To integrate, copy `screenshot_heartbeat.py` next to `screenlog.py`, then add:

```python
from screenshot_heartbeat import beat
```

Call `beat()` once after every **successful screen check** in the logger's main
loop, even when image-change detection decides not to save an image. Do not call
it from a separate independent loop: this would conceal a stuck capture loop.

Restart the screenshot systemd service after editing. The heartbeat file should
remain writable by the login user. No screenshot content is stored in it.

A heartbeat proves only that the capture loop advances; it does not guarantee
the USB device can save images. USB and last-written-image checks are future work.

## Cramaris controls (V0.5)

Montaris can start, stop, and restart **Cramaris** using `montaris-cramaris.service`.
It refuses to start when port 5000 is occupied by an unmanaged instance.

Install the service (does not automatically start it):

```bash
cd /home/rs/Montaris
mkdir -p "$HOME/.config/systemd/user"
cp systemd/montaris-cramaris.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user status montaris-cramaris.service
```

Stop any manually launched Cramaris before using the **Start** button.
Once tested, remove the Cramaris launch commands from your old startup script to prevent duplication. Do not remove the `xdg-open` command if you still want a browser tab opened on login.

Debug failures with `journalctl --user -u montaris-cramaris.service -n 50 --no-pager`.

## V0.6 additional application services

New service unit files exist for Memaris, Lumaris, Backaris, Thinkaris, and Valuaris.
They are **not installed, enabled, or started automatically** by git pull.

Install one at a time using:

```bash
cd /home/rs/Montaris
cp systemd/montaris-memaris.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user status montaris-memaris.service
```

Stop the manually running app before clicking **Start** in Montaris. Check its port
is free first. Services assume home directories named exactly Memaris, Lumaris,
Backaris, Thinkaris and Valuaris, each with `.venv/bin/python3` and the corresponding
`app.py` entry point (Backaris uses `backaris.py`). Check the entry point and
virtual environment path on your machine before installing each service.
Do not remove original startup entries until the corresponding service has been tested.

The controls refuse to start any managed application when its port is occupied.
Stop/Restart operate exclusively on the matching systemd user service.
