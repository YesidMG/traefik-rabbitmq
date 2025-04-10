FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
RUN pip install flask

# Copiar el código de la aplicación
COPY logger_app.py .

# Crear el directorio para los logs
RUN mkdir -p /app/logs

# Exponer el puerto
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "logger_app.py"]