# ---------- Server image ----------
    FROM python:3.11-slim

    # OS libs needed by Qt (glib + gssapi/kerberos for QtNetwork)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgssapi-krb5-2 \
     && rm -rf /var/lib/apt/lists/*
    
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
    WORKDIR /app
    
    # Python deps
    RUN python -m pip install --upgrade pip && \
        pip install "PyQt5==5.15.*"
    
    # Your TCP server code
    COPY server.py /app/server.py
    
    EXPOSE 12345
    CMD ["python", "/app/server.py"]
    