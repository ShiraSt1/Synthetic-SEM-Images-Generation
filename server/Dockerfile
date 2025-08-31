# # ---------- Server image ----------
#     FROM python:3.11-slim

#     RUN apt-get update && apt-get install -y --no-install-recommends \
#         libglib2.0-0 \
#         libgssapi-krb5-2 \
#      && rm -rf /var/lib/apt/lists/*
    
#     ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
#     WORKDIR /app
    
#     # מעתיקים את כל הפרויקט (כולל llm/)
#     COPY . /app
    
#     # מתקינים תלות
#     RUN python -m pip install --upgrade pip && \
#         pip install "PyQt5==5.15.*" python-dotenv
    
#     EXPOSE 12345
#     CMD ["python", "/app/server.py"]
    
# ---------- Server image ----------
    FROM python:3.11-slim

    RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgssapi-krb5-2 \
     && rm -rf /var/lib/apt/lists/*
    
    ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
    WORKDIR /app
    
    # מעתיקים את כל קבצי ה-server (כולל llm/)
    COPY . /app
    
    # תלויות פייתון (כולל python-dotenv)
    RUN python -m pip install --upgrade pip && \
        pip install "PyQt5==5.15.*" python-dotenv requests
    
    
    EXPOSE 12345
    CMD ["python", "server.py"]
    