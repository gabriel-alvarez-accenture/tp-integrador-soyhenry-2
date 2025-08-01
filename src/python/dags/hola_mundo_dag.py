from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hola_mundo():
    print("Hola mundo")

with DAG(
    dag_id="hola_mundo_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Solo se ejecuta manualmente
    catchup=False,
    tags=["ejemplo"],
) as dag:

    tarea_saludo = PythonOperator(
        task_id="imprimir_hola_mundo",
        python_callable=hola_mundo,
    )
