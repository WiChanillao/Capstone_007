# Revisión de claves REC en los commits nuevos

Revisión de `git log --all`; **no se tocó ningún commit**. Alcance: los commits
añadidos en esta entrega a las cuatro ramas publicadas.

| Commit | Rama | Clave | Asunto del commit | Tema del ticket | ¿Encaja? |
|---|---|---|---|---|---|
| `8f93638` | `experimento/generalizacion` | REC-63 | Evidencia de generalización, bootstrap y geometría | Modelo / mAP (ampliado con generalización) | Sí |
| `586fea9` | `experimento/generalizacion` | REC-64 | Scripts y notebook de experimentos en Colab | Revisión del Colab y rotación pendiente (`e22a54f`) | Sí, con matiz (ver abajo) |
| `9616280` | `experimento/generalizacion` | REC-140 | Evidencia visual, tickets REC y reglas permanentes | Evidencia y capturas | Sí |
| `17ffe8a` | `experimento/generalizacion` | REC-140 | Hashes de commits y resultado del CI en Jira | Evidencia y trazabilidad | Sí |
| `de3704e` | `feature/umbrales-por-clase` | REC-103 | Umbrales por clase y nivel posible, `imgsz=640` | Umbral de confianza (épico de REC-167) | Sí |
| `aa20fb8` | `feature/umbrales-por-clase` | REC-140 | Evidencia de umbrales, evaluación en test y Docker | Evidencia y capturas | Sí |
| `4e1118a` | `fix/ci-orden-pasos` | REC-170 | Construir antes de `test:unit` en CI y permitir `fix/**` | Bug del orden de pasos del CI | Sí |
| `f3e13e5` | `fix/ci-orden-pasos` | REC-170 | Registrar run de Actions exitoso | Evidencia del mismo bug | Sí |
| `88e72b1` | `fix/desafio-preguntas` | REC-162 | Banco de 25 preguntas y rondas sin repetición | Bug del Desafío Verde | Sí |
| `17ce4e5` | `fix/desafio-preguntas` | REC-162 | Capturas antes/después, preguntas y stack aislado | Evidencia del mismo bug | Sí |

## Claves que no encajan

**Ninguna clave es claramente incorrecta.** No se encontró ningún commit cuyo
prefijo REC contradiga el asunto del ticket.

### Matiz a aclarar en Jira (sin tocar commits)

- **REC-64**: `AGENTS.md` lo describe como “clave expuesta” (junto con
  REC-122), pero el historial muestra que ya se usó para “documentar revisión
  del Colab y rotación pendiente” (`e22a54f`). El commit `586fea9` trata
  precisamente scripts y notebook de Colab, así que encaja con esa parte del
  alcance. Conviene confirmar en Jira si REC-64 es el contenedor correcto para
  los experimentos o si debe crearse un ticket hijo; **no se creó ni se
  renombró nada** para evitar duplicados.
- **REC-103 / REC-167**: el commit `de3704e` va más allá del umbral simple,
  pero REC-103 se registró explícitamente como épico de la Historia REC-167 en
  `tickets_REC.csv`, así que la clave es coherente.
- **REC-140**: se usó para varios artefactos de evidencia de ramas distintas;
  es el ticket contenedor de evidencia y capturas, por lo que encaja.

## Pendiente

Cuando Jira asigne las claves reales a `REC-162`…`REC-170`, actualizar
**sólo** la tabla de equivalencias en `comentarios_existentes.md`. Los commits
ya publicados conservan sus prefijos: no se reescriben.
