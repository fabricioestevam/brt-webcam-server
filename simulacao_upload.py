"""
Script de Simulação de Webcam para Render Free
Envia imagens da pasta 'simulacao_webcam' para o endpoint /upload do servidor.
Compatível com front existente.
"""

import os
import time
import requests

# --------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------
IMAGES_FOLDER = "simulacao_webcam"  # pasta com imagens simulando webcam
UPLOAD_URL = "https://brt-webcam.onrender.com/upload"  # substitua pelo seu app Render
PARADA_ORIGEM = "simulacao"  # nome da parada para simulação
SLEEP_TIME = 1  # segundos entre cada envio (simula frame da webcam)

# --------------------------------------------
# LISTAR IMAGENS
# --------------------------------------------
if not os.path.exists(IMAGES_FOLDER):
    print(f"Pasta '{IMAGES_FOLDER}' não encontrada!")
    exit()

images = sorted([f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith((".jpg", ".png"))])

if not images:
    print(f"Nenhuma imagem encontrada na pasta '{IMAGES_FOLDER}'")
    exit()

# --------------------------------------------
# ENVIAR IMAGENS PARA O SERVIDOR
# --------------------------------------------
for img_file in images:
    img_path = os.path.join(IMAGES_FOLDER, img_file)
    
    if not os.path.isfile(img_path):
        print(f"[PULAR] Arquivo não encontrado: {img_file}")
        continue

    with open(img_path, "rb") as f:
        files = {"imagem": f}
        data = {"parada_origem": PARADA_ORIGEM}

        try:
            response = requests.post(UPLOAD_URL, files=files, data=data, timeout=10)
            if response.status_code == 200:
                print(f"[OK] {img_file} → {response.json()}")
            else:
                print(f"[ERRO] {img_file} → Status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[EXCEÇÃO] Falha ao enviar {img_file}: {e}")

    # Pausa entre imagens para simular frames da webcam
    time.sleep(SLEEP_TIME)

print("Simulação concluída!")
