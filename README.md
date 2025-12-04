🚌 BRT Webcam Server — Sistema de Detecção de Ônibus em Tempo Real

Servidor responsável por:

✔ Receber imagens da webcam (enviadas por um Raspberry, PC ou ESP32-CAM)
✔ Processar a imagem usando OCR
✔ Detectar a linha do ônibus visível na foto
✔ Calcular previsão de chegada à próxima parada
✔ Salvar dados no MongoDB
✔ Servir informações para o frontend do painel das paradas

Totalmente compatível com Render Free Tier, sem uso de modelos pesados como YOLO ou PyTorch.

📁 Estrutura do Projeto
brt-webcam-server/
│
├── server.py
├── requirements.txt
├── README.md
├── .env.example
│
└── utils/
    ├── detector.py
    ├── previsao.py
    └── limpeza.py

🚀 Funcionalidades
✔ Recebimento de imagens

O endpoint /upload recebe imagens enviadas pela webcam via método POST.

✔ OCR para identificar ônibus

A detecção é feita com Tesseract OCR, que funciona no Render Free.

✔ Cálculo de previsão

Cada linha possui um tempo estimado para chegar à próxima parada.

✔ Armazenamento no MongoDB

Cada registro de leitura fica salvo em leituras.

✔ Comunicação com o front

O frontend acessa /ultimos para obter os últimos dados detectados.

🌐 Endpoints Disponíveis
GET /

Retorna status do servidor.

GET /health

Health check para o Render.

POST /upload

Recebe a imagem da webcam.

Campos:

imagem: arquivo JPEG enviado pelo front/webcam.

Resposta:

{
  "status": "ok",
  "linha": "204",
  "previsao": {
    "linha": "204",
    "chega_em_min": 3,
    "previsao_horario": "2025-01-22T12:01:22Z"
  }
}

GET /ultimos

Retorna as últimas 10 detecções.

[
  {
    "timestamp": "2025-01-22T11:59:10Z",
    "linha_detectada": "431",
    "previsao": {...}
  }
]

GET /limpar

Remove registros antigos (mais de 1h).

🛠️ Instalação Local
1. Clone o repositório
git clone https://github.com/fabricioestevam/brt-webcam-server
cd brt-webcam-server

2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate    # Linux
venv\Scripts\activate       # Windows

3. Instale as dependências
pip install -r requirements.txt

4. Configure o .env

Copie:

cp .env.example .env


Edite:

MONGO_URI=sua-url-do-mongodb
DB_NAME=brt
PORT=5000
TESSERACT_CMD=/usr/bin/tesseract

5. Inicie o servidor
python server.py

☁️ Deploy no Render (Free Tier)
1. Crie um novo Web Service

Ambiente: Python 3

Build Command:

pip install -r requirements.txt


Start Command:

python server.py

2. Configure variáveis de ambiente no Render

Copie tudo do .env.

3. Deploy automático

O Render buscará sempre a última versão do GitHub.

🎥 Como enviar imagens da webcam

Seu script Python da webcam deve enviar assim:

requests.post(
    "https://SEU-SERVIDOR.onrender.com/upload",
    files={"imagem": ("frame.jpg", img_bytes, "image/jpeg")}
)


O servidor processa, detecta e salva.

📡 Como o front obtém os dados

Basta consumir o endpoint:

GET https://SEU-SERVIDOR.onrender.com/ultimos


Exemplo em JavaScript:

const resposta = await fetch("/ultimos");
const dados = await resposta.json();
console.log(dados);

🤖 Processamento de Imagem — Como funciona

O OCR extrai o texto visível no letreiro do ônibus:

Conversão da imagem para escala de cinza

Aplicação de blur para reduzir ruído

Threshold adaptativo

Extração de texto com Tesseract

Regex para capturar linhas como:

204

243A

860

431

Você pode melhorar o OCR colocando a câmera focada na frente do ônibus.

✨ Futuras melhorias

Histórico completo da linha

Previsão baseada em velocidade real

Reconhecimento de placa

Indicação de lotação por análise de pixels

Ajuste automático para iluminação da rua

📞 Suporte

Qualquer dúvida, erros ou logs do Render → só me chamar.
Posso até monitorar o deploy junto com você.

### TESTANDO A DETECÇÃO SIMULADA (APRESENTAÇÃO)

1. Execute o cliente webcam localmente (seu script) apontando `SERVIDOR_URL` para:
   https://SEU-SERVIDOR.onrender.com

2. O cliente envia a imagem para POST /upload (campo 'imagem').
   - Opcional: enviar campo form `simulate_line=301` para forçar linha 301.

3. O servidor retorna JSON com `linha_detectada` e `previsao`.
   Use `/ultimos` para ver as últimas leituras.
