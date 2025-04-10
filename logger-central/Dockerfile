FROM python:3.9-slim

WORKDIR /app

# Instalar curl para healthchecks
RUN apt-get update && apt-get install -y curl && \
    pip install flask && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY logger_app.py .

RUN mkdir -p /app/logs
VOLUME /app/logs

# Exponer el puerto
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "logger_app.py"]