# ---------- Client (GUI) image with noVNC ----------
    FROM python:3.11-slim

    # System packages for Qt + Xvfb + VNC + noVNC
    RUN apt-get update && apt-get install -y --no-install-recommends \
        # Qt deps
        libglib2.0-0 libgssapi-krb5-2 \
        libx11-6 libx11-xcb1 libxext6 libxrender1 libsm6 libice6 \
        libfontconfig1 libfreetype6 libdbus-1-3 \
        libxcomposite1 libxdamage1 libxfixes3 libxi6 libxtst6 libxrandr2 libxcursor1 libxss1 libxxf86vm1 \
        libgl1 libdrm2 libgbm1 libegl1 \
        libxkbcommon0 libxkbcommon-x11-0 xkb-data \
        libxcb1 libxcb-util1 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
        libxcb-render0 libxcb-shm0 libxcb-xfixes0 libxcb-randr0 libxcb-xinerama0 libxcb-xkb1 libxcb-cursor0 \
        libxau6 libxdmcp6 \
        # virtual display + VNC + noVNC + tools
        xvfb x11vnc fluxbox novnc websockify xauth xfonts-base \
        x11-utils procps \
     && rm -rf /var/lib/apt/lists/*
    
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
    WORKDIR /app
    
    RUN python -m pip install --upgrade pip && \
        pip install "PyQt5==5.15.*"
    
    COPY client.py /app/client.py
    COPY start.sh  /app/start.sh
    RUN chmod +x /app/start.sh
    
    # Qt hints (stability on a virtual X)
    ENV QT_X11_NO_MITSHM=1
    ENV QT_QPA_PLATFORM=xcb
    
    EXPOSE 8080
    CMD ["/app/start.sh"]
    