import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.mediomaratondesevilla.es/web-evento/11054-mms26"
STATE_FILE = "estado_sevilla.json"

PUSHOVER_USER = "uhb1bt1dzar4f2ox5am3cy33v4jyvg"
PUSHOVER_TOKEN = "afifdmbic9fqw29dkjxpjkn77do4q9"

def enviar_notificacion(mensaje):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": mensaje,
        },
    )

def obtener_estado():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text().lower()

    if "abiertas" in texto:
        return "abiertas"
    elif "cerradas" in texto:
        return "cerradas"
    else:
        return "desconocido"

def cargar_estado_anterior():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("estado")
    return None

def guardar_estado(estado):
    with open(STATE_FILE, "w") as f:
        json.dump({"estado": estado}, f)

def main():
    estado_actual = obtener_estado()
    estado_anterior = cargar_estado_anterior()

    print("Estado actual:", estado_actual)

    if estado_anterior is None:
        guardar_estado(estado_actual)
        print("Estado inicial guardado.")
        return

    if estado_actual != estado_anterior:
        enviar_notificacion(f"Sevilla 21K cambió a: {estado_actual.upper()}")
        guardar_estado(estado_actual)
        print("Cambio detectado y notificación enviada.")
    else:
        print("Sin cambios.")

if __name__ == "__main__":
    main()