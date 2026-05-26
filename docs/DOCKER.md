# Levantar MySQL con Docker

Este archivo explica cómo levantar un contenedor MySQL que inicializa la base de datos usando `db.sql`.

Pasos:

1. Desde la raíz del workspace (donde está `docker-compose.yml`) ejecutar:

```bash
docker compose up -d
```

2. Ver logs si hace falta:

```bash
docker compose logs -f db
```

3. Conectarse con el cliente `mysql`:

```bash
# conexión local desde la máquina host
mysql -h 127.0.0.1 -P 3306 -u tp_final_user -ppro_final_pass tp_final_db
```

O usando `docker exec`:

```bash
docker exec -it tp_final_db mysql -u root -proot_pass tp_final_db
```

Notas:

- El archivo `db.sql` que se usará para inicializar está en [tp_final_ids/backend/db.sql](tp_final_ids/backend/db.sql).
- Si necesitas cambiar credenciales, edita [docker-compose.yml](docker-compose.yml) antes de levantarlo.
