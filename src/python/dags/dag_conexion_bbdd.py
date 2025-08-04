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

host = "postgres_container"
port = "5432"
dbname = "postgres"
user = "postgres"
password = "postgres123"

# Configurar el cliente de MinIO (usando boto3)
s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)


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

        # Convertir el DataFrame a CSV en memoria
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        # Timestamp para la carpeta
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key_name = f"caso-csv/{timestamp}/AB_NYC.csv"  

        # Subir el archivo al bucket
        s3.put_object(
            Bucket='bucket-raw',
            Key=f"{key_name}",  
            Body=csv_buffer.getvalue()
        )


        #print("Data cargada correctamente en el DataFrame")
        return key_name
    except Exception as e:
        print("Error al leer el archivo CSV:", e)
        raise  

def load_data(ti):
    path_csv = ti.xcom_pull(task_ids="read_data")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    
    engine = create_engine(db_url)

    # Obtener el objeto desde MinIO
    response = s3.get_object(Bucket="bucket-raw", Key=path_csv)

    # Leer el contenido como DataFrame
    df = pd.read_csv(response['Body'])

    print(df.head())

    try:
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM "AB_NYC"'))


        df.to_sql("AB_NYC", engine, if_exists="append", index=False)
        print("Datos cargados exitosamente en la tabla")
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

    task_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='dbt run --project-dir /opt/dbt',
    )
    
    
    task_connection_db >> task_read_data >> task_load_data >> task_dbt
