# BRT Webcam Server

Servidor Flask para:

- Receber imagens da Webcam ou ESP32
- Detectar ônibus com YOLO
- Armazenar no MongoDB
- Enviar resultados para o Front (`/ultimos`)
- Funcionar no Render.com

## Requisitos

- Python 3.10+
- MongoDB Atlas
- Conta no Render

## Rodar localmente

pip install -r requirements.txt
python server.py

shell
Copiar código

## Endpoint principais

### `/upload` (POST)
Envia imagem da webcam.

### `/ultimos` (GET)
Retorna últimas detecções.

### `/health`
Status do servidor.