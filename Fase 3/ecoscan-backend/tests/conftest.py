"""Configuración común de pytest.

Los tests no dependen de la contraseña real ni de un valor por defecto en el
código: definen su propia variable de entorno antes de importar `main` o
`rutas_db`, que ahora exigen MYSQL_PASSWORD.
"""
import os

os.environ["MYSQL_PASSWORD"] = "clave_solo_para_pruebas"
