# utils/detector.py
"""
Detector SIMULADO para ambiente do Render.
Em vez de usar IA, OCR ou modelos pesados, esta versão apenas
simula a detecção da linha do ônibus.

Lógica simples:
- Se o nome do arquivo tiver algum número => retorna esse número como linha
- Se não tiver número => não detecta nada (retorna None)

Isso permite testar TODO O BACKEND sem processamento real.
"""

def extrair_linha_onibus(img_bytes, filename="imagem.jpg"):
    # Tenta extrair número do nome do arquivo
    numeros = []
    for c in filename:
        if c.isdigit():
            numeros.append(c)

    if len(numeros) > 0:
        return "".join(numeros)  # linha simulada, ex: "644"

    return None
