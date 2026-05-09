import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time
import queue
import mysql.connector

PUERTO = '/dev/ttyACM0'
BAUDIOS = 9600

# FUNCIÓN MYSQL
def insertar_en_mysql(uuid, codigo):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="programacionavanzada",
            port=3306
        )

        cursor = conexion.cursor()
        query = "INSERT INTO lecturas (uuid, codigo) VALUES (%s, %s)"
        cursor.execute(query, (uuid, codigo))

        conexion.commit()
        cursor.close()
        conexion.close()

        return True

    except mysql.connector.Error as e:
        messagebox.showerror("Error MySQL", str(e))
        return False


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector Serial + MySQL")
        self.root.geometry("400x300")
        self.root.configure(bg="lightgreen")

        self.uuid_var = tk.StringVar()
        self.codigo_var = tk.StringVar()

        tk.Label(root, text="UUID:", bg="lightgreen").pack(pady=5)
        tk.Entry(root, textvariable=self.uuid_var, width=40).pack()

        tk.Label(root, text="Código:", bg="lightgreen").pack(pady=5)
        tk.Entry(root, textvariable=self.codigo_var, width=40).pack()

        frame = tk.Frame(root, bg="lightgreen")
        frame.pack(pady=15)

        tk.Button(frame, text="Guardar", command=self.guardar).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Borrar", command=self.borrar).grid(row=0, column=1, padx=5)

        self.cola = queue.Queue()

        self.ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)
        time.sleep(2)

        self.running = True
        threading.Thread(target=self.leer_serial, daemon=True).start()

        self.actualizar_gui()

    def leer_serial(self):
        while self.running:
            if self.ser.in_waiting:
                linea = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if linea:
                    self.cola.put(linea)

    def actualizar_gui(self):
        while not self.cola.empty():
            linea = self.cola.get()

            if "," in linea:
                partes = linea.split(",")

                if len(partes) == 2:
                    self.uuid_var.set(partes[0])
                    self.codigo_var.set(partes[1])

        self.root.after(100, self.actualizar_gui)

    def guardar(self):
        uuid = self.uuid_var.get()
        codigo = self.codigo_var.get()

        if uuid and codigo:
            if insertar_en_mysql(uuid, codigo):
                messagebox.showinfo("Éxito", "Guardado en MySQL")
        else:
            messagebox.showerror("Error", "Datos vacíos")

    def borrar(self):
        self.uuid_var.set("")
        self.codigo_var.set("")

    def cerrar(self):
        self.running = False
        self.ser.close()
        self.root.destroy()


root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.cerrar)
root.mainloop()