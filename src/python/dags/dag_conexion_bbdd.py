from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2

def intentar_conexion():
    host = "postgres_container"
    port = "5432"
    dbname = "postgres"
    user = "postgres"
    password = "postgres123"

    # Crear conexión
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        print(f"Conexión exitosa a la base de datos {dbname}")
    except Exception as e:
        print(f"Error al conectar a la base de datos {dbname}:", e)

with DAG(
    dag_id="dag_conexion_bbdd",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None, 
    catchup=False,
    tags=["soyhenry"],
) as dag:

    tarea_conexion = PythonOperator(
        task_id="intentar_conexion",
        python_callable=intentar_conexion,
    )
