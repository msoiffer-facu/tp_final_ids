# API Cursos - TP Final IDS

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # completar con tus datos si no usás docker
python root.py
```

Con Docker (BD ya levantada por el equipo):
```bash
docker-compose up -d   # levanta MySQL en puerto 3306
python root.py
```

La API corre en `http://localhost:5000/api`

---

## Endpoints

### Cursos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos` | Listar todos los cursos |
| GET | `/api/cursos/<id>` | Obtener un curso |
| POST | `/api/cursos` | Crear curso |
| PUT | `/api/cursos/<id>` | Actualizar curso |
| DELETE | `/api/cursos/<id>` | Eliminar curso |

### Alumnos del curso

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos/<id>/alumnos` | Listar alumnos inscriptos |
| POST | `/api/cursos/<id>/alumnos` | Inscribir alumno |
| DELETE | `/api/cursos/<id>/alumnos/<alumno_id>` | Desinscribir alumno |

### Clases presenciales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos/<id>/clases` | Listar clases del curso |
| POST | `/api/cursos/<id>/clases` | Agregar clase |
| DELETE | `/api/cursos/<id>/clases/<clase_id>` | Eliminar clase |

### Equipos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/cursos/<id>/equipos` | Listar equipos del curso |
| POST | `/api/cursos/<id>/equipos` | Crear equipo |
| GET | `/api/cursos/<id>/equipos/<equipo_id>/alumnos` | Alumnos del equipo |
| POST | `/api/cursos/<id>/equipos/<equipo_id>/alumnos` | Agregar alumno al equipo |
| DELETE | `/api/cursos/<id>/equipos/<equipo_id>/alumnos/<alumno_id>` | Quitar alumno del equipo |

---

## Ejemplos de body

### POST /api/cursos
```json
{
  "nombre": "Introducción al Desarrollo de Software",
  "cuatrimestre": "1",
  "anio": 2025,
  "modificacion": "ninguna"
}
```

### POST /api/cursos/<id>/alumnos
```json
{ "alumno_id": 3 }
```

### POST /api/cursos/<id>/clases
```json
{ "fecha": "2025-04-10 08:00:00" }
```

### POST /api/cursos/<id>/equipos
```json
{
  "nombre": "Grupo 1",
  "descripcion": "Equipo del TP Final"
}
```

### POST /api/cursos/<id>/equipos/<equipo_id>/alumnos
```json
{ "alumno_id": 5 }
```

---

## Archivos

```
api-cursos/
├── root.py          # Entry point, registra blueprints
├── cursos.py        # Todos los endpoints de cursos
├── db_cursos.py     # Conexión a MySQL
├── requirements.txt
├── .env.example
└── README.md
```
