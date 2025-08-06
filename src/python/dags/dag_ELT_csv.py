from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
import pandas as pd
import boto3
from sqlalchemy import create_engine
from airflow.operators.bash import BashOperator
from io import StringIO
from sqlalchemy import text
import os
from dotenv import load_dotenv
import logging


dag_folder = os.path.dirname(__file__)
env_path = os.path.join(dag_folder, ".env")
load_dotenv(dotenv_path=env_path)

# Acceder a las variables
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname")
user = os.getenv("user")
password = os.getenv("password")
miniouser = os.getenv("miniouser")
miniopassword = os.getenv("miniopassword")
csv_path = os.getenv("csv_path")
miniobucket = os.getenv("miniobucket")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


# Configurar el cliente de MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id=miniouser,
    aws_secret_access_key=miniopassword,
    region_name='us-east-1'
)

# Crear una instancia de logger
dag_folder = os.path.dirname(__file__)
logs_folder = os.path.join(os.path.dirname(dag_folder), "logs")
os.makedirs(logs_folder, exist_ok=True)

log_path = os.path.join(logs_folder, f"dag_ELT_CSV_{timestamp}.log")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()


def check_db_and_file():
    try:
        logger.info(f"Comenzando la prueba de conexion a la base de datos {dbname}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        logger.info(f"Conexión exitosa a la base de datos {dbname}")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos {dbname}:", e)
        raise

    try:
        logger.info("Comenzando prueba para verificacion de existencia de archivo AB_NYC.csv")
        if os.path.exists(csv_path):
            logger.info("El archivo existe.")
        else:
            raise FileNotFoundError("El archivo no fue encontrado.")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")

def read_and_save_raw_data():
    try:
        df = pd.read_csv(csv_path)

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        key_name = f"caso-csv/{timestamp}/AB_NYC.csv"  

        s3.put_object(
            Bucket='bucket-raw',
            Key=f"{key_name}",  
            Body=csv_buffer.getvalue()
        )

        return key_name
    except Exception as e:
        logger.error("Error al leer el archivo CSV para persistir los datos en la capa RAW (MinIO)", e)
        raise  

def load_data(ti):
    try:
        path_csv = ti.xcom_pull(task_ids="read_and_save_raw_data")
        response = s3.get_object(Bucket=miniobucket, Key=path_csv)
        df = pd.read_csv(response['Body'])
        logger.info("Archivo leído correctamente desde MinIO")
    except Exception as e:
        logger.error(f"Error al leer el archivo en MinIO: {e}")

    try:
        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM "AB_NYC"'))

        df.to_sql("AB_NYC", engine, if_exists="append", index=False)
        logger.info(f"Datos cargados exitosamente en la base de datos en la tabla AB_NYC")
    except Exception as e:
        logger.error(f"Error al cargar los datos en la base de datos: {e}")
        raise  

with DAG(
    dag_id="dag_ELT_csv",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None, 
    catchup=False,
    tags=["soyhenry"],
) as dag:

    task_check_db_and_file = PythonOperator(
        task_id="check_db_and_file",
        python_callable=check_db_and_file,
    )

    task_read_and_save_raw_data = PythonOperator(
        task_id="read_and_save_raw_data",
        python_callable=read_and_save_raw_data,
    )
    
    task_load_data = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    task_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='dbt run --project-dir /opt/dbt',
    )
    
    
    task_check_db_and_file >> task_read_and_save_raw_data >> task_load_data >> task_dbt