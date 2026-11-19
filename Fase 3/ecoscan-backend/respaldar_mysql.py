"""Respaldo diario de MySQL para REC-118 (RPO ≤ 24 h).

Uso:
  python respaldar_mysql.py

Variables de entorno opcionales: MYSQL_HOST, MYSQL_PORT, MYSQL_USER,
MYSQL_PASSWORD, MYSQL_DB, DIRECTORIO_BACKUPS.
El script no programa la tarea por sí solo: eso depende del servidor.
"""
import gzip
import os
import subprocess
from datetime import datetime
from pathlib import Path

host = os.getenv("MYSQL_HOST", "localhost")
port = os.getenv("MYSQL_PORT", "3306")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "admin")
db = os.getenv("MYSQL_DB", "ecoscan")
destino = Path(os.getenv("DIRECTORIO_BACKUPS", Path(__file__).parent / "backups"))
destino.mkdir(parents=True, exist_ok=True)

nombre = f"{db}_{datetime.now():%Y-%m-%d}.sql.gz"
archivo = destino / nombre

# REC-118: en Windows mysqldump no suele estar en PATH; se busca en la ruta
# estándar de MySQL Server 8.0 antes de fallar.
mysqldump = "mysqldump"
if os.name == "nt" and not any(
    os.path.exists(os.path.join(carpeta, "mysqldump.exe"))
    for carpeta in os.getenv("PATH", "").split(os.pathsep) if carpeta
):
    candidato = Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe")
    if candidato.exists():
        mysqldump = str(candidato)

comando = [
    mysqldump,
    f"--host={host}",
    f"--port={port}",
    f"--user={user}",
    f"--password={password}",
    "--single-transaction",
    "--routines",
    "--triggers",
    db,
]

with archivo.open("wb") as salida:
    with gzip.GzipFile(fileobj=salida, mode="wb") as comprimido:
        proceso = subprocess.run(comando, stdout=comprimido, stderr=subprocess.PIPE)
        comprimido.flush()

if proceso.returncode != 0 or archivo.stat().st_size == 0:
    archivo.unlink(missing_ok=True)
    raise SystemExit(f"Falló el respaldo: {proceso.stderr.decode(errors='replace')}")

print(f"RESPALDO_OK {archivo} {archivo.stat().st_size} bytes")
