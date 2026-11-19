"""Pruebas unitarias del cálculo automático de impacto (REC-15 / REC-115)."""
import pytest
from fastapi import HTTPException

import rutas_db


FACTORES = [
    {"id_item": 1, "agua_litros": "3.000", "co2_kg": "0.0800", "residuos_kg": "0.0300"},
    {"id_item": 2, "agua_litros": "2.000", "co2_kg": "0.1700", "residuos_kg": "0.0150"},
    {"id_item": 3, "agua_litros": "12.000", "co2_kg": "0.2500", "residuos_kg": "0.1200"},
]


def test_sin_tildes():
    assert rutas_db._sin_tildes("Cartón y Papel") == "carton y papel"
    assert rutas_db._sin_tildes(None) == ""


def test_numero():
    assert rutas_db._numero("3.5") == 3.5
    assert rutas_db._numero(None) == 0.0
    assert rutas_db._numero("x") == 0.0


def test_impacto_sin_escaneos(monkeypatch):
    consultas = []

    def falsa(sql, params=()):
        consultas.append((sql, params))
        return [] if "FROM escaneos" in sql else FACTORES

    monkeypatch.setattr(rutas_db, "consultar", falsa)
    r = rutas_db.impacto()

    assert r["escaneos"] == 0
    assert r["materiales"] == {"carton": 0, "aluminio": 0, "plastico": 0}
    assert r["impacto"] == {"agua_litros": 0, "co2_kg": 0, "residuos_kg": 0}
    assert r["equivalencias"] == {"duchas_5min": 0, "km_auto": 0}


def test_impacto_multi_material_e_historico(monkeypatch):
    filas = [
        {"materiales_detectados": "Plastico, Carton", "total_objetos": 2,
         "cant_carton": 0, "cant_aluminio": 0, "cant_plastico": 0},
        {"materiales_detectados": "Aluminio", "total_objetos": 1,
         "cant_carton": 0, "cant_aluminio": 1, "cant_plastico": 0},
        {"materiales_detectados": "Carton", "total_objetos": 2,
         "cant_carton": 2, "cant_aluminio": 0, "cant_plastico": 0},
        {"materiales_detectados": "Ninguno", "total_objetos": 0,
         "cant_carton": 0, "cant_aluminio": 0, "cant_plastico": 0},
    ]
    monkeypatch.setattr(
        rutas_db, "consultar",
        lambda sql, params=(): filas if "FROM escaneos" in sql else FACTORES,
    )
    r = rutas_db.impacto()

    assert r["escaneos"] == 4
    assert r["materiales"] == {"carton": 3, "aluminio": 1, "plastico": 1}
    assert r["impacto"]["agua_litros"] == 41.0
    assert r["impacto"]["co2_kg"] == 1.0
    assert r["impacto"]["residuos_kg"] == 0.4
    assert r["equivalencias"] == {"duchas_5min": 0.7, "km_auto": 7.5}


def test_impacto_filtra_por_sesion(monkeypatch):
    vistos = []

    def falsa(sql, params=()):
        vistos.append((sql, params))
        return [] if "FROM escaneos" in sql else FACTORES

    monkeypatch.setattr(rutas_db, "consultar", falsa)
    rutas_db.impacto(id_sesion="sesion-prueba")

    sql, params = vistos[0]
    assert "id_sesion = %s" in sql
    assert params == (30, "sesion-prueba")


def test_ejecutar_mapea_error_de_datos(monkeypatch):
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, *args):
            raise rutas_db.pymysql.MySQLError(1452, "FK inválida")

    class Conexion:
        def cursor(self):
            return Cursor()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(rutas_db.pymysql, "connect", lambda **kw: Conexion())
    with pytest.raises(HTTPException) as error:
        rutas_db.ejecutar("INSERT INTO x VALUES (%s)", (1,))
    assert error.value.status_code == 400
    assert "FK inválida" in error.value.detail


@pytest.mark.asyncio
async def test_reporte_csv(monkeypatch):
    monkeypatch.setattr(
        rutas_db, "consultar",
        lambda sql="", params=(): [
            {"mes": "2026-11", "material": "Cartón y Papel", "resultado": "OK",
             "total": 3, "confianza_promedio_pct": "80.5", "latencia_promedio_ms": "110.3"}
        ],
    )
    respuesta = rutas_db.reporte_inferencias_csv()
    partes = []
    async for parte in respuesta.body_iterator:
        partes.append(parte)
    cuerpo = "".join(str(p) for p in partes)
    assert "mes,material,resultado,total" in cuerpo
    assert "2026-11,Cartón y Papel,OK,3" in cuerpo
