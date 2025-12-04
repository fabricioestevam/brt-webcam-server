import easyocr

reader = easyocr.Reader(["en"])

def read_text(frame):
    result = reader.readtext(frame)
    texto = []
    for (_, text, _) in result:
        texto.append(text)
    return " ".join(texto)
