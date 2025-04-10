from flask import Flask, request, jsonify
from collections import defaultdict
import pika
import sys
import os
import time
import datetime
import threading

# Configurar salida sin buffer para que los logs aparezcan inmediatamente
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+

app = Flask(__name__)

# Diccionario para almacenar el conteo de solicitudes por cliente
registro = defaultdict(int)

# Configuración de RabbitMQ
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "registro"
connection = None
channel = None

def conectar_rabbitmq():
    """Establece la conexión con RabbitMQ con reintentos"""
    global connection, channel
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Intentando conectar a RabbitMQ ({retry_count+1}/{max_retries})...")
            sys.stdout.flush()
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            
            # Declarar la cola que vamos a usar
            channel.queue_declare(queue=RABBITMQ_QUEUE)
            print("Conexión establecida con RabbitMQ")
            sys.stdout.flush()
            return True
            
        except pika.exceptions.AMQPConnectionError:
            retry_count += 1
            print(f"Intento {retry_count}/{max_retries}: No se pudo conectar a RabbitMQ. Reintentando en 5 segundos...")
            sys.stdout.flush()
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado al conectar con RabbitMQ: {e}")
            sys.stdout.flush()
            retry_count += 1
            time.sleep(5)
    
    print("No se pudo conectar a RabbitMQ después de varios intentos")
    sys.stdout.flush()
    return False

def callback(ch, method, properties, body):
    """Procesa los mensajes recibidos de la cola"""
    try:
        mensaje = body.decode()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f" [x] {timestamp} - Mensaje recibido: {mensaje}")
        
        # Extraer el service_id del mensaje
        if "service_id" in mensaje:
            service_id = mensaje.split("'service_id': '")[1].split("'")[0]
        else:
            # Si no se puede extraer, usar un valor por defecto
            service_id = mensaje.split("service_id")[1].split(",")[0].replace("'", "").replace(":", "").replace(" ", "")
        
        # Incrementar el contador para el cliente
        registro[service_id] += 1
        print(f" [x] Registro actualizado para {service_id}: {registro[service_id]}")
        sys.stdout.flush()
    except Exception as e:
        print(f" [!] Error procesando mensaje: {e}")
        sys.stdout.flush()

def iniciar_consumidor():
    """Inicia el consumo de mensajes de la cola"""
    if conectar_rabbitmq():
        try:
            channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=callback,
                auto_ack=True
            )
            print(' [*] Esperando mensajes. Para salir, presiona CTRL+C')
            sys.stdout.flush()
            channel.start_consuming()
        except Exception as e:
            print(f"Error en el consumidor: {e}")
            sys.stdout.flush()

@app.route("/reporte", methods=["GET"])
def obtener_registro():
    # La autenticación es manejada por Traefik
    return str(dict(registro))

@app.route("/reportes", methods=["GET"])
def obtener_registros():
    # La autenticación es manejada por Traefik
    return dict(registro)

@app.route("/reporte", methods=["POST"])
def registrar_cliente():
    # Obtener el identificador del cliente desde el header
    service_id = request.headers.get("X-Service-ID")
    if not service_id:
        return jsonify({"error": "Missing X-Service-ID header"}), 400

    # Incrementar el contador para el cliente
    registro[service_id] += 1
    return jsonify({
        "message": "Registered",
        "service": service_id,
        "count": registro[service_id]
    })

if __name__ == "__main__":
    print("Iniciando servicio de reporte con soporte para RabbitMQ...")
    
    # Iniciar el consumidor de mensajes en un hilo separado
    consumer_thread = threading.Thread(target=iniciar_consumidor, daemon=True)
    consumer_thread.start()
    
    # Iniciar servidor web
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print('Servicio interrumpido por el usuario')
        sys.stdout.flush()
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"Error en la aplicación: {e}")
        sys.stdout.flush()
        if connection and connection.is_open:
            connection.close()
