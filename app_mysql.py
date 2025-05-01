from flask import Flask, request, render_template, redirect, url_for
import pymysql
import logging
import time

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_connection():
    logging.info("Esperando a que MySQL esté listo...")
    for i in range(10): 
        try:
            return pymysql.connect(
                host="mysql-db",
                user="root",
                password="admin",
                database="prueba",
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
            logging.error(f"Intento {i+1}: Error al conectar a la base de datos: {e}")
            time.sleep(5) 
    return None

def crear_tabla_si_no_existe():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nombre VARCHAR(100),
                        edad INT
                    )
                """)
            conn.commit()
            logging.info("Tabla 'usuarios' verificada o creada correctamente.")
        except pymysql.MySQLError as e:
            logging.error(f"Error al crear la tabla: {e}")
        finally:
            conn.close()
            logging.info("Conexión a la base de datos cerrada.")

@app.route("/", methods=["GET", "POST"])
def index():
    crear_tabla_si_no_existe()

    logging.info("La página principal fue cargada, sirviendo el contenido actualizado.")
    
    conn = get_db_connection()
    if not conn:
        return "No se pudo conectar a la base de datos.", 500
    
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = request.form["edad"]
        logging.info(f"Insertando usuario esto es nuevo: Nombre = {nombre}, Edad = {edad}")
        try:
            cursor.execute("INSERT INTO usuarios (nombre, edad) VALUES (%s, %s)", (nombre, edad))
            conn.commit()
        except pymysql.MySQLError as e:
            logging.error(f"Error al insertar usuario: {e}")
        return redirect(url_for('index'))

    try:
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        logging.info(f"Usuarios recuperados y extraídos: {usuarios}")
    except pymysql.MySQLError as e:
        logging.error(f"Error al recuperar usuarios: {e}")
        usuarios = []

    finally:
        cursor.close()
        conn.close()

    return render_template("index.html", usuarios=usuarios)

@app.route("/eliminar/<int:usuario_id>", methods=["POST"])
def eliminar(usuario_id):
    logging.info(f"Eliminando usuario con ID: {usuario_id}")
    conn = get_db_connection()
    if not conn:
        return "No se pudo conectar a la base de datos.", 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
    except pymysql.MySQLError as e:
        logging.error(f"Error al eliminar usuario: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

if __name__ == "__main__":
    crear_tabla_si_no_existe()
    print("Flask está ejecutándose con recarga automática.")
    app.run(host="0.0.0.0", port="80", debug=True)
