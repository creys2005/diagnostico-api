from flask import Flask, render_template, jsonify
import socket
import psutil
import platform

app = Flask(__name__)

@app.route("/")
def index():
    """Servir a página HTML principal."""
    return render_template("index.html")

def get_system_info():
    """Coleta informações do computador."""
    system_info = {
        "Nome da Máquina": socket.gethostname(),
        "IP Local": socket.gethostbyname(socket.gethostname()),
        "Processador": platform.processor(),
        "Memória RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Uso de RAM (%)": psutil.virtual_memory().percent,
        "Uso de CPU (%)": psutil.cpu_percent(interval=1)
    }
    return system_info

@app.route('/coletar', methods=['GET'])
def coletar_dados():
    """Endpoint para coletar os dados e retornar como JSON."""
    data = get_system_info()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
