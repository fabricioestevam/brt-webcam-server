"""
Servidor BRT – Recebe imagens da webcam, processa, detecta ônibus
e envia dados para o front.
Compatível 100% com Render Free.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

# Importar utilitários
from utils.detector import extrair_linha_onibus
from utils.previsao import calcular_previsao
from utils.limpeza import limpar_antigos

# Carregar .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# ============================================================
# CONFIGURAR CORS - PERMITIR NETLIFY
# ============================================================
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://frontpi.netlify.app",
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]
col = db["leituras"]


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------
@app.route("/")
def home():
    return {"status": "online", "service": "BRT Webcam Server"}


@app.route("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------
# RECEBER IMAGENS DA WEBCAM
# ------------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "imagem" not in request.files:
        return {"error": "nenhuma imagem recebida"}, 400

    file = request.files["imagem"]
    img_bytes = file.read()
    
    # Pegar parada de origem (onde está a câmera)
    parada_origem = request.form.get("parada_origem", "poeta")

    # --------------------------------------------------------
    # PROCESSAMENTO: DETECTAR LINHA DO ÔNIBUS
    # --------------------------------------------------------
    linha = extrair_linha_onibus(img_bytes, file.filename)

    if linha:
        previsao = calcular_previsao(linha)
    else:
        previsao = None

    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "timestamp_datetime": datetime.now(timezone.utc),
        "linha_detectada": linha,
        "previsao": previsao,
        "parada_origem": parada_origem,  # NOVO: salvar qual parada detectou
        "tamanho_bytes": len(img_bytes)
    }

    col.insert_one(doc)

    return {
        "status": "ok",
        "linha": linha,
        "previsao": previsao,
        "parada_origem": parada_origem
    }


# ------------------------------------------------------------
# LISTAR ÚLTIMAS LEITURAS
# ------------------------------------------------------------
@app.route("/ultimos")
def ultimos():
    docs = col.find().sort("timestamp_datetime", -1).limit(10)

    dados = []
    for d in docs:
        dados.append({
            "timestamp": d["timestamp"],
            "linha_detectada": d["linha_detectada"],
            "previsao": d["previsao"],
            "parada_origem": d.get("parada_origem", "poeta")  # NOVO: retornar parada
        })

    return dados


# ------------------------------------------------------------
# LIMPEZA AUTOMÁTICA (manual)
# ------------------------------------------------------------
@app.route("/limpar")
def limpar():
    limpar_antigos(col)
    return {"status": "limpo"}


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)