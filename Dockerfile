FROM python:3.10.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY migrations ./migrations
COPY alembic.ini .env.example requirements.txt src/ ./

RUN pip3 install --no-cache-dir -U -r requirements.txt