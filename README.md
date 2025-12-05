# 🚌 **Sistema de Monitoramento BRT – Detecção por Webcam (YOLO + OCR)**

### 📡 **PI – Projeto Integrador 2025.2**

**Autor:** Fabrício Estevam
**Front:** Netlify
**Backend:** Render
**Tech:** Node.js, Express, Python YOLO, OCR, API REST, HTML/CSS/JS

---

## 📌 **Descrição do Projeto**

Este projeto realiza monitoramento inteligente de ônibus nas estações do BRT Recife usando:

* **Webcam local**
* **Detecção de ônibus via YOLO**
* **Leitura da placa ou prefixo via OCR**
* **Processamento no servidor Render**
* **Cálculo de previsão real baseada nas distâncias das paradas**
* **Dashboard front-end exibido nas televisões das estações**

O sistema foi projetado para funcionar como um painel informativo em tempo real nas paradas.

---

# 🚀 **Funcionalidades**

### ✔️ Detecção automática de ônibus via câmera

### ✔️ OCR para extrair o número/prefixo

### ✔️ Integração IoT → Servidor Render

### ✔️ Cálculo de previsão baseado na distância real do trajeto

### ✔️ Front em painel estilo BRT

### ✔️ Atualização automática sem recarregar a página

### ✔️ API REST para consumo em múltiplos dispositivos

---

# 🧠 **Arquitetura Geral**

```
WEBCAM → Python Client → YOLO + OCR → API Render (Node.js) → JSON → Front no Netlify
```

### Fluxo detalhado

1. A webcam captura frames.
2. Python envia o frame para o servidor Render.
3. O backend processa com YOLO + OCR.
4. O backend identifica:

   * prefixo do ônibus
   * parada atual associada
   * horário da detecção
5. O backend calcula tempo estimado até a próxima parada usando distâncias reais.
6. O front exibe tudo automaticamente.

---

# 🛠 **Tecnologias Utilizadas**

### **Backend**

* Node.js
* Express
* Python (YOLO + OCR)
* Axios
* Render Cloud Hosting

### **Frontend**

* HTML5
* CSS3
* JavaScript
* Fetch API
* Netlify Hosting

### **IA / Visão Computacional**

* YOLOv8 (Ultralytics)
* PaddleOCR / TesseractOCR

### **Infraestrutura**

* Render (Backend)
* Netlify (Frontend)
* Ambiente local (Webcam)

---

# 📦 **Instalação Local**

## 1️⃣ Clone o projeto

```
git clone https://github.com/fabricioestevam/brt-webcam-server
cd seu-repo
```

---

# 🖥 **Rodando o Backend (Node.js)**

### Instalar dependências:

```
npm install
```

### Rodar local:

```
npm start
```

### Estrutura básica:

```
/server
│── server.js
│── routes/
│── controllers/
│── utils/
│── logs/
└── python/ (YOLO + OCR)
```

A aplicação sobe por padrão em:

```
http://localhost:10000
```

---

# 🖼 **Rodando o Front-End**

O front é **100% estático**.

### Basta abrir:

```
index.html
```

Ou rodar com extensão Live Server do VSCode.

---

# 🔄 **Simulação (modo apresentação)**

A API consegue retornar dados simulados caso a webcam não esteja enviando frames.

Modo de simulação:

* O backend sorteia prefixos de ônibus
* Simula previsão com base nas distâncias reais:

```
Engenho Poeta → Getúlio Vargas → Cordeiro → Madalena → Derby → Boa Vista → Praça do Diário
```

* Distâncias (em linha reta):

  * Poeta → Vargas: 1.2 km
  * Vargas → Cordeiro: 550 m
  * Cordeiro → Madalena: 500 m
  * Madalena → Derby: 1.0 km
  * Derby → Boa Vista: 900 m
  * Boa Vista → Diário: 280 m
    *(todas acumuladas automaticamente pelo backend)*

---

# 📡 **Endpoints da API**

## ✔ `/api/next-bus`

Retorna o último ônibus detectado pela câmera.

**Resposta:**

```json
{
  "parada": "BRT - Cordeiro",
  "onibus": "2430",
  "previsao_minutos": 4,
  "timestamp": "2025-12-05T02:15:22Z"
}
```

---

## ✔ `/api/parada-info`

Retorna informações sobre a parada atual.

**Resposta:**

```json
{
  "parada": "BRT - Madalena",
  "ultima_atualizacao": "2025-12-05T02:16:00Z"
}
```

---

## ✔ `/api/health`

Retorna se o backend está online.

**Resposta:**

```json
{ "status": "online" }
```

---

# 🖼 **Prints do Sistema**

*(Substitua pelas suas imagens depois)*

```
📊 Painel do BRT exibindo ônibus detectado
🚌 Imagem da Webcam com ROI capturado
🧠 Log do YOLO detectando veículo
📡 Terminal mostrando envio para o Render
```

---

# 🔶 **Diagrama da Arquitetura**

```
 ┌──────────────┐
 │    WEBCAM    │
 └──────┬───────┘
        │ frames
        ▼
 ┌──────────────┐
 │  CLIENTE PY  │
 │ YOLO + OCR   │
 └──────┬───────┘
        │ POST /upload
        ▼
 ┌─────────────────────┐
 │   API RENDER (JS)   │
 │ process, salvar,    │
 │ calcular previsão   │
 └──────┬──────────────┘
        │ JSON
        ▼
 ┌─────────────────────┐
 │   FRONT NETLIFY     │
 │ Dashboard em tempo  │
 │        real         │
 └─────────────────────┘
```

---

# 👤 **Créditos**

**Desenvolvimento:**
Ezaú felipe
Fabricio Estevam
Gustavo José
Jenifer Mayara
Maria da Penha

**Tecnologias de IA:**
Ultralytics – YOLOv8
PaddleOCR / Tesseract

**Infraestrutura:**
Render
Netlify

---

# 📄 **Licença**

Projeto acadêmico — uso livre para fins educacionais.
