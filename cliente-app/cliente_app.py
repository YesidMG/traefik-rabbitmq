import os
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

SERVICE_ID = os.environ.get('SERVICE_ID', 'unknown')
API_REGISTRO_URL = "http://registro-app:5000/registro"

def registrar_servicio():
    headers = {"X-Service-ID": SERVICE_ID}
    try:
        response = requests.post(API_REGISTRO_URL, headers=headers)
        print(f"[{SERVICE_ID}] Registro: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"[{SERVICE_ID}] Error: {e}")
        return {"error": str(e)}

@app.route('/')
def index():
    result = registrar_servicio()
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
    app.run(host="0.0.0.0", port=5000)