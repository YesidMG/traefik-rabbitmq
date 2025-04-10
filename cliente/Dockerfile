FROM python:3.9-slim

WORKDIR /app

# Instalar curl para healthchecks
RUN apt-get update && apt-get install -y curl && \
    pip install flask requests pika && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY cliente_app.py .

CMD ["python", "cliente_app.py"]