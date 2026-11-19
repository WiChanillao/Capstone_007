"""Inicializa MySQL de forma idempotente usando los SQL versionados del repo.

Se ejecuta desde run.ps1 / run.sh con el intérprete del venv del backend.
Nunca borra datos: si la tabla `escaneos` ya tiene filas, no hace nada.
"""
import os
import sys
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parent.parent
INIT_DIR = ROOT / "docker" / "mysql" / "init"


def cargar_env():
    ruta = ROOT / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def conectar(sin_db=True):
    kwargs = dict(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "admin"),
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
        autocommit=True,
    )
    if not sin_db:
        kwargs["database"] = os.getenv("MYSQL_DB", "ecoscan")
    return pymysql.connect(**kwargs)


def ejecutar_sql(conn, ruta):
    sql = ruta.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
        while cur.nextset():
            pass
    print(f"  SQL aplicado: {ruta.relative_to(ROOT)}")


def main():
    cargar_env()
    db = os.getenv("MYSQL_DB", "ecoscan")
    print(f"MySQL: {os.getenv('MYSQL_HOST','localhost')}:{os.getenv('MYSQL_PORT','3306')} / {db}")

    conn = conectar(sin_db=True)
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS `" + db + "` CHARACTER SET utf8mb4")
        conn.select_db(db)
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'escaneos'")
            existe = cur.fetchone() is not None
            filas = 0
            if existe:
                cur.execute("SELECT COUNT(*) FROM escaneos")
                filas = cur.fetchone()[0]

        if existe and filas > 0:
            print(f"  BD ya inicializada: {filas} escaneos. No se modifica nada.")
            return 0

        if not existe:
            print("  Creando esquema...")
            ejecutar_sql(conn, INIT_DIR / "01_schema.sql")
        else:
            print("  Esquema presente; cargando solo datos semilla...")
        print("  Cargando datos semilla (48 escaneos de demostración)...")
        ejecutar_sql(conn, INIT_DIR / "02_seed.sql")

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM escaneos")
            print(f"  Verificación: {cur.fetchone()[0]} escaneos, MySQL listo.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR al inicializar MySQL: {exc}", file=sys.stderr)
        sys.exit(1)
