import os
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

SERVICE_ID = os.environ.get('SERVICE_ID', 'unknown')
API_REGISTRO_URL = "http://reporte-app:5000/reporte"
LOGGER_CENTRAL_URL = "http://logger-central:5000/logs"

def registrar_servicio():
    headers = {"X-Service-ID": SERVICE_ID}
    try:
        response = requests.post(API_REGISTRO_URL, headers=headers)
        print(f"[{SERVICE_ID}] Registro: {response.json()}")
        
        # Enviar log al logger-central
        enviar_log(f"Registro realizado: {response.json()}")
        
        return response.json()
    except Exception as e:
        print(f"[{SERVICE_ID}] Error: {e}")
        
        # Enviar log de error al logger-central
        enviar_log(f"Error al registrar: {str(e)}")
        
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
    # Registrar periódicamente en segundo plano
    import threading
    def periodic_register():
        while True:
            registrar_servicio()
            time.sleep(10)  # Cada 10 segundos
    
    threading.Thread(target=periodic_register, daemon=True).start()
    
    # Iniciar servidor web
    enviar_log(f"Servicio {SERVICE_ID} iniciado")
    app.run(host="0.0.0.0", port=5000)
