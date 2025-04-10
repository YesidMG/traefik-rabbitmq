FROM python:3.9-slim

WORKDIR /app

RUN pip install flask requests pika

COPY cliente_app.py .

CMD ["python", "cliente_app.py"]