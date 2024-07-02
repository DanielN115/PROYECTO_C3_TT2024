import configparser
import mysql.connector
from datetime import datetime

def setup_database():
    config = configparser.ConfigParser() #Gestiona los archivos para leerlos y cerrarlos
    config.read('config.ini')
    db_config = {
        'host': config['database']['host'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'database': config['database']['database']
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        reps_final INT,
                        date_completed DATETIME)''')
    conn.commit()
    cursor.close()
    conn.close()
    
def save_to_database(reps_final):
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = {
        'host': config['database']['host'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'database': config['database']['database']
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    date_completed = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Guarda el tiempo en que se lo llama, #Año, mes, dia, hora, minutos, segundos
    cursor.execute("INSERT INTO sessions (reps_final, date_completed) VALUES (%s, %s)", (reps_final, date_completed))
    conn.commit()
    cursor.close()
    conn.close()
    
def show_history_db():
    # Conectarse a la base de datos y recuperar datos
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = {
        'host': config['database']['host'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'database': config['database']['database']
    }
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions")
    rows = cursor.fetchall()
    conn.close()
    return rows
    
def main():
    pass

if __name__ == "__main__":
    main()