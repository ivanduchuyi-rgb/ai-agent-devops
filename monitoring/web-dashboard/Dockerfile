FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 9001
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["gunicorn", "--bind", "0.0.0.0:9001", "--workers", "4", "--worker-class", "gthread", "--threads", "2", "--timeout", "60", "--max-requests", "1000", "--max-requests-jitter", "50", "app:app"]