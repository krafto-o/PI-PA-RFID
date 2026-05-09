import random
import threading
import time
from datetime import datetime, timedelta

import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "rfid_registro"
DB_PORT = 3306

USUARIOS_TEST = [
    {"uid": "C3E45F95", "nombre": "Usuario1"},
    {"uid": "B3887A95", "nombre": "Usuario2"},
    {"uid": "63CA4095", "nombre": "Usuario3"},
]
UID_DENEGADO = "FF11AA22"


def generar_linea():
    if random.random() < 0.7:
        u = random.choice(USUARIOS_TEST)
        return f"ACCESO:{u['uid']}:{u['nombre']}"
    else:
        return f"DENEGADO:{UID_DENEGADO}"


def parsear_linea(linea):
    linea = linea.strip()
    if linea.startswith("ACCESO:"):
        partes = linea.split(":")
        if len(partes) == 3:
            return {"uuid": partes[1], "nombre": partes[2], "acceso": True}
    elif linea.startswith("DENEGADO:"):
        partes = linea.split(":")
        if len(partes) >= 2:
            return {"uuid": partes[1], "nombre": "Desconocido", "acceso": False}
    return None


def insertar_registro(uuid, nombre, acceso_concedido, fecha=None):
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
        )
        cursor = conexion.cursor()
        query = "INSERT INTO accesos (uuid, nombre, acceso_concedido, fecha) VALUES (%s, %s, %s, %s)"
        if fecha is None:
            fecha = datetime.now()
        fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (uuid, nombre, acceso_concedido, fecha_str))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as e:
        print(f"Error MySQL: {e}")
        return False


def poblar_db_prueba():
    ahora = datetime.now()
    registros = []

    for i in range(5):
        t = ahora - timedelta(minutes=random.randint(1, 55))
        u = random.choice(USUARIOS_TEST)
        registros.append(
            {"uuid": u["uid"], "nombre": u["nombre"], "acceso": True, "fecha": t}
        )

    for i in range(3):
        t = ahora - timedelta(hours=random.randint(1, 11))
        u = random.choice(USUARIOS_TEST)
        registros.append(
            {"uuid": u["uid"], "nombre": u["nombre"], "acceso": True, "fecha": t}
        )
        t2 = ahora - timedelta(hours=random.randint(1, 11))
        registros.append(
            {
                "uuid": UID_DENEGADO,
                "nombre": "Desconocido",
                "acceso": False,
                "fecha": t2,
            }
        )

    for i in range(4):
        t = ahora - timedelta(days=random.randint(1, 6), hours=random.randint(0, 23))
        u = random.choice(USUARIOS_TEST)
        registros.append(
            {"uuid": u["uid"], "nombre": u["nombre"], "acceso": True, "fecha": t}
        )
        t2 = ahora - timedelta(days=random.randint(1, 6), hours=random.randint(0, 23))
        registros.append(
            {
                "uuid": UID_DENEGADO,
                "nombre": "Desconocido",
                "acceso": False,
                "fecha": t2,
            }
        )

    for i in range(3):
        t = ahora - timedelta(weeks=random.randint(2, 3), days=random.randint(0, 6))
        u = random.choice(USUARIOS_TEST)
        registros.append(
            {"uuid": u["uid"], "nombre": u["nombre"], "acceso": True, "fecha": t}
        )

    for r in registros:
        insertar_registro(r["uuid"], r["nombre"], r["acceso"], r["fecha"])

    return len(registros)


def start_simulator(callback, stop_event=None):
    def _run():
        while True:
            if stop_event and stop_event.is_set():
                break
            time.sleep(3)
            linea = generar_linea()
            callback(linea)

    hilo = threading.Thread(target=_run, daemon=True)
    hilo.start()
    return hilo
