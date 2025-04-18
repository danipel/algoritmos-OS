import tkinter as tk
from threading import Thread, Semaphore, Lock
from time import sleep
import random

# Parámetros
NUM_SILLAS = 5
clientes_esperando = 0
mutex = Lock()
clientes = Semaphore(0)
barbero = Semaphore(0)

# Estado
estado_barbero = "Dormido"
cola_clientes = []

# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Problema del Barbero Dormilón")

canvas = tk.Canvas(ventana, width=600, height=400, bg='white')
canvas.grid(row=0, column=0, columnspan=2)

estado_label = tk.Label(ventana, text=f"Barbero: {estado_barbero}", font=('Arial', 14, 'bold'))
estado_label.grid(row=1, column=0, sticky='w', padx=10)

historial_text = tk.Text(ventana, height=10, width=70, wrap='word')
historial_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Dibujar sillas de espera
sillas_graficas = []
for i in range(NUM_SILLAS):
    x = 50 + i * 100
    y = 300
    silla = canvas.create_rectangle(x, y, x + 60, y + 60, fill='lightgray')
    sillas_graficas.append(silla)

# Silla del barbero
silla_barbero = canvas.create_rectangle(250, 100, 350, 180, fill='lightblue')
canvas.create_text(300, 90, text="Silla del Barbero", font=('Arial', 10, 'bold'))

cliente_grafico = None  # cliente atendido

def actualizar_interfaz():
    estado_label.config(text=f"Barbero: {estado_barbero}")
    
    # Actualizar sillas
    for i in range(NUM_SILLAS):
        color = "red" if i < len(cola_clientes) else "lightgray"
        canvas.itemconfig(sillas_graficas[i], fill=color)
    
    # Cliente atendido
    if cliente_grafico:
        canvas.itemconfig(cliente_grafico, state='normal')
    ventana.after(500, actualizar_interfaz)

def agregar_historial(mensaje):
    historial_text.insert(tk.END, mensaje + "\n")
    historial_text.see(tk.END)

# --- Lógica del barbero ---
def funcion_barbero():
    global estado_barbero, cliente_grafico
    while True:
        clientes.acquire()
        with mutex:
            global clientes_esperando
            clientes_esperando -= 1
            cliente_id = cola_clientes.pop(0)
        
        barbero.release()
        estado_barbero = "Cortando cabello 💇‍♂️"
        agregar_historial(f"Atendiendo cliente {cliente_id}")
        
        cliente_grafico = canvas.create_oval(280, 120, 320, 160, fill='orange')
        sleep(random.uniform(3, 5))  # cortar cabello
        canvas.delete(cliente_grafico)
        cliente_grafico = None

        estado_barbero = "Dormido 😴"
        agregar_historial("Barbero vuelve a dormir")

# --- Lógica de los clientes ---
contador_clientes = 1
# Activar para clientes automáticos
'''def nuevo_cliente():
    global clientes_esperando, contador_clientes
    while True:
        sleep(random.uniform(1, 8))
        con_atencion = False

        with mutex:
            if clientes_esperando < NUM_SILLAS:
                agregar_historial(f"Llega cliente {contador_clientes}")
                cola_clientes.append(contador_clientes)
                clientes_esperando += 1
                con_atencion = True
                clientes.release()  # Despierta al barbero

        if con_atencion:
            barbero.acquire()  # Espera su turno
        else:
            agregar_historial(f"Cliente {contador_clientes} se fue (sin sillas)")
        
        contador_clientes += 1'''
# Desactivar para clientes automáticos
def nuevo_cliente_manual():
    global clientes_esperando, contador_clientes
    con_atencion = False

    with mutex:
        if clientes_esperando < NUM_SILLAS:
            agregar_historial(f"Llega cliente {contador_clientes}")
            cola_clientes.append(contador_clientes)
            clientes_esperando += 1
            con_atencion = True
            clientes.release()  # Despierta al barbero

    if con_atencion:
        barbero.acquire()  # Espera su turno
    else:
        agregar_historial(f"Cliente {contador_clientes} se fue (sin sillas)")

    contador_clientes += 1
# ---------------------------------------

# Desactivar para clientes automáticos
boton_nuevo_cliente = tk.Button(ventana, text="Nuevo Cliente", font=('Arial', 12), command=lambda: Thread(target=nuevo_cliente_manual, daemon=True).start())
boton_nuevo_cliente.grid(row=1, column=1, padx=10)
# ---------------------------------------

# --- Iniciar hilos ---
Thread(target=funcion_barbero, daemon=True).start()
#Thread(target=nuevo_cliente, daemon=True).start()  # Activar para clientes automáticos
actualizar_interfaz()
ventana.mainloop()
