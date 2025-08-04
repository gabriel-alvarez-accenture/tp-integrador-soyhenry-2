from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

host = "postgres_container"
port = "5432"
dbname = "postgres"
user = "postgres"
password = "postgres123"


def connect_database():
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
        raise

def read_data():
    csv_path = "/opt/airflow/resources/csv/AB_NYC.csv"

    try:
        df = pd.read_csv(csv_path)
        print("Data cargada correctamente en el DataFrame")
        return df
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
        raise  

def load_data(ti):
    df_dict = ti.xcom_pull(task_ids="read_data")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    
    engine = create_engine(db_url)
    df = pd.DataFrame(df_dict)

    try:
        df.to_sql("AB_NYC", engine, if_exists="append", index=False)
        print("Datos cargados exitosamente en la tabla xd")
    except Exception as e:
        print("Error al cargar datos:", e)
        raise  

with DAG(
    dag_id="dag_conexion_bbdd",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None, 
    catchup=False,
    tags=["soyhenry"],
) as dag:

    task_connection_db = PythonOperator(
        task_id="connect_database",
        python_callable=connect_database,
    )

    task_read_data = PythonOperator(
        task_id="read_data",
        python_callable=read_data,
    )

    task_load_data = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    task_connection_db >> task_read_data >> task_load_data
