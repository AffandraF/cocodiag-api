FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    fontconfig \
    locales \
    libnss3 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libappindicator3-1 \
    libxrandr2 \
    libgbm1 \
    xdg-utils \
    --no-install-recommends

RUN apt-get install -y chromium

RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /tmp/chromedriver

# Set display port to avoid crash
ENV DISPLAY=:99

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8080

CMD ["gunicorn", "-b", ":8080", "main:app"]