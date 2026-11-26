# GymLog: Flask uygulamasını gunicorn ile çalıştıran üretim imajı
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Önce bağımlılıklar: kod değişse bile bu katman önbellekten gelir.
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn==23.0.0

COPY gymlog ./gymlog

# Root olmayan kullanıcı; SQLite dosyası /app/instance içinde (volume ile kalıcı).
RUN useradd --create-home --uid 1000 gymlog \
    && mkdir -p /app/instance && chown gymlog:gymlog /app/instance
USER gymlog
VOLUME ["/app/instance"]

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "gymlog:create_app()"]
