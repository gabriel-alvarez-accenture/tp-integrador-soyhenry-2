📊 Relevancia de los Datos
Este proyecto contempla dos casos principales de ingestión de datos, cada uno con su propia fuente y tratamiento:

🗂️ Caso 1: Archivo CSV
El archivo .csv ya se encuentra ubicado en el repositorio, por lo tanto, la fuente de datos es el propio archivo. Este atraviesa todo el proceso ELT (Extract, Load, Transform) para generar información relevante para el negocio.
Durante este proceso se generan tablas de dimensiones y una tabla de hechos, lo que permite estructurar los datos de forma clara y facilitar su análisis.

🌐 Caso 2: Consumo de API
En este caso, los datos se obtienen desde una API externa. La consulta es totalmente parametrizable mediante el archivo de entorno .env, lo que evita el hardcodeo y permite una configuración flexible.
Los datos extraídos se procesan para obtener una tabla única y refinada, lista para ser utilizada en análisis posteriores.



🏗️ Arquitectura de los Datos
Este proyecto se apoya en un stack moderno de herramientas que permiten construir una arquitectura robusta, escalable y trazable para procesos ELT.

🔄 Airflow
Airflow fue elegido por su capacidad de escalar en entornos distribuidos, su integración nativa con múltiples herramientas del ecosistema de datos, y su eficiencia para orquestar procesos complejos de forma robusta, trazable y modular.
Es ideal para coordinar flujos ELT, permitiendo definir dependencias, programar tareas y monitorear ejecuciones con facilidad.

🧱 DBT (Data Build Tool)
DBT permite transformar datos directamente sobre el motor SQL de forma modular, eficiente y controlada.
Su integración con Airflow y Git facilita la escalabilidad, el versionado y la calidad del código, lo que lo convierte en una herramienta clave en entornos analíticos modernos.

🗄️ MinIO
MinIO proporciona un almacenamiento de objetos altamente escalable y compatible con S3, ideal para manejar datos crudos de forma eficiente y económica.
Ofrece buena performance, fácil integración con el ecosistema de datos, y añade una capa de seguridad mediante el cifrado de objetos.

🐘 PostgreSQL
PostgreSQL se utiliza como base de datos relacional por su rendimiento sólido, bajo costo y amplia compatibilidad con herramientas del stack.
Es especialmente adecuado como motor SQL para transformaciones con DBT en entornos de tamaño medio, y también sirve como repositorio para las capas STAGING, CORE y CONSUMO.



🧬 Capas de la Arquitectura de Datos
La arquitectura de datos se organiza en capas bien definidas que permiten estructurar el pipeline ELT de forma clara, escalable y mantenible:

🟤 RAW (MinIO)
Almacena los datos extraídos directamente desde las fuentes, sin ningún tipo de procesamiento.
Representa una copia fiel del origen y es el punto de partida del pipeline.
Ideal para conservar la trazabilidad y auditar los datos originales.
🟡 STAGING (PostgreSQL)
Recibe los datos desde la capa RAW para realizar tareas de limpieza, normalización y preparación.
Es una capa transitoria que facilita las transformaciones posteriores.
Permite desacoplar la extracción de la transformación, mejorando la modularidad del pipeline.
🟢 CORE (PostgreSQL + dbt)
Contiene los datos transformados en modelos de negocio, como tablas de hechos y dimensiones.
Es la última capa del proceso ELT, donde los datos están listos para análisis y toma de decisiones.
Las transformaciones se realizan con dbt, asegurando calidad, versionado y trazabilidad.
🔵 CONSUMO (PostgreSQL)
Aunque el proceso ELT finaliza en la capa CORE, PostgreSQL también alberga una capa de consumo.
Aquí los usuarios finales pueden crear vistas, métricas y dashboards personalizados según sus necesidades.
Facilita el acceso a la información de forma flexible y orientada al negocio.



🐳 Cómo Ejecutar el Pipeline ELT con Docker
Este proyecto utiliza un Dockerfile personalizado para construir un entorno de Airflow con todas las dependencias necesarias. A continuación, se detallan los pasos para ejecutar el pipeline completo:

1️⃣ Construcción de la Imagen Personalizada
Construí la imagen de Docker a partir del Dockerfile, instalando las dependencias definidas en requirements.txt:
    docker build -t mi-airflow:latest .

2️⃣ Levantamiento del Entorno con Docker Compose
Iniciá el entorno de Airflow en segundo plano, construyendo los servicios si es necesario:
    docker-compose up -d --build

3️⃣ Ejecución del Pipeline
Una vez iniciado el entorno, Airflow ejecutará el DAG que orquesta el proceso ELT completo:
    Extracción de datos desde las fuentes (CSV o API).
    Almacenamiento en MinIO (capa RAW).
    Carga en PostgreSQL (capa STAGING).
    Transformación con dbt (capa CORE).

4️⃣ Finalización del Entorno
Para detener y eliminar los contenedores:
    docker-compose down
