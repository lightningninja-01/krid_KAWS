# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffering stdout —
# buffered logs would delay showing up in Render/Cloud Run's log stream.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first, separately from app code, so Docker's layer
# cache is only invalidated when requirements.txt actually changes —
# rebuilds during active development stay fast.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user — standard production hardening, costs nothing here.
RUN useradd --create-home appuser
USER appuser

# Both Render and Cloud Run inject a $PORT env var and expect the app to
# bind to it — never hardcode the port. Shell form (not exec form) is
# required here so $PORT gets expanded at container start.
ENV PORT=8000
EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
