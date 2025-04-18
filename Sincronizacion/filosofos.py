import tkinter as tk
from threading import Thread, Lock, Semaphore
from time import sleep
import random
from math import sin, cos, pi

N = 5
estados = ['pensando'] * N
mutex = Lock()
tenedores = [Semaphore(1) for _ in range(N)]
historial = []

# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Cena de los Filósofos (Concurrente)")

canvas = tk.Canvas(ventana, width=500, height=500, bg='white')
canvas.grid(row=0, column=0, rowspan=5)

radio = 180
centro = 250
filosofo_labels = []
texto_labels = []
graf_tenedores = []

def coord(n, r=radio):
    ang = 2 * pi * n / N
    x = centro + r * cos(ang)
    y = centro + r * sin(ang)
    return x, y

for i in range(N):
    x, y = coord(i)
    f = canvas.create_oval(x-30, y-30, x+30, y+30, fill="gold", tags=f"F{i}")
    t = canvas.create_text(x, y, text=f"F{i}", font=('Arial', 14, 'bold'))
    filosofo_labels.append(f)
    texto_labels.append(t)

for i in range(N):
    x1, y1 = coord(i)
    x2, y2 = coord((i + 1) % N)
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    fork = canvas.create_rectangle(xm-10, ym-10, xm+10, ym+10, fill="gray", tags=f"T{i}")
    graf_tenedores.append(fork)

def actualizar_grafica():
    for i in range(N):
        color = {
            'pensando': 'gold',
            'hambriento': 'blue',
            'comiendo': 'green'
        }[estados[i]]
        canvas.itemconfig(f"F{i}", fill=color)

    for i in range(N):
        if estados[i] == 'comiendo' or estados[(i + 1) % N] == 'comiendo':
            canvas.itemconfig(graf_tenedores[i], fill='red')
        else:
            canvas.itemconfig(graf_tenedores[i], fill='gray')

    actualizar_historial()
    ventana.after(500, actualizar_grafica)

# --- Leyenda visual ---
leyenda = tk.LabelFrame(ventana, text="Convenciones", padx=10, pady=5, font=('Arial', 12, 'bold'))
leyenda.grid(row=0, column=1, sticky='nw', padx=10)

colores = {
    "Pensando (gold)": "gold",
    "Hambriento (blue)": "blue",
    "Comiendo (green)": "green",
    "Tenedor libre (gray)": "gray",
    "Tenedor ocupado (red)": "red"
}

for texto, color in colores.items():
    frame = tk.Frame(leyenda)
    canvas_color = tk.Canvas(frame, width=20, height=20, bg=color)
    canvas_color.pack(side='left')
    label = tk.Label(frame, text=texto)
    label.pack(side='left')
    frame.pack(anchor='w')

# --- Historial ---
historial_frame = tk.LabelFrame(ventana, text="Historial", padx=10, pady=5, font=('Arial', 12, 'bold'))
historial_frame.grid(row=1, column=1, sticky='nw', padx=10, pady=5)

historial_text = tk.Text(historial_frame, height=20, width=40, wrap='word')
historial_text.pack()

def agregar_historial(mensaje):
    historial.append(mensaje)
    if len(historial) > 100:
        historial.pop(0)

def actualizar_historial():
    historial_text.delete('1.0', tk.END)
    for linea in historial[-20:]:  # mostrar últimas 20 líneas
        historial_text.insert(tk.END, linea + '\n')

# --- Lógica de filósofos ---
def izquierda(i): return (i + N - 1) % N
def derecha(i): return (i + 1) % N

def filosofo(i):
    global estados
    while True:
        estados[i] = 'pensando'
        agregar_historial(f"Filósofo {i} está pensando 🧠")
        sleep(random.uniform(1, 3))

        estados[i] = 'hambriento'
        agregar_historial(f"Filósofo {i} tiene hambre 🍽️")
        with mutex:
            tenedores[i].acquire()
            tenedores[derecha(i)].acquire()
            estados[i] = 'comiendo'
            agregar_historial(f"Filósofo {i} está comiendo 🍝")

        sleep(random.uniform(2, 4))

        estados[i] = 'pensando'
        agregar_historial(f"Filósofo {i} ha terminado de comer y piensa 💭")
        tenedores[i].release()
        tenedores[derecha(i)].release()

# --- Iniciar hilos ---
for i in range(N):
    Thread(target=filosofo, args=(i,), daemon=True).start()

actualizar_grafica()
ventana.mainloop()
