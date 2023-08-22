import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

# Create the Tkinter GUI
root = tk.Tk()
root.title("Matplotlib in Tkinter")

# Create a Matplotlib Figure and Plot
fig, ax = plt.subplots()
line, = ax.plot([], [], label='garis aja')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Matplotlib Plot')
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

x = [x/365 for x in range(1000)]
y = [100]
for p in range(999):
    y.append(max([round(y[-1] * 0.9 + y[-1] * np.random.normal(1.01, 0.2) * 0.1), 50]))

def update_chart():
    global x
    global y
    y = y[1:]
    y.append(max([round(y[-1] * 0.9 + y[-1] * np.random.normal(1.01, 0.2) * 0.1), 50]))
    line.set_xdata(x)
    line.set_ydata(y)
    ax.set_ylim(bottom=0, top=max(y))
    ax.relim()
    ax.autoscale_view()
    ax.set_title("Treding")
    
    canvas.draw()

    root.after(1, update_chart)

root.after(1000, update_chart)
# Run the Tkinter Main Loop
root.mainloop()
