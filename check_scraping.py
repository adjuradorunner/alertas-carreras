import requests
from bs4 import BeautifulSoup
import json
import os
import re

PUSHOVER_USER = os.environ.get("PUSHOVER_USER")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

STATE_FILE = "estados_scraping.json"

CARRERAS = {
    "Granada": "https://mediamaraton.granada.org/",
    "Granollers": "https://www.lamitja.cat/la-mitja/",
    "Malaga": "https://www.mediamaratonmalaga.com/web-evento/11205-evento",
    "Cordoba": "https://mediamaratoncordoba.es/",
    "Barcelona": "https://www.mitjamarato.barcelona/es/"
}

def enviar_notificacion(mensaje):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "message": mensaje,
        },
    )

def obtener_texto(url, nombre, estado_salud):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            estado_salud[nombre] = estado_salud.get(nombre, 0) + 1
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        texto = soup.get_text().lower()

        if len(texto) < 500:
            estado_salud[nombre] = estado_salud.get(nombre, 0) + 1
            return None

        # Si llega aquí, la web funciona
        if estado_salud.get(nombre, 0) >= 3:
            enviar_notificacion(f"✅ {nombre} se ha recuperado correctamente")

        estado_salud[nombre] = 0
        return texto

    except:
        estado_salud[nombre] = estado_salud.get(nombre, 0) + 1
        return None

def detectar_estado(texto):
    if "abiertas" in texto:
        return "abiertas"
    elif "agotadas" in texto or "cerradas" in texto or "tancades" in texto:
        return "cerradas"
    else:
        return "desconocido"

def detectar_ano(texto):
    anos = re.findall(r"20\d{2}", texto)
    return max(anos) if anos else None

def cargar_estados():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_estados(estados):
    with open(STATE_FILE, "w") as f:
        json.dump(estados, f)

def main():
    estados_anteriores = cargar_estados()
    nuevos_estados = {}

    # Recuperamos estado de salud anterior
    estado_salud = estados_anteriores.get("salud", {})

    for nombre, url in CARRERAS.items():
        texto = obtener_texto(url, nombre, estado_salud)

        # Si la web falla
        if texto is None:
            if estado_salud.get(nombre, 0) == 3:
                enviar_notificacion(f"⚠️ {nombre} lleva 3 ciclos fallando")
            continue

        estado_actual = detectar_estado(texto)
        ano_actual = detectar_ano(texto)

        estado_anterior = estados_anteriores.get(nombre)

        print(f"{nombre}: {estado_actual} ({ano_actual})")

        if estado_anterior:
            if estado_actual != estado_anterior.get("estado"):
                enviar_notificacion(f"🔥 {nombre}: ahora está {estado_actual.upper()}")

            elif ano_actual and ano_actual != estado_anterior.get("ano"):
                enviar_notificacion(f"📅 {nombre}: nueva edición detectada {ano_actual}")

        nuevos_estados[nombre] = {
            "estado": estado_actual,
            "ano": ano_actual
        }

    # Guardamos estado de salud también
    nuevos_estados["salud"] = estado_salud

    guardar_estados(nuevos_estados)

if __name__ == "__main__":
    main()
