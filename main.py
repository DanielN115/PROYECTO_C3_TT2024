from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import database as db
import matplotlib.pyplot as plt
import calendar


# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#fe0000"
RED_LIGHT = "#ff5232"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
BLUE = "#2686ac"
BLUE_LIGHT = "#2071b3"
FONT_NAME = "Aptos (Cuerpo)"

WORK_MIN = 25 #25 minutos, cuando termina se considera 1 pomodoro
SHORT_BREAK_MIN = 5 #5 minutos
LONG_BREAK_MIN = 30 #15 a 30 minutos, solo cuando se hagan 4 pomodoros

reps = 0
reps_final = 0
timer = 0
check_marks_list = []
paused = False
remaining_time = 0

# ---------------------------- DATABASE ------------------------------- # 
try:
    db.setup_database()
except:
    pass
    #messagebox.showerror("Error", "Conexión fallida a la base de datos")
# ---------------------------- TIMER RESET ------------------------------- # 

def reset_timer(): # Deja los labels en defecfto, borra las marcas
    global reps, reps_final
    if reps != 0:
        window.after_cancel(timer)
        timer_label.config(text="00:00")
        title_label.config(text="Timer", fg=GREEN)
        clear_check_marks()
        reps = 0
        pause_button.config(text="PAUSE",font=(FONT_NAME, 12))

def clear_check_marks(): # Metodo para borrar las marcas tanto en la lista como en el frame
    for label in check_marks_list:
        label.destroy()
    for label in check_marks_frame.winfo_children():
        label.destroy()
    check_marks_list.clear()
    
    
# ---------------------------- TIMER MECHANISM ------------------------------- # 

def start_timer():
    global reps, reps_final
    #print(reps)
    
    if timer:
        window.after_cancel(timer)  # Cancela el temporizador anterior
        
    # Si es un descanso largo, limpia las marcas de verificación
    if reps % 8 == 0:
        clear_check_marks()
    elif reps == 0:
        reps_final = 0
    reps += 1
    works = reps + 1 
    
    work_sec = int(WORK_MIN * 60)  # El metodo int nos asegura que si nos da un float no aparesca la parte decimal
    short_break_sec = int(SHORT_BREAK_MIN * 60)
    long_break_sec = int(LONG_BREAK_MIN * 60)

    if reps <= 8:
        if reps % 8 == 0 and reps > 0:  # Limpiar marcas de verificación antes de un descanso largo
            count_down(long_break_sec)
            title_label.config(text="Long Break", fg=RED, font=(FONT_NAME, 50))
        elif reps % 2 == 0:  # todas las repeticiones pares son descansos
            count_down(short_break_sec)
            title_label.config(text=f"Break {works // 2}", fg=PINK, font=(FONT_NAME, 50))
        else:  # si no es descanso entonces es para trabajo
            count_down(work_sec)
            title_label.config(text=f"Work {works // 2}", fg=GREEN, font=(FONT_NAME, 50))
    else: 
        save_sesion()

def pause_timer():
    global paused, timer
    if reps != 0:
        if paused:
            count_down(remaining_time)
            paused = False
            pause_button.config(text="PAUSE")
        else:
            window.after_cancel(timer)
            paused = True
            pause_button.config(text="RESUME")
        
# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #

