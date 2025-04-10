import os
import pika
import sys
import time
import datetime
import requests
from flask import Flask, jsonify

# Configurar salida sin buffer para que los logs aparezcan inmediatamente
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+

app = Flask(__name__)

SERVICE_ID = os.environ.get('SERVICE_ID', 'unknown')
LOGGER_CENTRAL_URL = "http://logger-central:5000/logs"
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "registro"

# Variable global para la conexión de RabbitMQ
connection = None
channel = None

def conectar_rabbitmq():
    """Establece la conexión con RabbitMQ con reintentos"""
    global connection, channel
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"[{SERVICE_ID}] Intentando conectar a RabbitMQ ({retry_count+1}/{max_retries})...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            
            # Declarar la cola que vamos a usar
            channel.queue_declare(queue=RABBITMQ_QUEUE)
            print(f"[{SERVICE_ID}] Conexión establecida con RabbitMQ")
            return True
            
        except pika.exceptions.AMQPConnectionError:
            retry_count += 1
            print(f"[{SERVICE_ID}] Intento {retry_count}/{max_retries}: No se pudo conectar a RabbitMQ. Reintentando en 5 segundos...")
            sys.stdout.flush()
            time.sleep(5)
        except Exception as e:
            print(f"[{SERVICE_ID}] Error inesperado al conectar con RabbitMQ: {e}")
            sys.stdout.flush()
            retry_count += 1
            time.sleep(5)
    
    print(f"[{SERVICE_ID}] No se pudo conectar a RabbitMQ después de {max_retries} intentos")
    return False

def registrar_servicio():
    """Envía un mensaje a la cola de RabbitMQ para registrar el servicio"""
    try:
        if not (connection and connection.is_open) or not (channel and channel.is_open):
            if not conectar_rabbitmq():
                raise Exception("No hay conexión disponible con RabbitMQ")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje = {
            "service_id": SERVICE_ID,
            "timestamp": timestamp,
            "action": "registro"
        }
        
        # Convertir el mensaje a string para enviarlo
        mensaje_str = str(mensaje)
        
        # Publicar el mensaje en la cola
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=mensaje_str
        )
        
        print(f"[{SERVICE_ID}] Registro enviado a la cola: {mensaje_str}")
        
        # Enviar log al logger-central
        enviar_log(f"Registro enviado a cola RabbitMQ: {mensaje_str}")
        
        return {"status": "message_sent", "queue": RABBITMQ_QUEUE, "time": timestamp}
        
    except Exception as e:
        print(f"[{SERVICE_ID}] Error al enviar mensaje a RabbitMQ: {e}")
        
        # Enviar log de error al logger-central
        enviar_log(f"Error al enviar mensaje a RabbitMQ: {str(e)}")
        
        return {"error": str(e)}

def enviar_log(mensaje):
    """Envía un log al servicio logger-central."""
    try:
        log_data = {
            "service_id": SERVICE_ID,
            "message": mensaje
        }
        response = requests.post(LOGGER_CENTRAL_URL, json=log_data)
        if response.status_code == 200:
            print(f"[{SERVICE_ID}] Log enviado correctamente a logger-central")
        else:
            print(f"[{SERVICE_ID}] Error al enviar log: {response.status_code}")
    except Exception as e:
        print(f"[{SERVICE_ID}] Error al enviar log a logger-central: {e}")

@app.route('/')
def index():
    result = registrar_servicio()
    
    # Enviar log de acceso al endpoint
    enviar_log("Acceso al endpoint principal")
    
    return jsonify({
        "service": SERVICE_ID,
        "registered": result
    })

if __name__ == "__main__":
    # Intentar conectar con RabbitMQ al inicio
    conectar_rabbitmq()
    
    # Registrar periódicamente en segundo plano
    import threading
    def periodic_register():
        while True:
            registrar_servicio()
            time.sleep(10)  # Cada 10 segundos
    
    threading.Thread(target=periodic_register, daemon=True).start()
    
    # Iniciar servidor web
    enviar_log(f"Servicio {SERVICE_ID} iniciado")
    
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print(f"[{SERVICE_ID}] Servicio detenido por el usuario")
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"[{SERVICE_ID}] Error en la aplicación: {e}")
        if connection and connection.is_open:
            connection.close()
