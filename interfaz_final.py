import threading
from datetime import datetime

import mysql.connector
import serial
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

PUERTO = "/dev/ttyUSB0"
BAUDIOS = 9600
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "rfid_registro"
DB_PORT = 3306

# Tiempo en milisegundos que la puerta permanece abierta y la GUI muestra el acceso
TIEMPO_PUERTA = 5000

is_connected = False

arduino = serial.Serial()
arduino.port = PUERTO
arduino.baudrate = BAUDIOS
arduino.timeout = 0.5
arduino.write_timeout = 0.5

# Globals for consultation window
ventana_consulta = None
tree = None
lblCount = None
lblCargando = None
rango_var = None
entryBusqueda = None
timer_standby = None


def insertar_acceso(uuid, nombre, acceso_concedido):
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
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valores = (uuid, nombre, acceso_concedido, fecha)
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except mysql.connector.Error as e:
        print(f"Error MySQL: {e}")
        return False


def ejecutar_query(rango, busqueda=""):
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
        )
        cursor = conexion.cursor()

        if rango == "hora":
            where = "WHERE fecha >= NOW() - INTERVAL 1 HOUR"
        elif rango == "dia":
            where = "WHERE DATE(fecha) = CURDATE()"
        elif rango == "semana":
            where = "WHERE YEARWEEK(fecha, 1) = YEARWEEK(CURDATE(), 1)"
        elif rango == "mes":
            where = "WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE())"
        else:
            where = ""

        query = f"SELECT uuid, nombre, acceso_concedido, fecha FROM accesos {where}"

        if busqueda:
            busqueda = busqueda.strip()
            query += " AND (nombre LIKE %s OR uuid LIKE %s)"
            query += " ORDER BY fecha DESC"
            cursor.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
        else:
            query += " ORDER BY fecha DESC"
            cursor.execute(query)

        rows = cursor.fetchall()
        cursor.close()
        conexion.close()
        return rows
    except mysql.connector.Error as e:
        print(f"Error MySQL: {e}")
        return []


def poblar_treeview(rows):
    global tree, lblCount, lblCargando
    if tree is None:
        return

    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        uuid, nombre, acceso, fecha = row
        acceso_str = "ACCESO" if acceso else "DENEGADO"
        nombre_str = nombre if nombre else "---"
        fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S") if isinstance(fecha, datetime) else str(fecha)
        tree.insert("", "end", values=(uuid, nombre_str, acceso_str, fecha_str))

    lblCount.config(text=f"Total: {len(rows)} registros")
    if lblCargando:
        lblCargando.config(text="")


def cargar_registros_async(rango, busqueda=""):
    global lblCargando
    if lblCargando:
        lblCargando.config(text="Cargando...")

    def trabajo():
        rows = ejecutar_query(rango, busqueda)
        ventana_principal.after(0, poblar_treeview, rows)

    threading.Thread(target=trabajo, daemon=True).start()


def on_rango_change():
    global rango_var
    rango = rango_var.get()
    busqueda = ""
    if entryBusqueda:
        busqueda = entryBusqueda.get()
    cargar_registros_async(rango, busqueda)


def on_buscar():
    global rango_var
    rango = rango_var.get()
    busqueda = entryBusqueda.get() if entryBusqueda else ""
    cargar_registros_async(rango, busqueda)


