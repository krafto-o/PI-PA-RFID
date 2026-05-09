import tkinter as tk
from tkinter import messagebox
import serial
import threading
import re
import mysql.connector


def insertarRegistro(id_temp, celcius, fahrenheit, rawvalue):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="exapractico04",
            port=3306,
        )
        cursor = conexion.cursor()
        query = "INSERT INTO temperatura (id_temp, celcius, fahrenheit,rawvalue) VALUES (%s, %s, %s, %s)"
        valores = (id_temp, celcius, fahrenheit, rawvalue)
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        messagebox.showinfo(
            "Información", "Datos guardados en la base de datos con exito."
        )
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error al insertar datos: {e}")


arduino = serial.Serial()
arduino.port = "COM5"
arduino.baudrate = 9600
arduino.timeout = 0.5
arduino.write_timeout = 0.5

is_connected = False


def DataReceivedHandler():
    global is_connected
    while is_connected:
        try:
            if arduino.is_open and arduino.in_waiting > 0:
                dato = arduino.readline()
                if dato:
                    ventana_principal.after(0, EscribirDato, dato)
        except serial.SerialException:
            messagebox.showerror("Error al conectar", "Error")


def EscribirDato(dato):
    lbTemp.config(text=dato)


def btnConectar_Click():
    global is_connected
    try:
        if not arduino.is_open:
            arduino.open()

        limite_texto = tboxLimite.get()
        try:
            temperatura_limite = int(limite_texto)
            arduino.write(str(temperatura_limite).encode("utf-8"))

            btnConectar.config(state=tk.DISABLED)
            btnDesconectar.config(state=tk.NORMAL)
            lbConexion.config(text="Conexion Correcta", fg="lime green")

            if not is_connected:
                is_connected = True
                hilo_lectura = threading.Thread(target=DataReceivedHandler, daemon=True)
                hilo_lectura.start()

        except ValueError:
            messagebox.showerror(
                "Error de limite de temperatura", "Ingrese un valor correcto"
            )
            if arduino.is_open:
                arduino.close()

    except serial.SerialException:
        messagebox.showerror(
            "Error de COM", "Configure el puerto de comunicacion correcto"
        )


def btnDesconectar_Click():
    global is_connected
    is_connected = False

    btnConectar.config(state=tk.NORMAL)
    btnDesconectar.config(state=tk.DISABLED)

    if arduino.is_open:
        arduino.close()

    lbConexion.config(text="Desconectado", fg="red")
    lbTemp.config(text="0.0")


def on_closing():
    btnDesconectar_Click()
    ventana_principal.destroy()


ventana_principal = tk.Tk()
ventana_principal.title("exapractico04")
ventana_principal.geometry("350x250")

tk.Label(ventana_principal, text="Límite de Temperatura:").pack(pady=(10, 0))
tboxLimite = tk.Entry(ventana_principal, justify="center")
tboxLimite.pack(pady=5)

btnConectar = tk.Button(
    ventana_principal, text="Conectar", command=btnConectar_Click, width=15
)
btnConectar.pack(pady=5)

btnDesconectar = tk.Button(
    ventana_principal,
    text="Desconectar",
    command=btnDesconectar_Click,
    state=tk.DISABLED,
    width=15,
)
btnDesconectar.pack(pady=5)

lbConexion = tk.Label(
    ventana_principal, text="Desconectado", fg="red", font=("Arial", 10, "bold")
)
lbConexion.pack(pady=5)

tk.Label(ventana_principal, text="Temperatura:").pack()
lbTemp = tk.Label(ventana_principal, text="0.0", font=("Arial", 24, "bold"))
lbTemp.pack(pady=5)

ventana_principal.mainloop()
