# Imagen base oficial de Apache Airflow versión 2.7.2
FROM apache/airflow:2.7.2

# Cambia al usuario 'airflow' para ejecutar las siguientes instrucciones
USER airflow

# Copia el archivo de dependencias al contenedor
COPY requirements.txt /

# Instala las dependencias definidas en requirements.txt sin guardar caché
RUN pip install --no-cache-dir -r /requirements.txt
