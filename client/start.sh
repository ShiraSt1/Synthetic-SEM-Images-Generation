#!/usr/bin/env bash
set -euo pipefail

# Pick a free DISPLAY (checks :99..:102)
for DISP in 99 100 101 102; do
  if ! xdpyinfo -display :$DISP >/dev/null 2>&1; then
    export DISPLAY=:$DISP
    break
  fi
done

LOCK="/tmp/.X${DISPLAY#:}-lock"

# If a stale lock exists but X isn't actually running, remove it
if [ -e "$LOCK" ] && ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
  rm -f "$LOCK"
fi

# 1) Start a virtual X server
Xvfb "$DISPLAY" -screen 0 1280x800x24 &

# Wait until the X server is ready
for i in $(seq 1 50); do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

# 2) Start a lightweight window manager
fluxbox >/dev/null 2>&1 &

# 3) Qt plugin debug + hints for stability under Xvfb
export QT_DEBUG_PLUGINS=1
export QT_X11_NO_MITSHM=1
export QT_QPA_PLATFORM=xcb

# 4) Launch your GUI app
python /app/client.py &

# 5) Expose the chosen DISPLAY over VNC
x11vnc -display "$DISPLAY" -nopw -forever -shared -rfbport 5900 -listen 0.0.0.0 -quiet &

# 6) noVNC gateway on port 8080 (HTTP). For HTTPS use --cert and --ssl-only.
exec /usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 0.0.0.0:8080

