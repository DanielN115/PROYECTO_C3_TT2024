from tkinter import *
import math

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#fe0000"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
BLUE = "#2271b3"
FONT_NAME = "Courier"

WORK_MIN = 1/20 #25 minutos, cuando termina se considera 1 pomodoro
SHORT_BREAK_MIN = 1/21 #5 minutos
LONG_BREAK_MIN = 1/21 #15 a 30 minutos, solo cuando se hagan 4 pomodoros

reps = 0
reps_final = 0
timer = 0
check_marks_list = []

# ---------------------------- TIMER RESET ------------------------------- # 

def reset_timer(): # Deja los labels en defecfto, borra las marcas
    global reps
    window.after_cancel(timer)
    timer_label.config(text="00:00")
    title_label.config(text="Timer", fg=GREEN)
    clear_check_marks()
    reps = 0

def clear_check_marks(): # Metodo para borrar las marcas tanto en la lista como en el frame
    for label in check_marks_list:
        label.destroy()
    for label in check_marks_frame.winfo_children():
        label.destroy()
    check_marks_list.clear()
    
    
# ---------------------------- TIMER MECHANISM ------------------------------- # 

def start_timer():
    global reps
    print(reps)
    if timer:
        window.after_cancel(timer)  # Cancela el temporizador anterior
        
    # Si es un descanso largo, limpia las marcas de verificación
    if reps % 8 == 0:
        clear_check_marks()
    reps += 1
    
    work_sec = int(WORK_MIN * 60)  # El metodo int nos asegura que si nos da un float no aparesca la parte decimal
    short_break_sec = int(SHORT_BREAK_MIN * 60)
    long_break_sec = int(LONG_BREAK_MIN * 60)

    if reps % 8 == 0 and reps > 0:  # Limpiar marcas de verificación antes de un descanso largo
        count_down(long_break_sec)
        title_label.config(text="Long Break", fg=RED, font=(FONT_NAME, 50))
    elif reps % 2 == 0:  # todas las repeticiones pares son descansos
        count_down(short_break_sec)
        title_label.config(text="Break", fg=PINK, font=(FONT_NAME, 50))
    else:  # si no es descanso entonces es para trabajo
        count_down(work_sec)
        title_label.config(text="Work", fg=GREEN, font=(FONT_NAME, 50))


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #


def count_down(count):
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
    else:
        global reps, reps_final
        if reps % 8 == 0:
            reset_timer()
            save_sesion()
        else:
            reps_final += 1
            if reps % 2 == 0:
                update_check_marks()
            start_timer()  # Reinicia el temporizador cuando llega a 00:00

def update_check_marks():
    global reps
    check_img_label = Label(check_marks_frame, image=tomato_check_img, bg=BLUE)
    check_img_label.pack(side=LEFT, padx=5)
    check_marks_list.append(check_img_label)
          
def save_sesion():
    global reps_final, check_marks_list, reps
    reset_timer()
    title_label.config(text="SESIÓN COMPLETA", fg=GREEN, font=(FONT_NAME, 40))
    timer_label.config(text="00:00")
    
    print(reps_final)
    print(reps)
    print(check_marks_frame)
    print(check_marks_list)
        
    for i in range(math.floor((reps_final+1)/2)):
        check_img_label = Label(check_marks_frame, image=tomato_check_img, bg=BLUE)
        check_img_label.pack(side=LEFT, padx=5)
        check_marks_list.append(check_img_label)
    reps_final = 0

# ---------------------------- UI SETUP ------------------------------- #

# Crea la ventana principal
window = Tk()
window.title("Pomodoro")
window.config(padx=20, pady=10, bg=BLUE)
window.geometry("650x700")
window.resizable(width=False, height=False)

# Crea el título
title_label = Label(text="Timer", fg=GREEN, bg=BLUE, font=(FONT_NAME, 50))
title_label.grid(column=1, row=0, pady=(0, 10))

# Crea un label para la imagen 
tomato_img = PhotoImage(file="img/icon_Pomodoro.png")  # imagen principal
tomato_check_img = PhotoImage(file="img/icon_Pomodoro2.png")  # imagen que remplaza los checks
icon_label = Label(image=tomato_img, bg=BLUE)
icon_label.grid(column=1, row=1, pady=(0, 10))

# Crea un label para el temporizador
timer_label = Label(text="00:00", fg="white", bg=RED, font=(FONT_NAME, 80, "bold"))
timer_label.grid(column=1, row=1, pady=(0, 10))

# Crea botones de start y reset
start_button = Button(text="Start", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2)

# Crea un frame para las marcas de verificación de pomodoro
check_marks_frame = Frame(window, bg=BLUE)
check_marks_frame.grid(column=1, row=3)

# Inicia el loop principal de la ventana
window.mainloop()