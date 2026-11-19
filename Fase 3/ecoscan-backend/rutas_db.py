"""Rutas /db/... para EcoLearn Chile (FastAPI + MySQL ecoscan).

Expone los datos reales de las 14 tablas cargadas en MySQL para los 4 módulos.
Se usa pymysql (ya instalado en el entorno del proyecto).
"""
import os
import csv
import io
import uuid
import unicodedata
from typing import Optional

import pymysql
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/db", tags=["mysql"])

DB_CONFIG = dict(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "admin"),
    database=os.getenv("MYSQL_DB", "ecoscan"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


def consultar(sql, params=()):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def ejecutar(sql, params=()):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    except pymysql.MySQLError as e:
        if e.args and e.args[0] in (1452, 1062, 1048, 3819, 4025):
            raise HTTPException(status_code=400, detail=f"Dato inválido: {e.args[1]}")
        raise
    finally:
        conn.close()


# ---------- Escáner IA ----------
@router.get("/materiales")
def materiales():
    return consultar(
        """SELECT m.id_material, m.nombre, c.nombre AS contenedor, c.color
           FROM material m LEFT JOIN contenedor c ON c.id_contenedor = m.id_contenedor"""
    )


@router.get("/materiales/{id_material}/instrucciones")
def instrucciones(id_material: int):
    return consultar(
        """SELECT i.id_instruccion, i.tipo, p.orden, p.texto
           FROM instruccion i
           LEFT JOIN paso_instruccion p ON p.id_instruccion = i.id_instruccion
           WHERE i.id_material = %s ORDER BY i.tipo, p.orden""",
        (id_material,),
    )


@router.get("/banners")
def banners():
    return consultar("SELECT * FROM banner_impacto")


class Inferencia(BaseModel):
    id_sesion: Optional[str] = None
    id_material: Optional[int] = None
    resultado: str  # OK | BORROSA | CONFIANZA_BAJA
    confianza: Optional[float] = None
    latencia_ms: int


@router.post("/inferencias", status_code=201)
def guardar_inferencia(d: Inferencia):
    ejecutar(
        """INSERT INTO inferencia
           (id_inferencia, id_sesion, id_material, resultado, confianza, latencia_ms)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (str(uuid.uuid4()), d.id_sesion, d.id_material, d.resultado, d.confianza, d.latencia_ms),
    )
    return {"ok": True}


@router.get("/reporte/inferencias.csv")
def reporte_inferencias_csv():
    """Reporte mensual real de inferencias por material (REC-117)."""
    filas = consultar(
        """SELECT DATE_FORMAT(i.fecha_hora, '%%Y-%%m') AS mes,
                  COALESCE(m.nombre, 'Sin material') AS material,
                  i.resultado,
                  COUNT(*) AS total,
                  ROUND(AVG(i.confianza) * 100, 1) AS confianza_promedio_pct,
                  ROUND(AVG(i.latencia_ms), 1) AS latencia_promedio_ms
           FROM inferencia i
           LEFT JOIN material m ON m.id_material = i.id_material
           GROUP BY mes, material, i.resultado
           ORDER BY mes DESC, material, i.resultado"""
    )
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["mes", "material", "resultado", "total",
                       "confianza_promedio_pct", "latencia_promedio_ms"])
    for fila in filas:
        escritor.writerow([fila.get("mes"), fila.get("material"), fila.get("resultado"),
                           fila.get("total"), fila.get("confianza_promedio_pct"),
                           fila.get("latencia_promedio_ms")])
    return StreamingResponse(
        iter([salida.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="reporte_inferencias.csv"'},
    )


# ---------- Puntos Limpios RM ----------
@router.get("/comunas")
def comunas():
    return consultar("SELECT * FROM comuna ORDER BY nombre")


@router.get("/puntos")
def puntos(comuna: Optional[int] = None):
    return consultar(
        """SELECT p.id_punto, p.nombre, p.direccion, p.horario, co.nombre AS comuna,
                  p.lat, p.lon, p.fuente, p.nota, p.coords_aproximadas,
                   GROUP_CONCAT(m.nombre SEPARATOR ', ') AS materiales
           FROM punto_limpio p
           JOIN comuna co ON co.id_comuna = p.id_comuna
           LEFT JOIN punto_material pm ON pm.id_punto = p.id_punto
           LEFT JOIN material m ON m.id_material = pm.id_material
           WHERE (%s IS NULL OR p.id_comuna = %s)
           GROUP BY p.id_punto, p.nombre, p.direccion, p.horario, co.nombre,
                    p.lat, p.lon, p.fuente, p.nota, p.coords_aproximadas""",
        (comuna, comuna),
    )


# ---------- Eco-Simulador RM ----------
@router.get("/simulador")
def simulador():
    return consultar("SELECT * FROM item_simulador")


# Factores reales de la BD: id_item 1=plástico, 2=aluminio, 3=cartón.
_FACTORES_POR_ITEM = {1: "plastico", 2: "aluminio", 3: "carton"}


def _numero(valor):
    try:
        return float(valor or 0)
    except (TypeError, ValueError):
        return 0.0


def _sin_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(texto or "").lower())
        if not unicodedata.combining(c)
    )


@router.get("/impacto")
def impacto(id_sesion: Optional[str] = None, dias: int = 30):
    """Impacto calculado solo desde escaneos reales de MySQL.

    No hay valores por defecto ni entradas manuales: sin escaneos, todo es 0.
    Si se envía id_sesion, solo cuentan las fotos de esa sesión anónima.
    """
    where = ["fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)"]
    params = [dias]
    if id_sesion:
        where.append("id_sesion = %s")
        params.append(id_sesion)
    sql_where = " WHERE " + " AND ".join(where)

    try:
        filas = consultar(
            "SELECT materiales_detectados, total_objetos, "
            "COALESCE(cant_carton, 0) AS cant_carton, "
            "COALESCE(cant_aluminio, 0) AS cant_aluminio, "
            "COALESCE(cant_plastico, 0) AS cant_plastico "
            "FROM escaneos" + sql_where,
            tuple(params),
        )
    except Exception:
        # Compatibilidad con una BD todavía no migrada.
        filas = consultar(
            "SELECT materiales_detectados, total_objetos, "
            "0 AS cant_carton, 0 AS cant_aluminio, 0 AS cant_plastico "
            "FROM escaneos" + sql_where,
            tuple(params),
        )

    materiales = {"carton": 0, "aluminio": 0, "plastico": 0}
    for fila in filas:
        c = int(fila.get("cant_carton") or 0)
        a = int(fila.get("cant_aluminio") or 0)
        p = int(fila.get("cant_plastico") or 0)
        # Filas históricas: se reconstruye el conteo desde el texto detectado.
        if c + a + p == 0:
            texto = _sin_tildes(fila.get("materiales_detectados"))
            if "carton" in texto:
                c = 1
            if "aluminio" in texto:
                a = 1
            if "plastico" in texto:
                p = 1
        materiales["carton"] += c
        materiales["aluminio"] += a
        materiales["plastico"] += p

    items = consultar(
        "SELECT id_item, agua_litros, co2_kg, residuos_kg FROM item_simulador ORDER BY id_item"
    )
    factores = {}
    for item in items:
        clave = _FACTORES_POR_ITEM.get(int(item["id_item"]))
        if clave:
            factores[clave] = {
                "agua_litros": _numero(item["agua_litros"]),
                "co2_kg": _numero(item["co2_kg"]),
                "residuos_kg": _numero(item["residuos_kg"]),
            }

    def factor(clave, campo):
        return factores.get(clave, {}).get(campo, 0.0)

    agua = sum(materiales[m] * factor(m, "agua_litros") for m in materiales)
    co2 = sum(materiales[m] * factor(m, "co2_kg") for m in materiales)
    residuos = sum(materiales[m] * factor(m, "residuos_kg") for m in materiales)

    return {
        "fuente": "MySQL ecoscan.escaneos + item_simulador",
        "ventana_dias": dias,
        "id_sesion": id_sesion,
        "escaneos": len(filas),
        "materiales": materiales,
        "impacto": {
            "agua_litros": round(agua, 2),
            "co2_kg": round(co2, 2),
            "residuos_kg": round(residuos, 2),
        },
        "equivalencias": {
            "duchas_5min": round(agua / 60, 1),
            "km_auto": round(co2 * 7.5, 1),
        },
        "factores": factores,
    }


# ---------- Desafío Verde RM ----------
@router.get("/habitos")
def habitos():
    return consultar("SELECT * FROM habito")


@router.post("/mantenimiento/retencion")
def aplicar_retencion():
    """Anonimiza a los 6 meses y elimina a los 12 meses (REC-119)."""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE inferencia SET id_sesion = NULL "
                "WHERE id_sesion IS NOT NULL AND fecha_hora < DATE_SUB(NOW(), INTERVAL 6 MONTH)"
            )
            anonimizadas = cur.rowcount
            cur.execute(
                "DELETE FROM inferencia WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL 12 MONTH)"
            )
            eliminadas_inf = cur.rowcount
            cur.execute(
                "DELETE FROM escaneos WHERE fecha < DATE_SUB(NOW(), INTERVAL 12 MONTH)"
            )
            eliminadas_esc = cur.rowcount
        conn.commit()
        return {
            "anonimizadas_6_meses": anonimizadas,
            "inferencias_eliminadas_12_meses": eliminadas_inf,
            "escaneos_eliminados_12_meses": eliminadas_esc,
        }
    finally:
        conn.close()


@router.post("/sesiones", status_code=201)
def crear_sesion():
    id_sesion = str(uuid.uuid4())
    ejecutar("INSERT INTO sesion (id_sesion) VALUES (%s)", (id_sesion,))
    return {"id_sesion": id_sesion}


@router.get("/sesiones/{id_sesion}/habitos")
def habitos_sesion(id_sesion: str):
    filas = consultar(
        "SELECT id_habito, marcado FROM habito_cumplido WHERE id_sesion = %s", (id_sesion,)
    )
    return [{"id_habito": f["id_habito"], "marcado": bool(f["marcado"])} for f in filas]


class Marca(BaseModel):
    marcado: bool


@router.put("/sesiones/{id_sesion}/habitos/{id_habito}")
def marcar_habito(id_sesion: str, id_habito: int, m: Marca):
    ejecutar(
        """INSERT INTO habito_cumplido (id_sesion, id_habito, marcado) VALUES (%s,%s,%s)
           ON DUPLICATE KEY UPDATE marcado = VALUES(marcado)""",
        (id_sesion, id_habito, int(m.marcado)),
    )
    return {"ok": True}
