Integrantes:
Alex Duvan Hernández Buitrago
Yesid Alejandro Martinez Guerrero

# Sistema de Registro de Servicios

Este proyecto implementa un sistema distribuido de registro de servicios utilizando RabbitMQ como broker de mensajes. Consta de servicios de cliente, sistema de reportes, logger central y un panel de visualización.

## Arquitectura de Mensajería

### Exchange y Colas

- **Cola**: `registro` - Cola principal donde los servicios cliente publican mensajes
- **Exchange**: Se utiliza el exchange predeterminado (cadena vacía `""`) con enrutamiento directo a la cola "registro"

### Formato de Mensaje

```python
{
    "service_id": "<ID del servicio>",  # Identifica el origen (app1, app2, app3)
    "timestamp": "<YYYY-MM-DD HH:MM:SS>",  # Momento de la solicitud
    "action": "registro"  # Tipo de acción realizada
}
```

### Procesamiento de Mensajes

- **Productor**: Los servicios cliente (`cliente-1`, `cliente-2`, `cliente-3`) envían mensajes a RabbitMQ
- **Consumidor**: El servicio `reporte-app` recibe los mensajes y:
  - Almacena conteos en `defaultdict(int)` indexados por `service_id`
  - Incrementa el contador correspondiente cuando recibe un mensaje
  - Expone endpoints para consultar estadísticas (`/reporte` y `/reportes`)

## Implementación de la Comunicación con RabbitMQ

La lógica para la comunicación con RabbitMQ se encuentra en dos archivos principales:

### 1. Cliente (Productor) - `cliente/cliente_app.py`

Este archivo implementa la lógica del servicio que produce y envía mensajes a RabbitMQ:

```python
# Configuración
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "registro"

# Conexión a RabbitMQ
def conectar_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    # ...

# Envío de mensajes - Productor
def registrar_servicio():
    # ...
    mensaje = {
        "service_id": SERVICE_ID,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "registro"
    }

    # Publicar mensaje en la cola
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=str(mensaje)
    )
    # ...
```

### 2. Reporte App (Consumidor) - `reporte-app/reporte_app.py`

Este archivo implementa la lógica del servicio que consume los mensajes de RabbitMQ:

```python
# Almacenamiento
registro = defaultdict(int)

# Configuración
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "registro"

# Procesamiento de mensajes - Consumidor
def callback(ch, method, properties, body):
    mensaje = body.decode()

    # Extraer service_id del mensaje
    service_id = mensaje.split("'service_id': '")[1].split("'")[0]

    # Incrementar contador
    registro[service_id] += 1
    # ...

# Configuración del consumidor
def iniciar_consumidor():
    # ...
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )
    channel.start_consuming()
    # ...

# Ejecución en un hilo independiente
consumer_thread = threading.Thread(target=iniciar_consumidor, daemon=True)
consumer_thread.start()
```

## Endpoints disponibles:

<details>
  <summary> reporte (localhost/reporte) </summary>
credenciales: 
  - usuario: admin
  - contraseña: 123

![reporte](imágenes/reporte.png)

- resultado la información en texto plano:
![reporte-resultado](imágenes/reporte-resultado.png)
</details>

<details>
  <summary> clientes (localhost/cliente/uno) (localhost/cliente/dos) (localhost/cliente/tres) </summary>

![clieteuno](imágenes/uno.png)
![clientedos](imágenes/dos.png)
![clientetres](imágenes/tres.png)

</details>

<details>
  <summary> panel (localhost/panel) </summary>

![panel](imágenes/panel.png)

</details>

<details>
  <summary> logs (localhost/logs) </summary>

![logs](imágenes/logs.png)

</details>

## Componentes del Sistema

- **Clientes**: Servicios que generan registros de actividad
- **RabbitMQ**: Broker de mensajes que facilita la comunicación entre servicios
- **Reporte App**: Procesa y almacena estadísticas de uso
- **Logger Central**: Almacena logs históricos de todos los servicios
- **Panel**: Interfaz gráfica para visualizar información del sistema

## Iniciar el Sistema

```bash
docker-compose up
```
