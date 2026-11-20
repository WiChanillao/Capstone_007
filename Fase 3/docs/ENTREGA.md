# Entrega final para evaluación — EcoLearn Chile / EcoScan

Guía de entrega: qué es el proyecto, cómo levantarlo, cómo ejecutar las pruebas y
dónde está la evidencia verificable de cada requisito. Todo el contenido está
dentro de este repositorio de GitHub.

> **Actualizado 20-11-2026:** el alcance canónico está en
> [`DOCUMENTACION_GENERAL.md`](DOCUMENTACION_GENERAL.md) y el contraste de los
> 161 issues en [`AUDITORIA_JIRA.md`](AUDITORIA_JIRA.md). Los conteos de pruebas
> de esta guía corresponden a la evidencia local histórica; los conteos vigentes
> por fecha están en la documentación general.

## 1. Resumen del proyecto

EcoLearn Chile es una PWA con **Menú Principal + 4 módulos** (Escáner IA,
Puntos Limpios RM, Eco-Simulador RM y Desafío Verde RM). El impacto está
integrado en el simulador, no es una pestaña separada. El usuario sube una foto de un residuo,
un modelo **YOLO11n** (`best.pt`) detecta **Aluminio, Cartón o Plástico**, el
backend FastAPI devuelve instrucciones de reciclaje y guarda el análisis en
**MySQL 8**. Los indicadores de impacto y el desafío verde se calculan
automáticamente desde la base de datos; no hay sliders ni escenarios manuales.

- **Stack:** React 19 + Vite + Tailwind (PWA) · FastAPI + Ultralytics · MySQL 8 ·
  Docker Compose con healthchecks · CI con GitHub Actions.
- **Métrica oficial:** `mAP@50 = 0.562` en validación (61 imágenes). La meta
  `0.65` **no** está alcanzada y así se reporta en la presentación.
- **Estado:** entregable académico, con deuda explícita documentada en
  [`DECISIONES.md`](DECISIONES.md) (autenticación, dominio de producción, UAT/SUS
  y rotación de clave histórica).

## 2. Levantar desde cero (3 comandos)

Ejecutar **desde `Fase 3/`** con Docker Desktop en ejecución:

```bash
copy .env.example .env
docker compose up --build -d
docker compose ps
```

Antes del segundo comando, editar `.env` y definir `MYSQL_ROOT_PASSWORD` con una
clave propia. El compose no acepta defaults: si falta, falla con
`Definir MYSQL_ROOT_PASSWORD en .env`. Los tres servicios deben aparecer
`healthy`. La app queda en **http://localhost:5173/** y la API en
**http://127.0.0.1:8000/** (Docs: `/docs`).

Puertos publicados, todos ligados a `127.0.0.1` de acuerdo con
[`../docker-compose.yml`](../docker-compose.yml):

| Servicio | Publicado | Interno |
|---|---|---|
| MySQL | `127.0.0.1:3307` | `3306` |
| Backend | `127.0.0.1:8000` | `8000` |
| Frontend | `127.0.0.1:5173` | `8080` (Nginx no root) |

Para apagar sin borrar datos: `docker compose down`. **`docker compose down -v` elimina los volúmenes** y sólo se usa si se decide expresamente reconstruir desde cero.

## 3. Ejecutar las pruebas

```bash
# Backend (22 pruebas en evidencia local; 36 en auditoría/CI posterior)
cd ecoscan-backend && venv\Scripts\python.exe -m pytest -q

# Frontend (24 pruebas unitarias tras PR 2)
cd ../ecoscan-frontend && npm run test:unit

# Extremo a extremo (4 pruebas Cypress)
npm run test:e2e
```

Los tests del backend definen su propia `MYSQL_PASSWORD` en
`ecoscan-backend/tests/conftest.py`: no dependen del `.env` ni de valores por
defecto. Resultado real guardado en
[`evidencia/pytest.txt`](evidencia/pytest.txt).

## 4. Requisitos Docker y seguridad → evidencia

| Requisito | Evidencia |
|---|---|
| Los 3 servicios arrancan y están `healthy` | [`evidencia/docker-compose-ps.txt`](evidencia/docker-compose-ps.txt), [sección 8](evidencia/EVIDENCIA_DOCKER.md) |
| Healthchecks declarados en el compose | [sección 3](evidencia/EVIDENCIA_DOCKER.md), [`../docker-compose.yml`](../docker-compose.yml) |
| Sin contraseña por defecto (`MYSQL_ROOT_PASSWORD` obligatoria) | [sección 6](evidencia/EVIDENCIA_DOCKER.md), [`../README.md`](../README.md) |
| `MYSQL_PASSWORD` obligatoria también en el código Python | [sección 7](evidencia/EVIDENCIA_DOCKER.md), [`../ecoscan-backend/main.py`](../ecoscan-backend/main.py) |
| Contenedores no root (`appuser`, `nginx`) | [`evidencia/usuarios_no_root.txt`](evidencia/usuarios_no_root.txt), [sección 6](evidencia/EVIDENCIA_DOCKER.md) |
| Puertos ligados a `127.0.0.1` y frontend `5173:8080` | [`evidencia/docker-compose-ps.txt`](evidencia/docker-compose-ps.txt) |
| `.env` y `.env.*` fuera del repo y de las imágenes | [sección 6](evidencia/EVIDENCIA_DOCKER.md), [`../.env.example`](../.env.example) |
| `/health` responde 200 con MySQL conectado y `best.pt` | [`evidencia/health.txt`](evidencia/health.txt) |
| Frontend responde 200 en `127.0.0.1:5173` | [`evidencia/frontend.txt`](evidencia/frontend.txt) |
| `/predict`: 10 MB, whitelist MIME, 8000×8000, `id_sesion`, 429 | [sección 7](evidencia/EVIDENCIA_DOCKER.md), [`../ecoscan-backend/tests/test_main.py`](../ecoscan-backend/tests/test_main.py) |
| Prueba desde cero (`down -v` + `up --build -d`) | [sección 8](evidencia/EVIDENCIA_DOCKER.md) |
| Captura real de Docker Desktop con los 3 contenedores | [`ESTRUCTURA_PROYECTO_DOCKER.png`](ESTRUCTURA_PROYECTO_DOCKER.png) |

El registro completo, ordenado por secciones y con comandos y resultados reales,
está en [`evidencia/EVIDENCIA_DOCKER.md`](evidencia/EVIDENCIA_DOCKER.md).

## 5. Enlaces de la entrega

- Guía completa del proyecto: [`README.md` de Fase 3](../README.md)
- Índice general del repositorio: [`README.md` raíz](../../README.md)
- Decisiones técnicas y limitaciones: [`DECISIONES.md`](DECISIONES.md)
- Evidencia Docker y de seguridad: [`evidencia/`](evidencia/)
- Matriz de pruebas oficial (Excel, 97 casos —6 Docker— + trazabilidad de 161 issues): [`pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx`](pruebas/MATRIZ_DE_PRUEBAS_EcoLearn_Oficial.xlsx)
- Plan de pruebas histórico (AC de 40 casos): [`pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx`](pruebas/PLAN_DE_PRUEBAS_EcoLearn.xlsx)
- Presentación final: [`presentacion/EcoLearn_Presentacion_Final_Fase3.pptx`](presentacion/EcoLearn_Presentacion_Final_Fase3.pptx)
- CRISP-DM y resultados: [`crisp-dm/`](crisp-dm/)
