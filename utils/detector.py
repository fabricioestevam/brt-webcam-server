import cv2
import pytesseract
import numpy as np
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extrair_linha_onibus(imagem_bytes):
    """Extrai o texto do ônibus usando OCR (padrão Render Free)."""
    
    try:
        img = Image.open(io.BytesIO(imagem_bytes)).convert("RGB")
        img_np = np.array(img)

        # Preprocessamento simples
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, 41, 15
        )

        texto = pytesseract.image_to_string(
            thresh,
            config="--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        # Filtrar apenas linhas (ex: 204, 431, 860, 243A)
        texto = texto.strip().replace("\n", "").replace(" ", "")

        if texto == "":
            return None

        # Pega apenas números/letras seguidos
        import re
        match = re.search(r"[0-9]{2,4}[A-Z]?", texto)

        if match:
            return match.group(0)

        return None

    except Exception as e:
        print("Erro no OCR:", e)
        return None
