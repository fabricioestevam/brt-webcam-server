"""
Servidor Flask para detectar Ônibus com YOLO + OCR + MongoDB
Compatível com Render e com envio de Webcam / ESP32 / Python
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from ultralytics import YOLO
import numpy as np
import base64
import cv2
import os

# ================================
# 🔐 CARREGAR VARIÁVEIS .ENV
# ================================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "brt_db")

if not MONGO_URI:
    raise RuntimeError("❌ ERRO: MONGO_URI não encontrada no .env")

# ================================
# 🔧 MONGO
# ================================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["deteccoes"]

# ================================
# 🤖 CARREGAR MODELO YOLO
# ================================
model = YOLO("yolov8n.pt")  # pequeno mas rápido

# ================================
# 🌐 FLASK
# ================================
app = Flask(__name__)
CORS(app)

# ================================
#   HEALTH CHECK
# ================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# ================================
#   ENDPOINT /upload
# ================================
@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        if "imagem" not in request.files:
            return jsonify({"error": "Nenhuma imagem recebida"}), 400

        file = request.files["imagem"]
        img_bytes = file.read()

        # Converter para matriz (OpenCV)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Imagem inválida"}), 400

        # ===========================
        #  🚌 RODAR YOLO
        # ===========================
        results = model(frame, stream=False)
        bus_detected = False

        for r in results:
            for box in r.boxes:
                cls = int(box.cls)
                label = model.names[cls]

                if label.lower() in ["bus", "truck", "coach"]:
                    bus_detected = True

        # ===========================
        #  SALVAR NO BANCO
        # ===========================
        doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bus_detected": bus_detected,
            "raw_image_base64": base64.b64encode(img_bytes).decode("utf-8")
        }

        collection.insert_one(doc)

        return jsonify({
            "status": "ok",
            "bus_detected": bus_detected
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
#   /ultimos — usado no front
# ================================
@app.route("/ultimos", methods=["GET"])
def ultimos():
    docs = collection.find().sort("timestamp", -1).limit(20)

    saida = []
    for d in docs:
        saida.append({
            "timestamp": d["timestamp"],
            "bus_detected": d["bus_detected"]
        })

    return jsonify(saida)


# ================================
#   MAIN LOCAL
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
