# Cierre técnico y defensa de EcoLearn

## Estado del candidato local

- Backend: 41 pruebas pasaron con los datos simulados y el puerto de MySQL de prueba deliberadamente desconectado. Queda un aviso de obsolescencia de Starlette TestClient con httpx. El frontend compiló y pasó 24 pruebas.
- Compose validado con MySQL real, escaneo completo y rollback. Ver [evidencia del commit probado](evidencia/VALIDACION_DOCKER_2d2d42f.md).
- GitHub tiene el commit candidato en la rama fix/ecolearn-cierre-entrega. El Run 44669949452 corresponde a una version anterior.
- El backend cargó `best.pt` con SHA-256 `ca855386ebb5a45fe8eeb52f3d43a88d2f4c3fe830506ed31ceb4f21e1fbb9b7`. Este hash identifica los pesos. Para vincularlos a la métrica oficial, conservar el manifiesto de evaluación con el mismo hash y los IDs del conjunto evaluado.
- Compose usa MySQL root y el backend conserva compatibilidad con esquemas antiguos mediante DDL al iniciar. Antes de habilitar producción, trasladar los cambios de esquema a migraciones explícitas, probar una base nueva y un volumen existente, y operar el backend con una cuenta de permisos mínimos.

## Matriz de riesgo por pauta

Los porcentajes identifican indicadores relacionados dentro de cada evaluación. Se superponen entre riesgos y no representan descuentos automáticos. Los ítems 3 y 7 de Ev3 se conservan como indicadores distintos en la pauta.

| Prioridad | Riesgo | Indicadores relacionados | Esfuerzo y evidencia de cierre |
|---|---|---|---|
| 1 | Demo y despliegue reproducible | Ev3.2, 25%; Ev2.2, 20% | Medio. Levantar un Compose aislado, conservar captura de los tres servicios y demostrar foto, escaneo, inferencias e impacto. |
| 2 | PPT e informe con cifras o flujos contradictorios | Ev3.1, 15%; Ev3.6, 20%; Ev3.4, 5%; Ev1.10, 5%; Ev2.7, 15% | Rápido para texto, medio para cotejo y ensayo. Cerrar con PPT e informe definitivos en el mismo commit y guion ajustado al tiempo docente. |
| 3 | Modelo bajo la meta y evidencia CRISP-DM | Ev3.2, 25%; Ev3.3, 20%; Ev2.1, 10% | Rápido para reconciliar el relato. Crítico si se exige alcanzar 0,65: congelar particiones, evaluar el peso exacto e informar mAP por clase y global. |
| 4 | Aportes y competencias individuales | Ev2.9, 15%; Ev2.4, 5%; Ev1.2, 5% | Medio. Por integrante, registrar competencia oficial, ticket o tarea, artefacto, enlace de revisión o commit y explicación breve de la contribución. |
| 5 | UAT y SUS | Ev3.2, 25%; Ev2.2, 20% | Depende de participantes. Usar tareas de escáner, mapa e interpretación del impacto. Reportar completitud, errores, incidencias y SUS con tamaño de muestra y limitaciones. |
| 6 | Scrumban sin control de flujo acreditado | Ev2.1, 10%; Ev1.6, 10%; Ev3.1, 15% | Rápido para documentar el alcance real. Para acreditar su uso, acordar y registrar límites WIP, reglas de entrada/salida y tiempos de transición desde una fecha real. |

## Cambios concretos para el PPT versionado

- Láminas 3, 4, 5 y 14: **Menú Principal y cuatro módulos**. El impacto va dentro del Eco-Simulador. Desafío Verde combina avance automático y trivia. Sustituir el bloque de arquitectura por el PNG actualizado. Usar `/db/impacto` y `/db/sesiones`.
- Lámina 6: conciliar conteos por partición con el cuaderno y el manifiesto del dataset evaluado. La preparación del cuaderno reescribe etiquetas en su copia de trabajo, por lo que la frase «solo en memoria» requiere corrección. Identificar los resultados que corresponden a cada corrida.
- Lámina 7: precisar que 0,562 corresponde a validación y que la meta de 0,65 no se alcanzó. Separar el dato histórico 27/30 de la evaluación de detección y de UAT. La latencia de inferencia y la latencia HTTP son mediciones distintas.
- Láminas 8 y 14: fechar la evidencia histórica, vincular las pruebas locales y verificar el run de Actions del commit candidato antes de presentar CI en verde. Incorporar la matriz oficial de 97 casos sin usar ese número como cantidad de pruebas automatizadas.
- Láminas 11 y 15: conservar los pendientes de producción, rotación y UAT/SUS. Para credenciales históricas, rotar primero y revisar el historial. Cualquier reescritura de Git requiere coordinación con el equipo.
- Lámina 13: 161 tickets en el inventario auditado. Los conteos del tablero visible dependen de la vista. Describir Scrumban como aplicación parcial con sprints y tablero. CRISP-DM cubre datos y modelo.