def abrir_ventana_consulta():
    global ventana_consulta, tree, lblCount, lblCargando, rango_var, entryBusqueda

    if ventana_consulta is not None and ventana_consulta.winfo_exists():
        ventana_consulta.lift()
        return

    ventana_consulta = tk.Toplevel(ventana_principal)
    ventana_consulta.title("Consultar Registros")
    ventana_consulta.geometry("650x500")
    ventana_consulta.configure(bg="#2c3e50")

    rango_var = tk.StringVar(value="hora")

    frame_rangos = tk.Frame(ventana_consulta, bg="#2c3e50")
    frame_rangos.pack(pady=10)

    tk.Radiobutton(frame_rangos, text="Última hora", variable=rango_var, value="hora", command=on_rango_change, bg="#2c3e50", fg="white", selectcolor="#34495e").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_rangos, text="Hoy", variable=rango_var, value="dia", command=on_rango_change, bg="#2c3e50", fg="white", selectcolor="#34495e").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_rangos, text="Semana", variable=rango_var, value="semana", command=on_rango_change, bg="#2c3e50", fg="white", selectcolor="#34495e").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_rangos, text="Mes", variable=rango_var, value="mes", command=on_rango_change, bg="#2c3e50", fg="white", selectcolor="#34495e").pack(side=tk.LEFT, padx=10)

    frame_busqueda = tk.Frame(ventana_consulta, bg="#2c3e50")
    frame_busqueda.pack(pady=5)

    entryBusqueda = tk.Entry(frame_busqueda, width=40, bg="#ecf0f1", fg="#2c3e50")
    entryBusqueda.pack(side=tk.LEFT, padx=5)
    entryBusqueda.bind("<Return>", lambda e: on_buscar())

    tk.Button(frame_busqueda, text="Buscar", command=on_buscar, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_busqueda, text="Limpiar", command=lambda: [entryBusqueda.delete(0, tk.END), on_rango_change()], bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)

    lblCargando = tk.Label(ventana_consulta, text="", fg="#f39c12", bg="#2c3e50", font=("Arial", 10))
    lblCargando.pack(pady=5)

    columns = ("uuid", "nombre", "acceso", "fecha")
    tree = ttk.Treeview(ventana_consulta, columns=columns, show="headings", height=15)

    tree.heading("uuid", text="UUID")
    tree.heading("nombre", text="Nombre")
    tree.heading("acceso", text="Acceso")
    tree.heading("fecha", text="Fecha")

    tree.column("uuid", width=120, anchor=tk.CENTER)
    tree.column("nombre", width=100, anchor=tk.CENTER)
    tree.column("acceso", width=80, anchor=tk.CENTER)
    tree.column("fecha", width=150, anchor=tk.CENTER)

    tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    lblCount = tk.Label(ventana_consulta, text="Total: 0 registros", fg="#ecf0f1", bg="#2c3e50", font=("Arial", 10))
    lblCount.pack(pady=5)

    frame_cerrar = tk.Frame(ventana_consulta, bg="#2c3e50")
    frame_cerrar.pack(pady=10)

    tk.Button(frame_cerrar, text="Cerrar", command=ventana_consulta.destroy, bg="#c0392b", fg="white", width=12).pack()

    ventana_consulta.protocol("WM_DELETE_WINDOW", lambda: [ventana_consulta.destroy()])

    cargar_registros_async("hora", "")


def procesar_linea(linea):
    linea = linea.strip()
    if linea == "READY":
        ventana_principal.after(0, lambda: lbConexion.config(text="Conectado", fg="lime green"))
        return

    if linea.startswith("ACCESO:"):
        partes = linea.split(":")
        if len(partes) == 3:
            uuid = partes[1]
            nombre = partes[2]
            insertar_acceso(uuid, nombre, True)
            ventana_principal.after(0, lambda u=uuid, n=nombre: actualizar_gui(u, n, True))

    elif linea.startswith("DENEGADO:"):
        partes = linea.split(":")
        if len(partes) >= 2:
            uuid = partes[1]
            insertar_acceso(uuid, "Desconocido", False)
            ventana_principal.after(0, lambda u=uuid: actualizar_gui(u, "", False))

    elif linea == "CERRADO":
        pass


def actualizar_gui(uuid, nombre, acceso):
    global timer_standby

    if timer_standby is not None:
        ventana_principal.after_cancel(timer_standby)
        timer_standby = None

    if acceso:
        lbEstado.config(text=f"ACCESO: {nombre}", fg="green")
        lbUUID.config(text=f"UUID: {uuid}")
        timer_standby = ventana_principal.after(TIEMPO_PUERTA, volver_standby)
    else:
        lbEstado.config(text=f"DENEGADO", fg="red")
        lbUUID.config(text=f"UUID: {uuid}")

    hora = datetime.now().strftime("%H:%M:%S")
    if acceso:
        texto = f"[{hora}] ACCESO: {nombre} ({uuid})"
    else:
        texto = f"[{hora}] DENEGADO: {uuid}"
    lbLog.config(text=texto)


