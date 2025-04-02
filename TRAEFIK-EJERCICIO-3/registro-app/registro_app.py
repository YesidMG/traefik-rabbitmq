from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# Diccionario para almacenar el conteo de solicitudes por cliente
registro = defaultdict(int)

@app.route("/registro", methods=["GET"])
def obtener_registro():
    # La autenticación es manejada por Traefik
    return jsonify(dict(registro))

@app.route("/registro", methods=["POST"])
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
    app.run(host="0.0.0.0", port=5000)
