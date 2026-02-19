import requests
from bs4 import BeautifulSoup
import json
import os
import re

PUSHOVER_USER = os.environ.get("PUSHOVER_USER")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

STATE_FILE = "estados.json"

CARRERAS = {
    "Granada": {
        "url": "https://mediamaraton.granada.org/",
        "tipo": "estado"
    },
    "Granollers": {
        "url": "https://www.lamitja.cat/la-mitja/",
        "tipo": "estado"
    },
    "Malaga": {
        "url": "https://www.mediamaratonmalaga.com/web-evento/11205-evento",
        "tipo": "estado"
    },
    "Cordoba": {
        "url": "https://mediamaratoncordoba.es/",
        "tipo": "inscripciones_aparecen"
    },
    "Barcelona": {
        "url": "https://www.mitjamarato.barcelona/es/",
        "tipo": "inscripciones_aparecen"
    }
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

def obtener_texto(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text().lower()
    except:
        return ""

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

    for nombre, datos in CARRERAS.items():
        url = datos["url"]
        tipo = datos["tipo"]

        texto = obtener_texto(url)
        estado_anterior = estados_anteriores.get(nombre, {})

        nuevo_estado = {}
        mensaje = None

        # --- Tipo estado clásico ---
        if tipo == "estado":
            estado_actual = detectar_estado(texto)
            ano_actual = detectar_ano(texto)

            nuevo_estado = {
                "estado": estado_actual,
                "ano": ano_actual
            }

            if estado_anterior:
                if estado_actual != estado_anterior.get("estado"):
                    mensaje = f"🔥 {nombre}: ahora las inscripciones están {estado_actual.upper()}"

                elif ano_actual and ano_actual != estado_anterior.get("ano"):
                    mensaje = f"📅 {nombre}: nueva edición detectada {ano_actual}"

        # --- Tipo aparición de inscripciones ---
        elif tipo == "inscripciones_aparecen":
            aparecen = "inscrip" in texto

            nuevo_estado = {
                "inscripciones": aparecen
            }

            if estado_anterior:
                if aparecen and not estado_anterior.get("inscripciones"):
                    mensaje = f"🚀 {nombre}: ¡ha aparecido el apartado de INSCRIPCIONES!"

        print(f"{nombre}: {nuevo_estado}")

        if mensaje:
            enviar_notificacion(mensaje)

        nuevos_estados[nombre] = nuevo_estado

    guardar_estados(nuevos_estados)

if __name__ == "__main__":
    main()
