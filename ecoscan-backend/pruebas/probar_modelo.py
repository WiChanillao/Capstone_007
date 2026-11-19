"""
EcoScan - Pruebas del sistema y del modelo YOLO (best.pt)

Con el backend encendido, hace tres cosas:
  1. Pruebas de humo: responden el backend y las rutas de MySQL?
  2. Pruebas del modelo: envia cada foto de la carpeta 'imagenes' a /predict,
     la compara con lo que habia realmente en la foto y mide el tiempo.
  3. (Opcional) Guarda cada analisis en la tabla 'inferencia' de MySQL.

Ejemplos:
  python probar_modelo.py
  python probar_modelo.py --guardar-bd
  python probar_modelo.py --yaml data.yaml --carpeta valid/images --etiquetas valid/labels

Las metricas son por IMAGEN (hay o no hay cada material en la foto).
No son mAP@50 (ese mide cajas) y no se deben mezclar con las del cuaderno.
"""
import argparse
import csv
import math
import mimetypes
import os
import re
import statistics
import sys
import time
import unicodedata
from datetime import datetime

import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
EXT_OK = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ID_MATERIAL = {"carton": 1, "plastico": 2, "aluminio": 3}  # igual que la tabla material
CLASES = ["carton", "aluminio", "plastico"]


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto)) if unicodedata.category(c) != "Mn")


def normalizar(clase):
    """Misma traduccion de clases que usa App.jsx. Devuelve un conjunto."""
    c = sin_tildes(clase).lower()
    out = set()
    if any(k in c for k in ("carton", "paper", "cardboard", "caja", "papel")):
        out.add("carton")
    if any(k in c for k in ("lata", "can", "aluminio", "metal")):
        out.add("aluminio")
    if any(k in c for k in ("plastico", "plastic", "botella", "pet", "hdpe")):
        out.add("plastico")
    return out


def parse_esperado(texto):
    """'carton+plastico' -> {'carton','plastico'}; 'ninguno' -> set(); vacio -> None (sin etiquetar)."""
    t = sin_tildes(texto or "").strip().lower()
    if t == "":
        return None
    if t in ("ninguno", "nada", "none", "-", "sin residuo"):
        return set()
    out = set()
    for parte in re.split(r"[+;|/]", t):
        parte = parte.strip()
        if parte:
            n = normalizar(parte)
            if not n:
                print(f"  AVISO: no entiendo la etiqueta '{parte}' (usa carton, aluminio, plastico o ninguno)")
            out |= n
    return out


def percentil(valores, p):
    v = sorted(valores)
    rango = max(1, math.ceil(p / 100 * len(v)))
    return v[rango - 1]


def tabla_md(encabezados, filas):
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "|".join(["---"] * len(encabezados)) + "|"]
    for f in filas:
        lineas.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(lineas)


# ----------------------------------------------------------------------
# 1. Pruebas de humo
# ----------------------------------------------------------------------
def pruebas_humo(base):
    revisiones = [
        ("Backend responde (GET /)", "/", None),
        ("Comunas", "/db/comunas", 9),
        ("Puntos limpios", "/db/puntos", 10),
        ("Habitos", "/db/habitos", 4),
        ("Banners", "/db/banners", 4),
        ("Simulador", "/db/simulador", 3),
        ("Materiales", "/db/materiales", 3),
        ("Instrucciones de Carton (material 1)", "/db/materiales/1/instrucciones", 6),
    ]
    filas = []
    for nombre, ruta, minimo in revisiones:
        t0 = time.perf_counter()
        try:
            r = requests.get(base + ruta, timeout=20)
        except requests.exceptions.RequestException:
            filas.append((nombre, "FALLA", "Sin conexion: esta encendido el backend?", "-"))
            if ruta == "/":
                return filas, False
            continue
        ms = (time.perf_counter() - t0) * 1000
        if r.status_code != 200:
            filas.append((nombre, "FALLA", f"HTTP {r.status_code} (MySQL encendido? datos cargados?)", f"{ms:.0f}"))
            continue
        try:
            data = r.json()
        except ValueError:
            filas.append((nombre, "FALLA", "Respuesta que no es JSON", f"{ms:.0f}"))
            continue

        if ruta == "/":
            ok = isinstance(data, dict) and data.get("status") == "ok"
            filas.append((nombre, "OK" if ok else "FALLA", f"modelo activo: {data.get('modelo_activo')}", f"{ms:.0f}"))
            continue

        n = len(data)
        ok = n >= minimo
        detalle = f"{n} filas (se esperaban {minimo} o mas)"
        if ok and ruta == "/db/simulador":
            con_factores = all(float(f.get("agua_litros", 0)) > 0 for f in data)
            ok = con_factores
            detalle += "; factores cargados" if con_factores else "; FACTORES EN CERO"
        if ok and ruta == "/db/puntos":
            con_mat = all(f.get("materiales") for f in data)
            ok = con_mat
            detalle += "; todos con materiales" if con_mat else "; hay puntos SIN materiales"
        filas.append((nombre, "OK" if ok else "FALLA", detalle, f"{ms:.0f}"))
    return filas, True


