import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

# 1. Crear la ventana principal usando ThemedTk en lugar de tk.Tk()
# Pasamos el nombre del tema directamente al parámetro 'theme'
root = ThemedTk(theme="equilux")
root.title("Mi Interfaz Equilux")
root.geometry("400x300")

# ¡IMPORTANTE para Equilux!:
# Como Equilux es un tema oscuro, el fondo de la ventana principal (root)
# no cambia automáticamente. Debes configurarlo para que coincida con el tema.
# Obtenemos el color de fondo del tema actual y lo aplicamos a la raíz:
bg_color = ttk.Style().lookup("TFrame", "background")
root.configure(bg=bg_color)

# 2. Crear un Frame usando ttk
# Siempre usa los widgets de 'ttk' (ttk.Frame, ttk.Button, etc.)
# en lugar de los de 'tk' clásico para que el tema se aplique correctamente.
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 3. Añadir widgets de ejemplo
titulo = ttk.Label(main_frame, text="Bienvenido a Equilux", font=("Helvetica", 16))
titulo.pack(pady=10)

entrada = ttk.Entry(main_frame, width=30)
entrada.pack(pady=10)
entrada.insert(0, "Escribe algo aquí...")

boton = ttk.Button(main_frame, text="Haz clic aquí")
boton.pack(pady=10)

# Barra de progreso para ver más detalles del tema
progreso = ttk.Progressbar(main_frame, mode="indeterminate")
progreso.pack(fill=tk.X, pady=10)
progreso.start(10)

# 4. Iniciar el bucle de la aplicación
root.mainloop()
