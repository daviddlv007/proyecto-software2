\# Proyecto Django - Business Intelligence con IA



Este proyecto es una aplicación web desarrollada con \*\*Django\*\* y \*\*PostgreSQL\*\* para la gestión de datos, generación de dashboards y uso de inteligencia artificial.



---



\## Requisitos previos

Antes de clonar el proyecto, asegúrate de tener instalado:

\- \*\*Python 3.12+\*\*

\- \*\*PostgreSQL 17\*\*

\- \*\*pip\*\* (gestor de paquetes de Python)







----BASE DE DATOS-----

0. Instalar pgadmin 4(https://www.postgresql.org/ftp/pgadmin/pgadmin4/v9.8/windows/)



1. descargar PostgreSQL version 17 o superior (https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

Instalar y poner de contraseña openpg





2. Crear una base de datos en pgadmin 4 en la sección de PostgreSQL 17 llamada "software2\_DB"









-----CLONAR PROYECTO Y ARRANCAR-------
1. Clonar el repositorio con "git clone https://github.com/AlexRomanR/software2\_parcial.git"
2. Una vez clonado abrirlo con vs  code e ir a la terminar y poner:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    python -m venv venv
    .\\venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt

   
3. hacer:
   python manage.py makemigrations
   python manage.py migrate

   Si sale error de puerto, fijarse en C:\\Program Files\\PostgreSQL\\17\\data fijarse el archivo "postgresql.conf" y  buscar la palabra "port" y verificar el puerto que tiene y compáralo con el port de settings.py del proyecto(tiene que ser el mismo) si no es el mismo cambiar el de settings.py para que coincida con el otro e intentar de nuevo el python manage.py migrate

   y luego crear un superusuario
   python manage.py createsuperuser

   arrancar el servidor:
   python manage.py runserver

   en el navegador poner: http://127.0.0.1:8000


credencial de Django:
usuario: elmer
contraseña: MMMnnn1--
   



