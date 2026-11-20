# Reglas permanentes del proyecto EcoLearn / EcoScan

Estas reglas aplican a todas las sesiones y a cualquier rama o worktree.

## Git y revisiones

- Nunca usar `--force`, reescribir historial ni mezclar nada con `main` sin el
  OK explícito del usuario.
- No hacer push de `main`. Los push a ramas de trabajo requieren autorización
  explícita y sólo se hacen tras el escaneo de secretos.
- No cambiar commits ya existentes.
- Cada commit nuevo empieza con la clave del ticket: `REC-123: ...`.
- Cada PR lleva el enlace a su ticket.

## Jira (proyecto REC, capstone-reci-smart.atlassian.net)

- Todo cambio queda registrado en Jira: app, Docker, documentación,
  evidencia, errores y pruebas. Toda tarea tiene ticket (Bug, Tarea o
  Historia).
- Antes de trabajar en algo nuevo, buscar duplicados y crear o localizar su
  ticket.
- Ya existen: REC-64 y REC-122 (clave expuesta), REC-105 (CSP), REC-140
  (evidencia). Vincularlos; no duplicarlos.
- Cada ticket lleva: descripción, causa (si es error), rama, hashes de
  commits, archivos de evidencia, resultado de pruebas y capturas adjuntas.
- No marcar nada como "Hecho" sin evidencia real (captura o salida de prueba).
- Sin acceso a Jira: generar `Fase 3/docs/evidencia/jira/tickets_REC.csv` y
  `tickets_REC.md` con instrucciones de importación, y Mantener el mismo
  flujo de trabajo.
- Nunca escribir tokens ni claves en el repo, en Jira ni en el chat: usar
  variables de entorno y redactar como `***`.

## Evidencia y datos

- No versionar imágenes, dataset, fotos, zips, pesos ni hojas de contacto.
- Scripts en `Fase 3/docs/experimentos/`; reportes y capturas sanitizadas en
  `Fase 3/docs/evidencia/`.
- Las capturas se toman con un navegador headless nuevo, aislado de las
  pestañas y la caché del usuario; sin datos personales.
- Antes de commitear, escanear el diff buscando `AIza`, `sk-`, `ghp_`,
  `password=`, `ROBOFLOW`, rutas `C:\Users` y valores del `.env`. Si hay un
  hallazgo, detenerse y avisar.
- `best.pt` y el mAP@50 oficial 0,562 no se modifican.

## Verificación

- Cambios en la app: `pytest` y `vitest`; Docker con `down -v`,
  `up --build -d` y comprobación de healthchecks.
- Los stacks de prueba usan otro nombre de proyecto y otros puertos; no se
  toca el stack ni el volumen del usuario.
- Dejar constancia del resultado real, aunque sea una falla.