def count_down(count):
    global remaining_time
    count_min = math.floor(count / 60)  # Calcula los minutos restantes del tiempo y los redondea
    count_sec = count % 60  # calcula los segundos restantes
    
    if count_sec < 10:  # Si los segundos son menores a 10, agrega un cero al inicio para mantener el formato 00:00
        count_sec = f"0{count_sec}"
    if count_min == 0:
        count_min = f"0{count_min}"

    timer_label.config(text=f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
        remaining_time = count
    else:
        global reps, reps_final
        if reps % 8 == 0:
            save_sesion()
        else:
            if reps % 2 != 0:
                reps_final += 1
                update_check_marks()
            start_timer()  # Reinicia el temporizador cuando llega a 00:00
            
# ---------------------------- CHECKMARKS MECHANISM ------------------------------- #

def update_check_marks():
    global reps
    check_img_label = Label(check_marks_frame, image=tomato_check_img, bg=BLUE)
    check_img_label.pack(side=LEFT, padx=5)
    check_marks_list.append(check_img_label)
          

# ---------------------------- SAVE IN DATABASE ------------------------------- #
def save_sesion():
    global reps_final, check_marks_list, reps
    if reps != 0: 
        try:
            db.save_to_database(reps_final) # Guarda la sesión en la base de datos
        except:
            messagebox.showerror("Error", "Conexión fallida a la base de datos")
        
        reset_timer()
        title_label.config(text="SESIÓN COMPLETA", fg=GREEN, font=(FONT_NAME, 40))
        timer_label.config(text="00:00")
        
        #print(reps_final, reps)        
        
        for i in range(math.floor(reps_final)):
            check_img_label = Label(check_marks_frame, image=tomato_check_img, bg=BLUE)
            check_img_label.pack(side=LEFT, padx=5)
            check_marks_list.append(check_img_label)
        reps_final = 0

# ---------------------------- SHOW HISTORIAL IU ------------------------------- #

def show_history():
    try:
        rows = db.show_history_db()[-10:]  # Obtener las últimas 10 filas de la base de datos
        
        # Crear listas para datos de gráfica
        reps_final = [row[1] for row in rows]  # Campo reps_final
        dates = [row[2].strftime("%d/%B/%Y\n%Hh:%Mm:%Ss") for row in rows]  # Campo fecha completada con nombre de mes

        # Calcular recuento de pomodoros completados
        count_0 = reps_final.count(0)
        count_1 = reps_final.count(1)
        count_2 = reps_final.count(2)
        count_3 = reps_final.count(3)
        count_4 = reps_final.count(4)

        # Calcular la media de pomodoros completados
        if reps_final:
            mean_reps_final = sum(reps_final) / len(reps_final)
        else:
            mean_reps_final = 0

        # Configurar la gráfica utilizando matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar el tamaño de la figura
        bar_width = 0.5  # Ancho de las barras

        # Calcular el máximo valor de reps_final para ajustar el eje y
        ax.bar(dates, reps_final, width=bar_width, color='b', alpha=0.7)
        ax.set_title('Historial de Sesiones - Ultimas 10')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Repeticiones Completadas')
        ax.set_ylim(0, 4)  # Ajuste el limite de la escala en y
        ax.grid(True)
        fig.autofmt_xdate()  # Rota las fechas para mejor visualización

        # Mostrar la gráfica en la ventana de historial
        history_window = Toplevel()
        history_window.title("Historial de Sesiones")

        # Mostrar el recuento y la media de pomodoros completados
        info_label = Label(history_window, text=f"Recuento de Pomodoros Completados:\n"
                                                f"Sesiones con 0 pomodoros: {count_0}\n"
                                                f"Sesiones con 1 pomodoros: {count_1}\n"
                                                f"Sesiones con 2 pomodoros: {count_2}\n"
                                                f"Sesiones con 3 pomodoros: {count_3}\n"
                                                f"Sesiones con 4 pomodoros: {count_4}\n\n"
                                                f"Totales Sesiones: {count_0 + count_1 + count_2 + count_3 + count_4}\n"
                                                f"Media de Repeticiones Completadas: {mean_reps_final:.2f}",
                                                
                                                font=(FONT_NAME, 12))
        info_label.pack(padx=10, pady=10)

        
        # Mostrar la gráfica en la ventana de historial
        canvas = FigureCanvasTkAgg(fig, master=history_window)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10, fill=BOTH, expand=True)
        
    except:
        messagebox.showerror("Error", "Conexión fallida a la base de datos")

# ---------------------------- UI SETUP ------------------------------- #

# Ventana principal
window = Tk()
window.title("Pomodoro")
window.config(padx=20, pady=10, bg=BLUE)
window.geometry("600x720")
window.resizable(width=False, height=False)

# Título
title_label = Label(text="Timer", fg=GREEN, bg=BLUE, font=(FONT_NAME, 50))
title_label.grid(column=1, row=0, pady=(0, 10))

# Label para la imagen 
tomato_img = PhotoImage(file="img/icon_Pomodoro.png")  # imagen principal
tomato_check_img = PhotoImage(file="img/icon_Pomodoro2.png")  # imagen que remplaza los checks
icon_label = Label(image=tomato_img, bg=BLUE)
icon_label.grid(column=1, row=1, pady=(0, 10))

# Label para el temporizador
timer_label = Label(text="00:00", fg="white", bg=RED, font=(FONT_NAME, 80, "bold"))
timer_label.grid(column=1, row=1, pady=(0, 10))

# Frame para los botones
buttons_frame = Frame(window, bg=BLUE)
buttons_frame.grid(column=1, row=3, pady=(10, 0))

# Botones del frame de botones
start_button = Button(buttons_frame, text="START", bg=GREEN, fg="black", font=(FONT_NAME, 12), command=start_timer)
start_button.pack(side=LEFT, padx=20)

pause_button = Button(buttons_frame, text="PAUSE", bg=GREEN, fg="black", font=(FONT_NAME, 12), command=pause_timer)
pause_button.pack(side=LEFT, padx=20)

reset_button = Button(buttons_frame, text="RESET", bg=RED_LIGHT, fg="black", font=(FONT_NAME, 12), command=reset_timer)
reset_button.pack(side=LEFT, padx=20)

finish_button = Button(buttons_frame, text="FINISH", bg=RED_LIGHT, fg="black", font=(FONT_NAME, 12), command=save_sesion)
finish_button.pack(side=LEFT, padx=20)

historial_button = Button(buttons_frame, text="HISTORIAL", bg=YELLOW, fg="black", font=(FONT_NAME, 12), command=show_history)
historial_button.pack(side=LEFT, padx=20)

# Frame para las marcas de verificación de pomodoro
check_marks_frame = Frame(window, bg=BLUE)
check_marks_frame.grid(column=1, row=4, pady=10)

# Inicia el loop principal de la ventana
window.mainloop()