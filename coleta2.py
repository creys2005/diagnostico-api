from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Caminho para armazenar os dados coletados
ARQUIVO_DADOS = "dados_coletados.json"

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
    """Recebe os dados do cliente e armazena no servidor."""
    try:
        client_data = request.get_json()
        client_data["Recebido_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        salvar_dados(client_data)
        return jsonify({"status": "sucesso", "dados_recebidos": client_data}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
