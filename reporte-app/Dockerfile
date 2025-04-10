FROM python:3.9-slim

WORKDIR /app

COPY reporte_app.py .

# Instalar curl para healthchecks y pika para RabbitMQ
RUN apt-get update && apt-get install -y curl && \
    pip install flask pika && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "reporte_app.py"]