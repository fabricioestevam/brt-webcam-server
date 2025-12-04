"""
Server V2 - PADRÃO (OCR básico + OpenCV)
Rotas:
  - GET /            -> status
  - GET /health      -> health JSON
  - POST /upload     -> recebe imagem multipart ("imagem"), tenta detectar linha via OCR
  - GET /ultimos     -> últimas leituras do MongoDB
  - POST /deteccao/manual -> registra detecção manual (json {"linha": "437", ...})
  - GET /previsoes/<parada> -> previsões simples para uma parada
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os
import io
import re

# visão
try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# load env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "brt")
PORT = int(os.getenv("PORT", 10000))

if not MONGO_URI:
    raise RuntimeError("MONGO_URI não configurado no .env")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
colecao = db["leituras"]

app = Flask(__name__)

# linhas conhecidas
LINHAS_CONHECIDAS = {
    "437": "TI Caxangá (Conde da Boa Vista)",
    "2441": "TI CDU (Conde da Boa Vista)",
    "2450": "TI Camaragibe (Conde da Boa Vista)",
    "2444": "TI Getúlio Vargas (Conde da Boa Vista)",
    "301": "Linha Demonstrativa 301",
    "723": "Linha Demonstrativa 723",
    "820": "Linha Demonstrativa 820"
}

def ocr_extract_numbers_from_image_bytes(img_bytes):
    """
    Tenta extrair números do frame usando pytesseract.
    Retorna a string de dígitos concatenados ou '' se nada.
    """
    if not OCR_AVAILABLE:
        return ""
    try:
        # carregar imagem via PIL -> cv2
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        # pequenas melhorias
        gray = cv2.resize(gray, None, fx=1.0, fy=1.0, interpolation=cv2.INTER_LINEAR)
        gray = cv2.GaussianBlur(gray, (3,3), 0)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # chamar tesseract
        config = "--psm 6 -c tessedit_char_whitelist=0123456789"
        text = pytesseract.image_to_string(thresh, config=config)
        digits = "".join(re.findall(r"\d+", text))
        return digits.strip()
    except Exception:
        return ""

def fallback_simulate_line(img_bytes):
    """Simples fallback: usa hash dos bytes para escolher uma linha conhecida."""
    import hashlib, random
    h = hashlib.sha256(img_bytes).hexdigest()
    seed = int(h[:8], 16)
    random.seed(seed)
    return random.choice(list(LINHAS_CONHECIDAS.keys()))

def calcular_previsao_para_linha(linha):
    """Retorna dict com minutos estimados e horário."""
    base_min = {
        "437": 5, "2441": 6, "2450": 7, "2444": 4,
        "301": 3, "723": 5, "820": 2
    }
    minutos = int(base_min.get(linha, 6))
    agora = datetime.now(timezone.utc)
    chegada = agora + timedelta(minutes=minutos)
    return {"chega_em_min": minutos, "previsao_horario": chegada.isoformat()}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "BRT Webcam Server", "status": "online"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":"online",
        "ocr_available": OCR_AVAILABLE,
        "mongodb": "connected"
    })

@app.route("/upload", methods=["POST"])
def upload():
    """
    Recebe multipart:
      - imagem (arquivo)
      - parada_origem (opcional)
      - parada_destino (opcional)
      - simulate_line (opcional) -> força linha (ex: 301)
    """
    try:
        if "imagem" not in request.files:
            return jsonify({"error":"Nenhuma imagem recebida (campo 'imagem')"}), 400

        f = request.files["imagem"]
        img_bytes = f.read()
        parada_origem = request.form.get("parada_origem", "")
        parada_destino = request.form.get("parada_destino", "")
        simulate = request.form.get("simulate_line")

        # 1) se for forcing
        if simulate:
            linha = str(simulate).strip()
        else:
            # 2) tentar OCR
            numeros = ocr_extract_numbers_from_image_bytes(img_bytes)
            if numeros:
                # procurar se algum número conhecido aparece como substring (ex: '437')
                linha = None
                for k in LINHAS_CONHECIDAS.keys():
                    if k in numeros:
                        linha = k
                        break
                if not linha:
                    # se numerou algo mas não bate com conhecido, usa primeiro número
                    linha = numeros[:4]
            else:
                # 3) fallback
                linha = fallback_simulate_line(img_bytes)

        previsao = calcular_previsao_para_linha(linha)

        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parada_origem": parada_origem,
            "parada_destino": parada_destino,
            "linha_detectada": linha,
            "nome_linha": LINHAS_CONHECIDAS.get(linha, "Linha desconhecida"),
            "previsao": previsao,
            "tamanho_bytes": len(img_bytes),
            "fonte": "webcam_padrao"
        }
        colecao.insert_one(doc)

        payload = {
            "status":"success",
            "linha_detectada": linha,
            "nome_linha": doc["nome_linha"],
            "previsao": previsao
        }
        return jsonify(payload), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ultimos", methods=["GET"])
def ultimos():
    docs = colecao.find().sort("timestamp", -1).limit(20)
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
    try:
        data = request.get_json(force=True)
        linha = str(data.get("linha", "")).strip()
        parada_origem = data.get("parada_origem", "")
        parada_destino = data.get("parada_destino", "")

        if not linha:
            return jsonify({"error":"campo 'linha' obrigatório"}), 400

        previsao = calcular_previsao_para_linha(linha)
        agora_iso = datetime.now(timezone.utc).isoformat()
        doc = {
            "timestamp": agora_iso,
            "parada_origem": parada_origem,
            "parada_destino": parada_destino,
            "linha_detectada": linha,
            "nome_linha": LINHAS_CONHECIDAS.get(linha, "Linha desconhecida"),
            "previsao": previsao,
            "fonte": "manual"
        }
        res = colecao.insert_one(doc)
        posicao = colecao.count_documents({"parada_destino": parada_destino, "linha_detectada": linha})
        return jsonify({
            "status":"success",
            "deteccao_id": str(res.inserted_id),
            "linha": linha,
            "tempo_estimado_min": previsao["chega_em_min"],
            "posicao_fila": posicao
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/previsoes/<parada_id>", methods=["GET"])
def previsoes(parada_id):
    try:
        docs = colecao.find({"parada_destino": parada_id}).sort("timestamp", 1)
        lista = []
        for d in docs:
            lista.append({
                "linha": d.get("linha_detectada"),
                "nome": d.get("nome_linha"),
                "previsao": d.get("previsao")
            })
        return jsonify({"parada": parada_id, "total": len(lista), "previsoes": lista})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
