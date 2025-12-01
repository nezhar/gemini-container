FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["datasette", "logs.db", "--host", "0.0.0.0"]
