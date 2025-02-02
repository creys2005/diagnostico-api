from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import speedtest
import subprocess

app = Flask(__name__)

# Caminho para armazenar os dados coletados
ARQUIVO_DADOS = "dados_coletados.json"

def medir_velocidade():
    """Mede a velocidade de download, upload e latência."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / (1024 * 1024), 2)  # Convertendo para Mbps
        upload_speed = round(st.upload() / (1024 * 1024), 2)  # Convertendo para Mbps
        ping = round(st.results.ping, 2)

        return {
            "Velocidade de Download (Mbps)": download_speed,
            "Velocidade de Upload (Mbps)": upload_speed,
            "Latência (ms)": ping
        }
    except Exception as e:
        return {"Erro": f"Falha ao medir velocidade: {str(e)}"}

def executar_tracert(destino):
    """Executa um tracert para o destino fornecido."""
    try:
        resultado = subprocess.run(["tracert", "-d", destino], capture_output=True, text=True, timeout=10)
        return resultado.stdout.split("\n")
    except Exception as e:
        return [f"Erro ao executar tracert: {str(e)}"]

def salvar_dados(data):
    """Salva os dados recebidos no servidor."""
    try:
        with open(ARQUIVO_DADOS, "a", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write("\n")
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")

@app.route("/")
def index():
    """Servir a página HTML principal."""
    return render_template("index.html")

@app.route('/coletar', methods=['POST'])
def coletar_dados():
    """Recebe os dados do cliente, mede a velocidade, executa o tracert e armazena no servidor."""
    try:
        client_data = request.get_json()
        client_data.pop("Linguagem", None)
        client_data.pop("Memória RAM (GB)", None)
        client_data.pop("Navegador", None)
        client_data.pop("Núcleos da CPU", None)
        client_data.pop("Plataforma", None)
        client_data.pop("Recebido_em", None)
        client_data.pop("Resolução de Tela", None)
        client_data.pop("Velocidade de Download (Mbps)", None)
        client_data["Diagnóstico de Rede"] = medir_velocidade()
        client_data["Tracert para nfb.redeis.com.br"] = executar_tracert("nfb.redeis.com.br")
        client_data["Browser"] = request.user_agent.browser
        client_data["Hostname"] = request.remote_addr
        client_data["Recebido_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        salvar_dados(client_data)
        return jsonify({"status": "sucesso", "dados_recebidos": client_data}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
