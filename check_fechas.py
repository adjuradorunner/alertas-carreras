import os
import json
import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

PUSHOVER_USER = os.environ.get("PUSHOVER_USER")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

STATE_FILE = "estado_fechas.json"

def ahora_espana():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

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

# -----------------------------
# BEHOBIA
# -----------------------------

def gestionar_behobia(estado):
    url = "https://www.behobia-sansebastian.com/es/inscripciones/calendario"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text().lower()

    # Extraer año
    match_ano = re.search(r"calendario\s+(20\d{2})", texto)
    if not match_ano:
        return estado

    ano = int(match_ano.group(1))

    # Extraer fechas tipo 23 mar
    fechas = re.findall(r"(\d{1,2})\s+(mar|abr|may)", texto)

    meses = {
        "mar": 3,
        "abr": 4,
        "may": 5
    }

    ahora = ahora_espana()

    for dia, mes_txt in fechas:
        mes = meses.get(mes_txt)
        fecha_evento = datetime(ano, mes, int(dia), 11, 0)

        clave = f"behobia_{fecha_evento.date()}"

        if ahora.date() == fecha_evento.date() and ahora.hour == 11:
            if not estado.get(clave):
                enviar_notificacion(f"🔥 Hoy abre bloque Behobia ({dia} {mes_txt} {ano})")
                estado[clave] = True

    return estado

# -----------------------------
# VALENCIA
# -----------------------------

def gestionar_valencia(estado):
    url = "https://www.valenciaciudaddelrunning.com/medio/info-inscripciones-2026/"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text().lower()

    # Extraer todas las fechas tipo "17 noviembre"
    fechas = re.findall(r"(\d{1,2})\s+nov", texto)

    ano = ahora_espana().year + 1  # asumimos siguiente edición

    ahora = ahora_espana()

    for dia in fechas:
        fecha_evento = datetime(ano, 11, int(dia), 11, 0)

        clave = f"valencia_{fecha_evento.date()}"

        if ahora.date() == fecha_evento.date() and ahora.hour == 11:
            if not estado.get(clave):
                enviar_notificacion(f"🔥 Hoy evento clave Valencia ({dia} Nov {ano})")
                estado[clave] = True

    return estado

# -----------------------------
# MAIN
# -----------------------------

def main():
    estado = cargar_estado()
    ahora = ahora_espana()

    # Solo actuar a las 11:00
    if ahora.hour != 11:
        return

    estado = gestionar_behobia(estado)
    estado = gestionar_valencia(estado)

    guardar_estado(estado)

if __name__ == "__main__":
    main()
