from datetime import datetime, timedelta, timezone

# Tempos fictícios por enquanto, você pode depois ajustar
TEMPO_POR_LINHA = {
    "204": 3,
    "431": 5,
    "860": 7,
    "243A": 4
}

def calcular_previsao(linha):
    agora = datetime.now(timezone.utc)
    minutos = TEMPO_POR_LINHA.get(linha, 6)
    chegada = agora + timedelta(minutes=minutos)

    return {
        "linha": linha,
        "chega_em_min": minutos,
        "previsao_horario": chegada.isoformat()
    }
