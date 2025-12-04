"""
Server v2 - BRT Recife (detecção SIMULADA)
Recebe imagens via POST /upload (multipart/form-data, campo "imagem")
Retorna uma linha simulada e salva no MongoDB.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os
import hashlib
import random

# Load .env from repo root
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# CONFIG
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "brt")
DEFAULT_PORT = int(os.getenv("PORT", 10000))

if not MONGO_URI:
    raise RuntimeError("MONGO_URI não configurado no .env")

# Conexão Mongo
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
colecao = db["leituras"]

app = Flask(__name__)

# Linhas conhecidas (exemplo)
LINHAS_CONHECIDAS = {
    "437": "TI Caxangá (Conde da Boa Vista)",
    "2441": "TI CDU (Conde da Boa Vista)",
    "2450": "TI Camaragibe (Conde da Boa Vista)",
    "2444": "TI Getúlio Vargas (Conde da Boa Vista)",
    "301": "Linha Demonstrativa 301",
    "723": "Linha Demonstrativa 723",
    "820": "Linha Demonstrativa 820"
}

# Tempos por linha (minutos) usados para simulação
TEMPO_POR_LINHA = {
    "437": 5,
    "2441": 6,
    "2450": 7,
    "2444": 4,
    "301": 3,
    "723": 5,
    "820": 2
}

# Helpers
def gerar_linha_simulada(img_bytes: bytes, override: str | None = None) -> str:
    """
    Gera uma linha simulada:
    - se override fornecido (simulate_line), usa ele se for conhecido
    - senão, usa hash dos bytes para escolher consistentemente uma linha conhecida
    """
    if override:
        override = str(override).strip()
        if override in LINHAS_CONHECIDAS:
            return override
        # aceitar só números no override
        # se não for conhecida, retorna override mesmo assim (para demo)
        return override

    # hash dos bytes para resultado determinístico (a mesma imagem gera mesma linha)
    h = hashlib.sha256(img_bytes).hexdigest()
    seed = int(h[:8], 16)
    random.seed(seed)
    linhas = list(LINHAS_CONHECIDAS.keys())
    escolhido = random.choice(linhas)
    return escolhido

def calcular_previsao(linha: str):
    minutos = int(TEMPO_POR_LINHA.get(linha, 6))
    agora = datetime.now(timezone.utc)
    chegada = agora + timedelta(minutes=minutos)
    return {
        "linha": linha,
        "chega_em_min": minutos,
        "previsao_horario": chegada.isoformat()
    }

# ROUTES
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "BRT Webcam Server (simulado)",
        "simulated": True,
        "endpoints": ["/health", "/upload", "/ultimos", "/deteccao/manual", "/previsoes/<parada>"]
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "simulated": True,
        "mongodb": "connected" if MONGO_URI else "missing",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/upload", methods=["POST"])
def upload():
    """
    Recebe:
      - multipart/form-data:
        - imagem: arquivo .jpg/.png
        - parada_origem (opcional)
        - parada_destino (opcional)
        - simulate_line (opcional) -> força a linha retornada (ex: 301)
    Retorna:
      - status, linha_detectada, nome_linha, previsao
    """
    try:
        if "imagem" not in request.files:
            return jsonify({"error": "Nenhuma imagem (campo 'imagem') recebida"}), 400

        file = request.files["imagem"]
        img_bytes = file.read()

        parada_origem = request.form.get("parada_origem", "")
        parada_destino = request.form.get("parada_destino", "")
        simulate_line = request.form.get("simulate_line")  # opcional override

        # Gerar linha simulada
        linha = gerar_linha_simulada(img_bytes, override=simulate_line)
        previsao = calcular_previsao(linha)

        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parada_origem": parada_origem,
            "parada_destino": parada_destino,
            "linha_detectada": linha,
            "nome_linha": LINHAS_CONHECIDAS.get(linha, "Linha simulada"),
            "previsao": previsao,
            "tamanho_bytes": len(img_bytes),
            "fonte": "webcam_simulada"
        }
        colecao.insert_one(doc)

        response_payload = {
            "status": "success",
            "linha_detectada": linha,
            "nome_linha": doc["nome_linha"],
            "previsao": previsao
        }

        # Para compatibilidade com o cliente: devolver 201 se detectou "algo"
        return jsonify(response_payload), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ultimos", methods=["GET"])
def ultimos():
    docs = colecao.find().sort("timestamp", -1).limit(10)
    out = []
    for d in docs:
        out.append({
            "timestamp": d.get("timestamp"),
            "parada_origem": d.get("parada_origem"),
            "parada_destino": d.get("parada_destino"),
            "linha_detectada": d.get("linha_detectada"),
            "nome_linha": d.get("nome_linha"),
            "previsao": d.get("previsao")
        })
    return jsonify(out)

@app.route("/deteccao/manual", methods=["POST"])
def deteccao_manual():
    """
    Espera JSON:
    {
      "linha": "437",
      "parada_origem": "A",
      "parada_destino": "B"
    }
    Registra manualmente na fila (simulação) e retorna previsão/posição.
    """
    try:
        data = request.get_json(force=True)
        linha = str(data.get("linha", "")).strip()
        parada_origem = data.get("parada_origem", "")
        parada_destino = data.get("parada_destino", "")

        if not linha:
            return jsonify({"error": "Campo 'linha' obrigatório"}), 400

        previsao = calcular_previsao(linha)
        agora_iso = datetime.now(timezone.utc).isoformat()

        deteccao = {
            "timestamp": agora_iso,
            "parada_origem": parada_origem,
            "parada_destino": parada_destino,
            "linha_detectada": linha,
            "nome_linha": LINHAS_CONHECIDAS.get(linha, "Linha simulada"),
            "previsao": previsao,
            "fonte": "manual"
        }
        res = colecao.insert_one(deteccao)

        # calcular posição na fila (simples): contar quantos estão 'em_rota' com mesma parada_destino
        posicao = colecao.count_documents({
            "parada_destino": parada_destino,
            "linha_detectada": linha
        })

        return jsonify({
            "status": "success",
            "deteccao_id": str(res.inserted_id),
            "linha": linha,
            "tempo_estimado_min": previsao["chega_em_min"],
            "posicao_fila": posicao
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/previsoes/<parada_id>", methods=["GET"])
def previsoes(parada_id):
    """
    Retorna previsões para uma parada (simples)
    """
    try:
        docs = colecao.find({"parada_destino": parada_id}).sort("timestamp", 1)
        lista = []
        for d in docs:
            lista.append({
                "linha": d.get("linha_detectada"),
                "nome": d.get("nome_linha"),
                "previsao": d.get("previsao")
            })
        return jsonify({
            "parada": parada_id,
            "total": len(lista),
            "previsoes": lista
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run
if __name__ == "__main__":
    port = int(os.getenv("PORT", DEFAULT_PORT))
    app.run(host="0.0.0.0", port=port)
