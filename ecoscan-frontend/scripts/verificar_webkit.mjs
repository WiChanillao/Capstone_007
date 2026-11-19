// Verificación cross-browser en WebKit (REC-114).
// Uso: node scripts/verificar_webkit.mjs [URL]
import { webkit } from 'playwright';

const url = process.argv[2] || 'http://localhost:5173/';
const ancho = Number(process.argv[3] || 1280);
const errores = [];
const navegador = await webkit.launch({ headless: true });
const pagina = await navegador.newPage({ viewport: { width: ancho, height: 800 } });

pagina.on('console', (msg) => {
  if (msg.type() === 'error') errores.push(msg.text());
});
pagina.on('pageerror', (err) => errores.push(String(err)));

await pagina.goto(url, { waitUntil: 'networkidle' });
await pagina.getByText('EcoLearn Chile', { exact: false }).first().waitFor();

const pestañas = ['Menú Principal', 'Escáner IA', 'Puntos Limpios RM',
  'Eco-Simulador RM', 'Desafío Verde RM'];
const botones = await pagina.locator('nav button').allTextContents();
const visibles = pestañas.filter((nombre) => botones.some((b) => b.includes(nombre)));

const sliders = await pagina.locator('input[type="range"]').count();
const desbordeHorizontal = await pagina.evaluate(
  () => document.documentElement.scrollWidth > window.innerWidth + 1
);
const marcas = [];
for (const nombre of pestañas.slice(1)) {
  await pagina.locator('nav button', { hasText: nombre }).click();
  await pagina.waitForTimeout(250);
  const texto = await pagina.locator('main').innerText();
  marcas.push({ pestaña: nombre, ok: texto.length > 40 });
}

const resultado = {
  navegador: 'WebKit (Playwright ' + (await import('playwright/package.json', { with: { type: 'json' } })).default.version + ')',
  url,
  ancho_px: ancho,
  desborde_horizontal: desbordeHorizontal,
  pestañas_encontradas: visibles.length,
  pestañas: visibles,
  sliders,
  navegacion: marcas,
  errores_consola: errores,
};
console.log(JSON.stringify(resultado, null, 2));
await navegador.close();

if (visibles.length !== 5 || sliders !== 0 || desbordeHorizontal || marcas.some((m) => !m.ok) || errores.length) {
  process.exitCode = 1;
}
