# Frontend — EcoLearn Chile (EcoScan)

App React 19 + Vite + Tailwind (PWA) con **Menú Principal + 4 módulos**:
**Escáner IA**, **Puntos Limpios RM**, **Eco-Simulador RM** y **Desafío Verde RM**.
El impacto está integrado en el Eco-Simulador, no es una pestaña separada.

## Desarrollo

```bash
npm install
npm run dev          # http://localhost:5173
```

La URL del backend se toma de `VITE_API_URL` (por defecto `/api`, mismo origen; nginx la redirige a `backend:8000`). Para desarrollo sin Docker, copiar `.env.example` a `.env.local` y apuntar a `http://127.0.0.1:8000`.

## Comandos

| Comando | Descripción |
|---|---|
| `npm run dev` | Servidor de desarrollo Vite |
| `npm run build` | Build de producción (lo usa el `Dockerfile` con Nginx) |
| `npm run preview` | Previsualizar el build |
| `npm run test:unit` | Vitest (componentes) |
| `npm run test:e2e` | Cypress headless (Electron) |
| `npm run test:webkit` | Verificación en WebKit con Playwright |
| `npm run lint` | oxlint |

## Notas

- No hay *sliders* ni carga manual: el escáner dispara la predicción al subir una foto.
- El impacto se cuenta por sesión anónima, por eso una sesión nueva parte en 0.
- En Docker, el frontend se sirve por Nginx en el puerto host `5173`.