def pruebas_borde(base):
    """Casos limite del endpoint /predict."""
    filas = []

    def evaluar(nombre, resp, exito):
        c = resp.status_code
        if 400 <= c < 500:
            filas.append((nombre, "OK", f"HTTP {c}: error controlado"))
        elif c >= 500:
            filas.append((nombre, "REVISAR", f"HTTP {c}: el backend falla sin avisar bien (agregar manejo de errores)"))
        else:
            filas.append((nombre, "REVISAR", f"HTTP {c}: {exito}"))

    try:
        r = requests.post(base + "/predict", files={"file": ("texto.jpg", b"esto no es una imagen", "image/jpeg")}, timeout=30)
        evaluar("Archivo que no es imagen", r, "acepto un archivo invalido")
        r = requests.post(base + "/predict", timeout=30)
        evaluar("Peticion sin archivo", r, "acepto una peticion vacia")
    except requests.exceptions.RequestException as e:
        filas.append(("Casos limite", "FALLA", f"Sin conexion: {e}"))
    return filas


# ----------------------------------------------------------------------
# 2. Pruebas del modelo
# ----------------------------------------------------------------------
def cargar_esperados(args, imagenes):
    """Devuelve (dict imagen -> conjunto esperado o None, descripcion del origen)."""
    esperados = {}
    if args.yaml:
        import yaml  # viene con ultralytics

        with open(args.yaml, encoding="utf-8") as f:
            nombres = yaml.safe_load(f)["names"]
        nombres = {int(k): v for k, v in nombres.items()} if isinstance(nombres, dict) else dict(enumerate(nombres))
        for img in imagenes:
            stem = os.path.splitext(os.path.basename(img))[0]
            txt = os.path.join(args.etiquetas or os.path.dirname(img), stem + ".txt")
            if os.path.exists(txt):
                clases = set()
                with open(txt, encoding="utf-8") as f:
                    for linea in f:
                        p = linea.split()
                        if p:
                            clases |= normalizar(nombres[int(float(p[0]))])
                esperados[img] = clases
            else:
                esperados[img] = None
        return esperados, "etiquetas YOLO (.txt)"

    if os.path.exists(args.csv):
        with open(args.csv, encoding="utf-8-sig", newline="") as f:
            contenido = f.read()
        delim = ";" if ";" in contenido.splitlines()[0] else ","
        por_nombre = {}
        for fila in csv.DictReader(contenido.splitlines(), delimiter=delim):
            por_nombre[(fila.get("imagen") or "").strip()] = parse_esperado(fila.get("esperado"))
        for img in imagenes:
            esperados[img] = por_nombre.get(os.path.basename(img))
        return esperados, os.path.basename(args.csv)

    # No hay etiquetas: se crea una plantilla para llenar
    with open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["imagen", "esperado"])
        for img in imagenes:
            w.writerow([os.path.basename(img), ""])
    print(f"  Se creo la plantilla {args.csv}. Llenala (carton, aluminio, plastico, ninguno; varios con +) y vuelve a ejecutar.")
    return {img: None for img in imagenes}, None


def predecir(base, ruta):
    with open(ruta, "rb") as f:
        datos = f.read()
    mime = mimetypes.guess_type(ruta)[0] or "image/jpeg"
    t0 = time.perf_counter()
    r = requests.post(base + "/predict", files={"file": (os.path.basename(ruta), datos, mime)}, timeout=120)
    ms = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    detecciones = r.json().get("detecciones", [])
    conf = {}
    for d in detecciones:
        for c in normalizar(d.get("clase", "")):
            conf[c] = max(conf.get(c, 0.0), float(d.get("confianza", 0)))
    return conf, ms, len(detecciones)


def clasificar_resultado(conf, umbral):
    """Regla de la tabla inferencia: OK exige material; si no, CONFIANZA_BAJA sin material."""
    if conf:
        principal = max(conf, key=conf.get)
        if conf[principal] >= umbral:
            return "OK", principal
    return "CONFIANZA_BAJA", None


