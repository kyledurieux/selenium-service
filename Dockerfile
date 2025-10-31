FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# System deps Chrome needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates curl unzip fontconfig \
    libnss3 libasound2 libxss1 libatk-bridge2.0-0 libatk1.0-0 \
    libdrm2 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 xvfb fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome (stable)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt .
RUN pip install -r requirements.txt
COPY app/ .

EXPOSE 8080
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]
