import os
from airflow.models import DagBag

# Ruta relativa a la carpeta de DAGs
DAGS_FOLDER = os.path.join(os.path.dirname(__file__), "../dags")

def test_dag_import():
    dag_bag = DagBag(dag_folder=DAGS_FOLDER, include_examples=False)

    # Verifica que no haya errores al importar
    assert dag_bag.import_errors == {}, f"Errores al importar DAGs: {dag_bag.import_errors}"

    # Verifica que el DAG específico esté presente
    assert 'dag_ELT_api' in dag_bag.dags, "El DAG 'dag_ELT_api' no fue encontrado"