def guardar_inferencia(base, resultado, material, conf, ms):
    cuerpo = {
        "id_sesion": None,
        "id_material": ID_MATERIAL[material] if material else None,
        "resultado": resultado,
        "confianza": round(max(conf.values()), 4) if conf else None,
        "latencia_ms": int(round(ms)),
    }
    r = requests.post(base + "/db/inferencias", json=cuerpo, timeout=20)
    return r.status_code


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8000", help="direccion del backend")
    ap.add_argument("--carpeta", default=os.path.join(AQUI, "imagenes"), help="carpeta con las fotos")
    ap.add_argument("--csv", default=os.path.join(AQUI, "etiquetas.csv"), help="archivo con lo que hay en cada foto")
    ap.add_argument("--yaml", help="data.yaml de Roboflow (para leer etiquetas YOLO .txt)")
    ap.add_argument("--etiquetas", help="carpeta con los .txt YOLO (por defecto, la misma de las fotos)")
    ap.add_argument("--umbral", type=float, default=0.40, help="confianza minima para resultado OK (defecto 0.40)")
    ap.add_argument("--guardar-bd", action="store_true", help="guardar cada analisis en la tabla inferencia")
    args = ap.parse_args()
    base = args.url.rstrip("/")
    sello = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    informe = [f"# Informe de pruebas EcoScan - {datetime.now().strftime('%d-%m-%Y %H:%M')}", ""]

    # ---- 1. Humo
    print("\n[1/3] Pruebas de humo del sistema...")
    humo, hay_backend = pruebas_humo(base)
    informe += ["## 1. Pruebas de humo (backend y MySQL)", "", tabla_md(["Prueba", "Estado", "Detalle", "ms"], humo), ""]
    if not hay_backend:
        print("\n".join(f"  {a}: {b} - {c}" for a, b, c, _ in humo))
        print("\nNo se pudo conectar. Enciende el backend (python main.py) y vuelve a ejecutar.")
        sys.exit(1)

    print("[2/3] Casos limite de /predict...")
    borde = pruebas_borde(base)
    informe += ["## 2. Casos limite de /predict", "", tabla_md(["Prueba", "Estado", "Detalle"], borde), ""]

    # ---- 3. Modelo
    print("[3/3] Pruebas del modelo con fotos...")
    imagenes, omitidas = [], []
    if os.path.isdir(args.carpeta):
        for nombre in sorted(os.listdir(args.carpeta)):
            ext = os.path.splitext(nombre)[1].lower()
            if ext in EXT_OK:
                imagenes.append(os.path.join(args.carpeta, nombre))
            elif ext in (".heic", ".heif"):
                omitidas.append(nombre)
    if omitidas:
        print(f"  AVISO: se omitieron {len(omitidas)} fotos HEIC (conviertelas a JPG): {', '.join(omitidas[:5])}...")

    filas_img = []
    if not imagenes:
        print(f"  No hay fotos (jpg/png) en: {args.carpeta}")
        informe += ["## 3. Pruebas del modelo", "", f"No habia fotos en `{args.carpeta}`.", ""]
    else:
        esperados, origen = cargar_esperados(args, imagenes)
        print(f"  {len(imagenes)} fotos. Etiquetas: {origen or 'sin etiquetas'}")
        try:
            predecir(base, imagenes[0])  # calentamiento: la primera llamada es mas lenta y no se cuenta
        except Exception as e:
            print(f"  Fallo la primera prediccion: {e}")
            sys.exit(1)

        for i, img in enumerate(imagenes, 1):
            nombre = os.path.basename(img)
            esperado = esperados.get(img)
            try:
                conf, ms, n_det = predecir(base, img)
            except Exception as e:
                filas_img.append(dict(imagen=nombre, esperado=esperado, detectado=set(), conf={}, ms=None,
                                      estado="ERROR", resultado_bd="", detalle=str(e)[:60]))
                print(f"  ({i}/{len(imagenes)}) {nombre}: ERROR {e}")
                continue
            detectado = set(conf)
            if esperado is None:
                estado = "SIN_ETIQUETA"
            elif detectado == esperado:
                estado = "CORRECTO"
            elif detectado & esperado:
                estado = "PARCIAL"
            else:
                estado = "INCORRECTO"
            resultado, material = clasificar_resultado(conf, args.umbral)
            bd = ""
            if args.guardar_bd:
                try:
                    codigo = guardar_inferencia(base, resultado, material, conf, ms)
                    bd = f"{resultado} (HTTP {codigo})"
                except requests.exceptions.RequestException as e:
                    bd = f"ERROR {e}"
            filas_img.append(dict(imagen=nombre, esperado=esperado, detectado=detectado, conf=conf, ms=ms,
                                  estado=estado, resultado_bd=bd, detalle=""))
            print(f"  ({i}/{len(imagenes)}) {nombre}: {estado}  detectado={sorted(detectado) or 'nada'}  {ms:.0f} ms")

        validas = [f for f in filas_img if f["ms"] is not None]
        etiquetadas = [f for f in validas if f["esperado"] is not None]

        informe += ["## 3. Pruebas del modelo (por imagen)", "",
                    f"- Fotos probadas: {len(validas)} de {len(imagenes)} (con error: {len(imagenes) - len(validas)})",
                    f"- Fotos con etiqueta real: {len(etiquetadas)} (origen: {origen or 'ninguno'})",
                    "- Se envia cada foto una vez a `/predict`; la primera llamada de calentamiento no se cuenta.", ""]

        if etiquetadas:
            exactas = sum(1 for f in etiquetadas if f["estado"] == "CORRECTO")
            informe += [f"**Imagenes con resultado exacto: {exactas} de {len(etiquetadas)} "
                        f"({100 * exactas / len(etiquetadas):.1f}%)**", ""]
            filas_m = []
            for c in CLASES:
                tp = sum(1 for f in etiquetadas if c in f["esperado"] and c in f["detectado"])
                fp = sum(1 for f in etiquetadas if c not in f["esperado"] and c in f["detectado"])
                fn = sum(1 for f in etiquetadas if c in f["esperado"] and c not in f["detectado"])
                p = tp / (tp + fp) if tp + fp else None
                r = tp / (tp + fn) if tp + fn else None
                f1 = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
                fmt = lambda x: "n/a" if x is None else f"{x:.2f}"
                filas_m.append((c, tp, fp, fn, fmt(p), fmt(r), fmt(f1)))
            informe += [tabla_md(["Material", "Aciertos (TP)", "Falsas alarmas (FP)", "No detectados (FN)",
                                  "Precision", "Recall", "F1"], filas_m), ""]
            sin_res = [f for f in etiquetadas if not f["esperado"]]
            if sin_res:
                falsas = sum(1 for f in sin_res if f["detectado"])
                informe += [f"Fotos sin residuo: {len(sin_res)}; el modelo detecto algo en {falsas} de ellas.", ""]

        if validas:
            lat = [f["ms"] for f in validas]
            informe += ["### Latencia (ida y vuelta HTTP en este computador)", "",
                        tabla_md(["Promedio", "Mediana", "P95", "Minimo", "Maximo", "Menos de 100 ms"],
                                 [(f"{statistics.mean(lat):.0f} ms", f"{statistics.median(lat):.0f} ms",
                                   f"{percentil(lat, 95):.0f} ms", f"{min(lat):.0f} ms", f"{max(lat):.0f} ms",
                                   f"{100 * sum(1 for x in lat if x < 100) / len(lat):.0f}%")]), "",
                        "_Incluye subir la imagen, la inferencia y la respuesta. Depende del computador "
                        "donde corre el backend (CPU o GPU)._", ""]

        if args.guardar_bd:
            ok = sum(1 for f in filas_img if "HTTP 201" in f["resultado_bd"])
            informe += [f"Analisis guardados en MySQL (tabla inferencia): {ok} de {len(validas)}", ""]

        informe += ["### Detalle por foto", "",
                    tabla_md(["Foto", "Esperado", "Detectado (confianza)", "ms", "Estado"],
                             [(f["imagen"],
                               "-" if f["esperado"] is None else (", ".join(sorted(f["esperado"])) or "ninguno"),
                               ", ".join(f"{c} {v:.2f}" for c, v in sorted(f["conf"].items())) or "nada",
                               "-" if f["ms"] is None else f"{f['ms']:.0f}", f["estado"]) for f in filas_img]), ""]

    # ---- Salida
    carpeta_sal = os.path.join(AQUI, "resultados")
    os.makedirs(carpeta_sal, exist_ok=True)
    ruta_md = os.path.join(carpeta_sal, f"informe_{sello}.md")
    ruta_csv = os.path.join(carpeta_sal, f"fotos_{sello}.csv")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
    if filas_img:
        with open(ruta_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["imagen", "esperado", "detectado", "confianza_max", "latencia_ms", "estado", "guardado_bd"])
            for r in filas_img:
                w.writerow([r["imagen"],
                            "" if r["esperado"] is None else ("+".join(sorted(r["esperado"])) or "ninguno"),
                            "+".join(sorted(r["detectado"])),
                            f"{max(r['conf'].values()):.4f}" if r["conf"] else "",
                            "" if r["ms"] is None else f"{r['ms']:.0f}", r["estado"], r["resultado_bd"]])

    print("\n" + "=" * 60)
    print("\n".join(informe))
    print("=" * 60)
    print(f"Informe guardado en: {ruta_md}")
    if filas_img:
        print(f"Detalle por foto:    {ruta_csv}")


if __name__ == "__main__":
    main()
