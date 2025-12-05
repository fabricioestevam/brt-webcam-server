from datetime import datetime, timedelta, timezone

# Distâncias entre as paradas (em quilômetros)
DISTANCIAS_KM = [
    ("BRT - Engenho Poeta",      "BRT - Getúlio Vargas", 1.2),
    ("BRT - Getúlio Vargas",     "BRT - Cordeiro",        0.55),
    ("BRT - Cordeiro",           "BRT - Madalena",        0.50),
    ("BRT - Madalena",           "BRT - Derby",           1.0),
    ("BRT - Derby",              "BRT - Boa Vista",       0.9),
    ("BRT - Boa Vista",          "BRT - Praça do Diário", 0.28),
]

# Tempo médio real de um BRT urbano (22 km/h → ~0.37 km/min)
VELOCIDADE_KM_POR_MIN = 22 / 60  # = 0.366

# Se quiser ajustar depois, só altera essa linha ↑
# Quanto menor esse valor, maior o tempo estimado

def calcular_previsao(linha_detectada):
    """
    A webcam envia apenas a *linha* do ônibus.
    Aqui calculamos a previsão realística baseado na distância acumulada.
    """

    agora = datetime.now(timezone.utc)

    #  TOTAL DA LINHA (considerando todas as paradas adiante)
    distancia_total = sum([d[2] for d in DISTANCIAS_KM])

    # Transformar distância em minutos
    minutos_estimados = distancia_total / VELOCIDADE_KM_POR_MIN

    # Arredonda para cima para evitar "0 minutos"
    minutos_estimados = int(minutos_estimados + 1)

    horario_previsto = agora + timedelta(minutes=minutos_estimados)

    return {
        "linha": linha_detectada,
        "chega_em_min": minutos_estimados,
        "previsao_horario": horario_previsto.isoformat(),
    }
