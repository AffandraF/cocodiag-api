FROM python:3.11-slim

ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

EXPOSE 8080

CMD ["gunicorn", "-b", ":8080", "main:app"]