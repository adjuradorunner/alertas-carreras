import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime, timedelta
import pytz

PUSHOVER_USER = os.environ.get("PUSHOVER_USER")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

STATE_FILE = "estados.json"

# --- FECHAS OBJETIVO ---
VALENCIA_FECHA = datetime(2026, 11, 1)  # Ajustable
BEHOBIA_FECHA = datetime(2026, 4, 15)   # Ajustable

def ahora_espana():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

def es_las_11():
    ahora = ahora_espana()
    return ahora.hour == 11

def enviar_notificacion(mensaje):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": mensaje,
        },
    )

def cargar_estado():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_estado(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def gestionar_fechas():
    estado = cargar_estado()
    ahora = ahora_espana()
    hoy = ahora.date()

    if not es_las_11():
        return

    # --- Valencia ---
    valencia_dia = VALENCIA_FECHA.date()
    valencia_antes = valencia_dia - timedelta(days=1)

    if hoy == valencia_antes and not estado.get("valencia_dia_antes"):
        enviar_notificacion("📅 Mañana abren inscripciones Valencia 2027")
        estado["valencia_dia_antes"] = True

    if hoy == valencia_dia and not estado.get("valencia_mismo_dia"):
        enviar_notificacion("🔥 Hoy abren inscripciones Valencia 2027")
        estado["valencia_mismo_dia"] = True

    # --- Behobia ---
    behobia_dia = BEHOBIA_FECHA.date()

    if hoy == behobia_dia and not estado.get("behobia_mismo_dia"):
        enviar_notificacion("🔥 Hoy abren inscripciones Behobia")
        estado["behobia_mismo_dia"] = True

    guardar_estado(estado)

def main():
    gestionar_fechas()

if __name__ == "__main__":
    main()
