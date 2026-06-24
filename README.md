# Plataforma Web de Gestión Universitaria

Este proyecto consiste en el desarrollo de una plataforma web de alcance completo para la administración y control de un curso universitario. El sistema integra funcionalidades esenciales para gestionar usuarios, alumnos, equipos de trabajo, registrar asistencias mediante códigos QR y generar reportes analíticos.

Desarrollado como **Proyecto Final** para la materia *Introducción al Desarrollo de Software* de la **Facultad de Ingeniería de la Universidad de Buenos Aires**.

---

##  Tecnologías Utilizadas

El sistema está dividido en dos componentes principales que respetan una arquitectura RESTful, comunicándose exclusivamente el frontend con el back mediante el JSONs:

* **Backend:** Aplicación desarrollada en **Python** utilizando el framework **Flask** y conectada una la base de datos MySQL.
* **Frontend:** Interfaz web desarrollada en **Python** con **Flask** que consume los servicios de la API backend.
* **Base de Datos:** **MySQL** con un script automatizado de creación/carga inicial.
* **Documentación:** Especificación de endpoints mediante **Swagger** e informacion detallada del proyecto en un documento pdf.

---

##  Alcance

La plataforma resuelve e implementa las siguientes características:

1. **Gestión de Usuarios y Seguridad:**
   * Acceso protegido mediante usuario y contraseña.
   * Autenticación y seguridad mandatoria en los endpoints de la API.
   * Registro y seguimiento detallado de actividad de los usuarios.

2. **Administración de Alumnos (ABM):**
   * Alta, Baja y Modificación de la información de los alumnos.
   * Importación masiva de datos de alumnos a partir de archivos externos en formato **CSV**.
   * Exportación de los datos de los alumnos en formato **PDF** o **CSV**

3. **Gestión de Evaluaciones y Notas:**
   * ABM integral de tipos de evaluación (parciales, parcialitos, Trabajos Prácticos, etc.).
   * Carga y centralización de calificaciones obtenidas por cada alumno en todos los esquemas evaluativos.

4. **Trabajo en Equipo:**
   * ABM de equipos de trabajo constituidos por un número "$n$" de alumnos.
   * Vinculación y asociación directa de los equipos a Trabajos Prácticos del curso.

5. **Sistema de Control de Asistencia:**
   * Generación y envío por correo electrónico de códigos **QR dinámicos**.
   * Los códigos generados tienen un solo uso y solo pueden ser utilizados por el alumno correspondiente y en la fecha exacta de la clase.

6. **Dashboard de Consultas e Informes (Exportación a PDF):**
   * Panel visual para listar información clave por pantalla.
   * Emisión y descarga de reportes formales en formato **PDF** y **CSV**:
     * Listado de alumnos.
     * Estadísticas analíticas de aprobación del curso.
     * Listado de los equipos de trabajo.

---

## 📁 Estructura del Repositorio

```text
├── backend/
│   ├── dbs/
│   ├── herramientas/
│   ├── routes/
│   ├── services/
│   ├── db.py
│   ├── docker-compose.yml
│   ├── tp_final_ids.sql
│   ├── auth.py
│   └── app_back.py
├── frontend/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── app_front.py
├── docs/
│   ├── DOCKER.md           # Documentacion de como iniciar el docker-compose
│   ├── documentacion.pdf
│   └── swagger.yaml
├── init.sh                 # Script Bash para instalación automatizada de dependencias y arranque del proyecto
├── .gitignore
├── README.md
└── requirements.txt
```
# Instalación y Configuración Local
El proyecto está  automatizado para que su arranque sea lo más sencilla posible.

## Requisitos Previos
* Tener instalado Python 3.x.

* Tener instalado y en ejecución Docker y Docker Compose.

## Pasos para la Inicialización
1. Clonación del repositorio de trabajo:
```bash
git clone https://github.com/msoiffer-facu/tp_final_ids.git
cd tp_final_ids
```
2. Configurar las variables de entorno:
Antes de ejecutar la aplicación, debés crear los archivos .env del backend y del frontend a partir de la plantilla provista para configurar las credenciales de la base de datos, claves secretas de Flask y puertos:
```bash
cd backend
cp .env.example .env
cd ..
cd frontend
cp .env.example .env
cd ..
```
(Opcional: Abrí el archivo .env con tu editor de texto si necesitás modificar algún parámetro local).

3. Ejecutar el script de automatización:
Dale permisos de ejecución al archivo init.sh y correlo. Este script se encargará de forma automática de:
* Crear el entorno virtual de Python.
* Descargar e instalar todas las dependencias del proyecto.
* Levantar el entorno de desarrollo y ejecutar en paralelo tanto el Frontend como el Backend.
```bash
chmod +x init.sh
source init.sh
```
4. Levantamiento de la Base de Datos (Docker):
La base de datos MySQL y los servicios del backend se gestionan a través de Docker. La base de datos se generará automáticamente si no existe, por lo que no requerís configuraciones manuales previas de servidores SQL.

# Integrantes del Equipo
El proyecto fue desarrollado de forma colaborativa por un equipo conformado por:
* **Agustín Bianchi** - Seccion de evaluaciones, backend del login y frontend del dashboard
* **Santiago Luka Picone** - Seccion de cursos
* **Alejo Hillar** - Seccion de profesores
* **Santiago Parodi** - Backend de reportes PDF y frontend de equipos
* **Francisco Vargas** - Primera version del backend de evaluaciones
* **Muriel Soiffer** - Seccion de asistencia, de la documentacion y revicion de codigo
* **Reginaldo S. Hinojosa Baldera** - Frontend de la vista de inicio y del backend de equipos
* **Tiziano N. Laffargue** - Backend de notas, frontend de alumnos y la conexion del front con el back del dashboard
* **Jonathan J. Tirado Vasquez** - Backend de alumnos y el frontend del login