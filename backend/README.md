# API Cursos - TP Final IDS

Backend Flask para la gestión de cursos universitarios.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # completar con tus datos de DB y token
```

Crear las tablas en MySQL:
```bash
mysql -u root -p tp_final_ids < db_cursos.sql
```

Correr la app:
```bash
python app.py
```

La API queda en `http://localhost:5000`

## Autenticación

Todos los endpoints requieren el header:
```
Authorization: Bearer <token>
```
El token se define en `.env` como `API_TOKEN`.

## Endpoints

### Cursos (ABM)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos` | Listar todos los cursos activos |
| GET | `/api/cursos/<id>` | Obtener un curso por ID |
| POST | `/api/cursos` | Crear un nuevo curso |
| PUT | `/api/cursos/<id>` | Actualizar un curso |
| DELETE | `/api/cursos/<id>` | Baja lógica de un curso |

### Inscripciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos/<id>/alumnos` | Listar alumnos del curso |
| POST | `/api/cursos/<id>/alumnos` | Inscribir un alumno |
| DELETE | `/api/cursos/<id>/alumnos/<id_alumno>` | Desinscribir un alumno |

## Ejemplos de body

### POST /api/cursos
```json
{
  "nombre": "Introducción al Desarrollo de Software",
  "descripcion": "Materia del primer año",
  "codigo": "IDS-2025-1",
  "anio": 2025,
  "cuatrimestre": "1",
  "id_profesor": 1
}
```

### POST /api/cursos/<id>/alumnos
```json
{
  "id_alumno": 5
}
```

## Archivos

```
api-cursos/
├── app.py            # Flask app, todas las rutas
├── db.py             # Conexión a MySQL
├── auth.py           # Decorador de autenticación por token
├── db_cursos.sql     # Tablas: cursos, alumnos, inscripciones
├── requirements.txt
├── .env.example
└── README.md
```
