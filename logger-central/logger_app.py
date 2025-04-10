from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Directorio donde se almacenarán los logs
LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "service_logs.txt")

# Asegurar que el directorio de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/logs', methods=['POST'])
def receive_log():
    """Recibe los logs de los servicios cliente y los guarda en un archivo."""
    data = request.json
    
    if not data:
        return jsonify({"error": "No se han recibido datos"}), 400
    
    # Extraer información del log
    service_id = data.get('service_id', 'desconocido')
    message = data.get('message', 'Sin mensaje')
    
    # Crear entrada de log con timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] - Servicio: {service_id} - Mensaje: {message}\n"
    
    # Escribir en el archivo de log
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        print(f"Log guardado: {log_entry.strip()}")
        return jsonify({"status": "registro recibido"}), 200
    except Exception as e:
        print(f"Error al guardar log: {str(e)}")
        return jsonify({"error": f"Error al guardar log: {str(e)}"}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Muestra los logs almacenados."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = f.readlines()
            return "<pre>" + "".join(logs) + "</pre>"
        else:
            return "No hay logs disponibles", 404
    except Exception as e:
        return f"Error al leer logs: {str(e)}", 500

if __name__ == '__main__':
    print(f"Logger-central iniciado. Los logs se guardarán en {LOG_FILE}")
    app.run(host='0.0.0.0', port=5000)