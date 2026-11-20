# CI: Build antes que Pruebas unitarias (registro histórico; antiguo “REC-170”)

> **Actualización 20-11-2026:** `REC-170` **no existe** en Jira (máximo `REC-161`).
> El fix está mergeado en `main` desde PR 1 (`092fc88`) y el workflow ya usa
> `build → test:unit` con trigger `fix/**`. Ver
> [`../jira/MAPEO_CLAVES_REALES.md`](../jira/MAPEO_CLAVES_REALES.md).

Rama: `fix/ci-orden-pasos`, creada desde `main @ 62c73a2646e7d7b1cd4e420f88ba1706aa841d25`.
Sin `--force`, sin reescribir historial, sin tocar `main`.

## 1. Reproducción en clon limpio (sin cambios locales)

- Clon limpio desde `https://github.com/WiChanillao/Capstone_007.git`, checkout de `main`.
- `head=62c73a2646e7d7b1cd4e420f88ba1706aa841d25`.
- `node=v22.23.5`, `npm=11.19.0` (Node 22 real, igual que el workflow).
- Antes de `npm ci`: `dist_existe=False`. Después de `npm ci`: `dist=False`.
- `npm run test:unit` (sin `dist/`) falla:

```text
FAIL  src/sw.test.js [ src/sw.test.js ]
Error: ENOENT: no such file or directory, open '.../Fase 3/ecoscan-frontend/dist/sw.js'
 ❯ src/sw.test.js:17:16
     15|
     16|   describe.skipIf(!existsSync(rutaSw))('sw.js generado por el build', …
     17|     const sw = readFileSync(rutaSw, 'utf8');
       |                ^
```

Resultado: `Test Files 1 failed | 1 passed (2)`, `Tests 14 passed (14)`.

**Conclusión: se confirma la hipótesis.** La línea causante es
`Fase 3/ecoscan-frontend/src/sw.test.js:17`
(`const sw = readFileSync(rutaSw, 'utf8')`). El `describe.skipIf` de la línea 16
no evita la lectura porque el cuerpo del `describe` se ejecuta al recolectar
los tests, antes de decidir si se omiten.

El fallo es preexistente en `main` (run `44657570481`) y aparece también en
`feature/umbrales-por-clase` (run `44667984006`).

## 2. Corrección mínima

En `.github/workflows/ci.yml`, job `frontend`:

1. `npm ci`
2. **`npm run build`** (antes)
3. `npm run test:unit`
4. `npm audit --audit-level=high`

Se mantienen los `working-directory: Fase 3/ecoscan-frontend` y
`Fase 3/ecoscan-backend`. No se usa `skip`, no se desactiva ningún test y no se
tocan dependencias.

Además se añade `'fix/**'` a `on.push.branches`; sin ese patrón, la rama
`fix/ci-orden-pasos` no habría generado ningún run y no se podría verificar el
arreglo en Actions.

## 3. Secuencia local exacta del CI (clon limpio, Node 22.23.5)

| Paso | Comando | Salida real |
|---|---|---|
| Frontend | `npm ci` | exit 0; 607 paquetes; avisa 4 vulnerabilidades *moderate* |
| Frontend | `npm run build` | exit 0; genera `dist/sw.js` y `dist/workbox-778a14ff.js` |
| Frontend | `npm run test:unit` | exit 0; **2 archivos, 17 pruebas** (antes sin build: 1 fallo + 14 pruebas) |
| Frontend | `npm audit --audit-level=high` | exit 0; 4 *moderate* por debajo del umbral *high* |
| Backend | `python -m pytest -q --cov=main --cov=rutas_db --cov-report=term-missing` | exit 0; **36 passed**, cobertura total 74 % (`main` 74 %, `rutas_db` 73 %) |
| Backend | `pip-audit -r requirements.txt` | exit 0; **No known vulnerabilities found** |

### Hallazgos de auditors (sin silenciar)

- `glob 9.0.0 - 14.0.1` — Severity: moderate —
  GHSA-3g3m-2fjr-6pw4 (*AbortSignal cancellation bypass allows post-timeout
  filesystem traversal*). Viene de `workbox-build` → `vite-plugin-pwa`.
- `minimatch 7.0.0 - 11.0.0` — Severity: moderate —
  GHSA-g3hv-75wg-m249 (*potential denial of service via globparts
  amplification*). El reporte cuenta 4 vulnerabilidades moderate en total.
- `npm audit` propone `npm audit fix --force` → `vite-plugin-pwa@1.1.0`, que es
  un **cambio breaking**. No se aplicó en el fix de CI (éste es sólo el orden
  de pasos del CI). Queda registrado como deuda y **no se marca Hecho** hasta
  decidir qué hacer con esas CVEs.
- `pytest`: 1 advertencia no fatal de `fastapi.testclient` (recomienda
  `httpx2`). No falla el job.
- `pip-audit`: 1 advertencia benigna del venv por la ruta con espacio; el
  resultado es "No known vulnerabilities found".

## 4. Qué comprobar en la pestaña Actions

Tras el push de `fix/ci-orden-pasos` debe aparecer un run de **CI EcoLearn
Chile** para esa rama. Verificar:

1. En el job `frontend`, el orden de los pasos sea
   *Instalar dependencias → Build → Pruebas unitarias → Auditoría*.
2. `Pruebas unitarias` termine en verde con 17 pruebas.
3. `Auditoría de dependencias` termine en verde (moderate no rompe el umbral
   `high`), igual que `Build`.
4. En el job `backend`, `Pruebas unitarias` (36 pruebas) y `Auditoría de
   dependencias` (`pip-audit`) en verde.

No puedo leer los logs de un job con la API: responde `403 Must have admin
rights to Repository.` Sólo puedo consultar estado/conclusión por API pública;
si el run verde no aparece, hay que revisarlo en la pestaña Actions o darme
permisos de administrador sobre el repositorio.

## 5. Resultado real en Actions (API pública, sin logs)

Run **`44669949452`** — https://github.com/WiChanillao/Capstone_007/actions/runs/44669949452
- Rama `fix/ci-orden-pasos`, SHA `4e1118a`, `status=completed`,
  `conclusion=success`.
- Job `frontend`: **success**. Pasos en orden: Instalar dependencias →
  **Build** → Pruebas unitarias → Auditoría de dependencias, todos `success`.
- Job `backend`: **success**. Pruebas unitarias y Auditoría de dependencias,
  ambos `success`.

Con esto el orden de CI queda corregido y verificado en CI. Las 4 CVEs *moderate*
seguían existiendo en la auditoría, pero no rompen el umbral `high`, igual que
en la ejecución local; se mantienen registradas arriba como deuda.
