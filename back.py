from flask import Flask, jsonify, request
from flask_cors import CORS # Necesario para permitir solicitudes desde el frontend
import psycopg2
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas, permitiendo que tu frontend acceda a esta API

# --- Carga de variables de entorno ---
# Asegúrate de tener un archivo .env en el mismo directorio con tus credenciales de Supabase DB
load_dotenv()

# --- Configuración de Conexión a PostgreSQL (Supabase) ---
# Obtén estas credenciales de tu panel de control de Supabase (Database -> Connection String)
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

# Nombre de la tabla de Supabase que deseas consultar
# ¡IMPORTANTE! Asegúrate de que este nombre coincida EXACTAMENTE con el nombre de tu tabla en Supabase,
# incluyendo mayúsculas y minúsculas. PostgreSQL es sensible a mayúsculas/minúsculas para nombres entre comillas.
SUPABASE_TABLE_NAME = "transacciones_credito" 

# Asegúrate de que tu tabla tenga al menos las columnas 'id', 'nombre', 'categoria' y 'valor'
# para que el frontend funcione correctamente. 'valor' será la columna que se sumará.

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Endpoint para obtener datos de Supabase usando psycopg2.
    Retorna los datos de la tabla especificada como JSON.
    """
    connection = None
    cursor = None
    try:
        # Conecta a la base de datos PostgreSQL de Supabase
        connection = psycopg2.connect(
            user="postgres.rtustrknlofzfphcbgqe",
            password="wpAhsatAY8wcJJSb",
            host="aws-0-sa-east-1.pooler.supabase.com",
            port="6543",
            dbname="postgres"
        )
        cursor = connection.cursor()

        # Ejecuta la consulta SQL para obtener todos los datos de la tabla
        # Se han añadido comillas dobles alrededor del nombre de la tabla para manejar la sensibilidad a mayúsculas/minúsculas de PostgreSQL.
        cursor.execute('SELECT * FROM "Transacciones_Credito";')
        
        # Obtiene los nombres de las columnas para crear diccionarios
        column_names = [desc[0] for desc in cursor.description]
        
        # Obtiene todas las filas
        rows = cursor.fetchall()

        # Convierte las filas a una lista de diccionarios para facilitar la serialización JSON
        data = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            data.append(row_dict)

        if not data:
            # Si no se encuentran datos
            return jsonify({"error": "No se encontraron datos en la tabla especificada."}), 404

        # Retorna los datos en formato JSON
        return jsonify(data)

    except psycopg2.Error as e:
        # Manejo de errores específicos de PostgreSQL
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Fallo al obtener datos de la base de datos", "detalles": str(e)}), 500
    except Exception as e:
        # Manejo de otros errores
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Fallo inesperado al obtener datos", "detalles": str(e)}), 500
    finally:
        # Asegúrate de cerrar el cursor y la conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    # Ejecuta la aplicación Flask en modo de depuración para desarrollo.
    # En producción, usarías un servidor WSGI como Gunicorn.
    # Asegúrate de que el puerto (5000) sea el mismo que usa el frontend para la llamada API.
    app.run(debug=True, port=5000)
