from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    """Servir a página HTML principal."""
    return render_template("index.html")

@app.route('/coletar', methods=['POST'])
def coletar_dados():
    """Recebe as informações enviadas pelo navegador do cliente e retorna a resposta."""
    try:
        client_data = request.get_json()
        return jsonify({"status": "sucesso", "dados_recebidos": client_data}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
