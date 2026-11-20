# Herramientas y conectores MCP (REC-140)

Fecha: 2026-11-20. Objetivo: poder leer logs de Actions y gestionar Jira sin
tokens escritos en el repo, en Jira ni en el chat.

## Qué se configuró, para qué y cómo desinstalarlo

| Elemento | Para qué | Cómo desinstalarlo |
|---|---|---|
| Conector MCP remoto `github` (`https://api.githubcopilot.com/mcp/`) | Leer PRs y, si los permisos lo permiten, logs de GitHub Actions (hoy la API pública responde `403 Must have admin rights`). | Quitar la entrada `mcp.servers.github` de `~/.config/opencode/opencode.json` (o borrar el archivo si no tiene otras entradas). No deja archivos en el proyecto. |
| Conector MCP remoto `atlassian` (`https://mcp.atlassian.com/v2/mcp`) | Crear/actualizar tickets REC y comentarios con evidencia real. | Quitar la entrada `mcp.servers.atlassian` del mismo archivo. |
| Playwright + Chrome headless (ya instalados en `AppData/Local/Temp/opencode/headless`) | Capturas aisladas del Desafío y del caso "Posible". | Borrar esa carpeta temporal; no se añadió nada a `package.json`. |

No se instaló GitHub CLI (`gh`): la creación del PR 1 ya se hizo con la API
usando la credencial de Git en memoria, y `gh` no soluciona el `403` de logs,
que es un permiso del repositorio. Tampoco se añadieron dependencias al
proyecto ni se cambió configuración del sistema o de seguridad.

## Configuración exacta (OpenCode V2)

Archivo: `~/.config/opencode/opencode.json`. Se conservó el servidor local
`browse` existente y se añadieron dos servidores remotos:

```json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "remote",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": { "X-MCP-Toolsets": "default,actions" }
      },
      "atlassian": {
        "type": "remote",
        "url": "https://mcp.atlassian.com/v2/mcp"
      }
    }
  }
}
```

Fuentes oficiales consultadas:

- OpenCode MCP (V2, `mcp.servers`, OAuth por defecto, `{env:NOMBRE}` para
  secretos): https://opencode.ai/docs/mcp-servers/
- GitHub MCP Server (endpoint remoto y guía de OpenCode):
  https://github.com/github/github-mcp-server y
  https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-opencode.md
- Atlassian MCP Server v2 (URL y OAuth 2.1):
  https://support.atlassian.com/atlassian-ai-gateway/docs/get-started-with-the-atlassian-remote-mcp-server/

Nota: la guía de GitHub para OpenCode usa la forma antigua (`mcp.github` con
`enabled`). Se aplicó la forma V2 vigente de OpenCode (`mcp.servers` y
`disabled` en lugar de `enabled`), que es la documentación de referencia.

## Autenticación

- Ambos servidores usan **OAuth**; OpenCode guarda las credenciales fuera del
  archivo de configuración. **No hay tokens en el repo, en Jira ni en el chat.**
- La lectura simple inicial devolvió `401` en ambos endpoints, confirmando que
  son alcanzables y que esperan inicio de sesión. `opencode.json` validó como
  JSON correcto.
- Estado: **configurados, pendientes de inicio de sesión**. En la TUI hay que
  ejecutar `/mcps`, seleccionar `github` y `atlassian` y completar el login en
  el navegador. Hasta que la conexión figure como `connected`, no se informa
  ninguna lectura MCP como realizada.

## Evidencia real disponible

- PR 1 creado y verificado con la API de GitHub usando la credencial local de
  Git en memoria: https://github.com/WiChanillao/Capstone_007/pull/1
- `GET /user` autenticó como `BrunoDiazAST` (sin imprimir ningún token).
- Endpoints MCP: `api.githubcopilot.com/mcp/` → HTTP 401;
  `mcp.atlassian.com/v2/mcp` → HTTP 401 (esperando OAuth).
- Sin secretos en el diff; el escaneo previo al commit cubre `AIza`, `sk-`,
  `ghp_`, `password=`, `ROBOFLOW`, rutas de usuario y valores del `.env`.
