# Validación Docker y MySQL de EcoLearn

El 20 de noviembre de 2026 se probó el código del commit `2d2d42f` en un proyecto Compose aislado, con una base MySQL 8 inicializada desde los scripts del repositorio y con puertos y volumen propios.

| Comprobación | Resultado observado |
|---|---|
| Arranque del entorno | Se construyeron las imágenes y Compose levantó los tres servicios con sus comprobaciones de salud. |
| API a través de nginx | `/api/health` devolvió `mysql_conectado: true`. `/api/version` identificó `best.pt` y las tres clases. |
| Catálogo y esquema | `/api/db/puntos` devolvió 35 registros. MySQL informó 15 tablas en `ecoscan`. |
| Rutas operativas en el proxy | El proxy respondió HTTP 404 en las rutas de retención, exportación CSV y escritura directa de inferencias. |
| Escaneo de extremo a extremo | La foto `aluminio.jpg` produjo una detección aceptada con `escaneo_guardado: true`. MySQL registró un escaneo y una inferencia aceptada para la sesión nueva. El endpoint de impacto devolvió un escaneo para esa sesión. |
| Fallo parcial de escritura | Un disparador temporal de la base aislada rechazó el INSERT de inferencias. La API conservó la detección y respondió `escaneo_guardado: false`. La consulta posterior encontró cero sesiones, cero escaneos y cero inferencias para el identificador de prueba. El disparador se retiró. |

SHA-256 de `best.pt` reportado por la API: `ca855386ebb5a45fe8eeb52f3d43a88d2f4c3fe830506ed31ceb4f21e1fbb9b7`.

La prueba verifica integración y rollback. El resultado oficial de evaluación del detector sigue siendo mAP@50 de 0,562 en validación.