La guía 2.6 contiene texto completado que menciona React 18 y Scrum. Si el equipo la usa como informe, actualizar el objetivo a React 19 y FastAPI, explicar el alcance de Scrumban, y vincular tanto la evaluación a 0,562 como la evidencia de cada contribución. Confirmar la plantilla y la duración de Ev3 con la convocatoria docente. Los tiempos de los clips de demo no acreditan la duración de la defensa.

## Checklist previo a GitHub y a la defensa

- [ ] Desde Fase 3 ejecutar `docker compose config --quiet`. Con Docker Desktop accesible, levantar un entorno de pruebas con proyecto, puertos y volumen aislados. Revisar primero si Compose define nombres de contenedor fijos y asignar nombres distintos mediante un override. Conservar los volúmenes originales.
- [ ] Verificar `docker compose ps`, `GET /health` con `mysql_conectado=true`, `GET /version`, esquema de 15 tablas y el SHA-256 del peso de entrega. Guardar fecha, commit y entorno.
- [ ] Ejecutar pytest, build y Vitest. En la integración probar foto nítida, borrosa y sin detecciones, una sesión distinta y el caso de persistencia degradada. Comparar filas de `escaneos`, `inferencia` y el impacto de la sesión de prueba. Verificar acceso local a las operaciones de mantenimiento y su bloqueo por el proxy.
- [x] Validar la transaccion InnoDB en MySQL aislado. Una escritura de inferencias fallida dejo cero filas en sesion, escaneos e inferencia. La idempotencia ante reenvios requiere un mecanismo aparte.
- [ ] Reunir la evidencia de UAT y SUS con participantes, tareas y resultados reales. Mantener el diagnóstico inicial y las pruebas automatizadas como evidencias distintas.
- [ ] Cerrar versiones del informe y PPT, verificar nombres y formato docente, asignar qué explica cada integrante y cronometrar un ensayo completo.
- [ ] Revisar `git status --short` y `git diff --check`. Revisar archivos nuevos de manera explícita. El diagnóstico local `tests/diagnostico_400.py` requiere revisión antes de incluirlo. Examinar secretos, datos y respaldos antes de publicar.
- [ ] Hacer commit de la versión aprobada, confirmar la referencia remota con `git fetch origin` y `git rev-list --left-right --count origin/main...HEAD`, publicar por el flujo acordado y verificar Actions y los enlaces de evidencia del commit publicado.

## Cómo fortalecer la evaluación sin reentrenar

1. Registrar el hash de `best.pt`, la revisión del dataset, los IDs por partición, el comando de evaluación y las métricas por clase. Mantener el mAP@50 de 0,562 en validación y 0,65 como meta pendiente. Si falta el manifiesto original, identificar expresamente la cifra como resultado histórico documentado.
2. Preparar un conjunto de fotos aparte para evaluar el uso real, con cartón, aluminio, plástico, objetos fuera de alcance y condiciones difíciles. Fijar antes de medir qué cuenta como una detección correcta, un error o una abstención. Reportar esas cifras junto con el tamaño del conjunto. Mantenerlas separadas del mAP.
3. Usar validación para estudiar si el umbral operativo mejora el equilibrio entre errores y abstenciones. Reservar test para una evaluación final única, si hay una partición independiente. Cambiar el umbral de la app afecta qué resultados se muestran y guardan. Por sí solo no mejora el mAP del detector.
4. Realizar UAT y SUS con usuarios reales. Observar si pueden tomar una foto aprovechable, recuperarse ante un resultado dudoso y encontrar un punto limpio. Documentar fallas y correcciones de usabilidad. No usar ejemplos de demo como resultados de usuarios.