def volver_standby():
    global timer_standby
    timer_standby = None
    lbEstado.config(text="Esperando...", fg="gray")
    lbUUID.config(text="UUID: ---")


def DataReceivedHandler():
    global is_connected
    while is_connected:
        try:
            if arduino.is_open and arduino.in_waiting > 0:
                linea = arduino.readline().decode("utf-8", errors="ignore").strip()
                if linea:
                    procesar_linea(linea)
        except serial.SerialException:
            ventana_principal.after(0, lambda: messagebox.showerror("Error", "Conexion serial perdida"))
            break
        except Exception as e:
            print(f"Error lectura: {e}")


def btnConectar_Click():
    global is_connected
    try:
        if not arduino.is_open:
            arduino.open()

        btnConectar.config(state=tk.DISABLED)
        btnDesconectar.config(state=tk.NORMAL)
        lbConexion.config(text="Conectando...", fg="orange")

        if not is_connected:
            is_connected = True
            hilo = threading.Thread(target=DataReceivedHandler, daemon=True)
            hilo.start()

    except serial.SerialException:
        messagebox.showerror("Error", f"No se pudo abrir {PUERTO}")
        lbConexion.config(text="Desconectado", fg="red")


def btnDesconectar_Click():
    global is_connected
    is_connected = False

    btnConectar.config(state=tk.NORMAL)
    btnDesconectar.config(state=tk.DISABLED)

    if arduino.is_open:
        arduino.close()

    lbConexion.config(text="Desconectado", fg="red")
    lbEstado.config(text="Esperando...", fg="gray")
    lbUUID.config(text="UUID: ---")


def on_closing():
    global is_connected
    is_connected = False

    if arduino.is_open:
        arduino.close()

    if ventana_consulta is not None and ventana_consulta.winfo_exists():
        ventana_consulta.destroy()

    ventana_principal.quit()
    ventana_principal.destroy()


ventana_principal = tk.Tk()
ventana_principal.title("Control de Acceso RFID")
ventana_principal.geometry("400x350")
ventana_principal.configure(bg="#2c3e50")

frame_header = tk.Frame(ventana_principal, bg="#2c3e50")
frame_header.pack(pady=10)

lbConexion = tk.Label(frame_header, text="Desconectado", fg="red", font=("Arial", 12, "bold"), bg="#2c3e50")
lbConexion.pack()

lbEstado = tk.Label(ventana_principal, text="Esperando...", fg="gray", font=("Arial", 16, "bold"), bg="#2c3e50")
lbEstado.pack(pady=10)

lbUUID = tk.Label(ventana_principal, text="UUID: ---", font=("Arial", 11), bg="#2c3e50", fg="white")
lbUUID.pack()
lbLog = tk.Label(ventana_principal, text="", font=("Arial", 9), bg="#2c3e50", fg="#ecf0f1")
lbLog.pack(pady=5)

frame_botones = tk.Frame(ventana_principal, bg="#2c3e50")
frame_botones.pack(pady=15)

btnConectar = tk.Button(frame_botones, text="Conectar", command=btnConectar_Click, width=12, bg="#27ae60", fg="white")
btnConectar.grid(row=0, column=0, padx=5)

btnDesconectar = tk.Button(frame_botones, text="Desconectar", command=btnDesconectar_Click, width=12, bg="#c0392b", fg="white", state=tk.DISABLED)
btnDesconectar.grid(row=0, column=1, padx=5)

btnConsultar = tk.Button(frame_botones, text="Consultar", command=abrir_ventana_consulta, width=12, bg="#3498db", fg="white")
btnConsultar.grid(row=0, column=2, padx=5)

frame_salir = tk.Frame(ventana_principal, bg="#2c3e50")
frame_salir.pack(pady=10)

btnSalir = tk.Button(frame_salir, text="Salir", command=on_closing, width=20, bg="#e74c3c", fg="white")
btnSalir.pack()

ventana_principal.protocol("WM_DELETE_WINDOW", on_closing)
ventana_principal.mainloop()