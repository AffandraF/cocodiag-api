FROM python:3.9-slim

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

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Set display port to avoid crash
ENV DISPLAY=:99

# Copy dan install dependencies dari requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8080

CMD ["gunicorn", "-b", ":8080", "main:app"]