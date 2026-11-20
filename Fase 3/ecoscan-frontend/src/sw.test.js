import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const raiz = process.cwd();
const configuracion = readFileSync(resolve(raiz, 'vite.config.js'), 'utf8');
const rutaSw = resolve(raiz, 'dist/sw.js');

describe('PWA: actualización automática del service worker', () => {
  it('configura autoUpdate, caché versionada y limpieza de cachés antiguas', () => {
    expect(configuracion).toMatch(/registerType:\s*'autoUpdate'/);
    expect(configuracion).toMatch(/cacheId:\s*'ecolearn-v2-'/);
    expect(configuracion).toMatch(/cleanupOutdatedCaches:\s*true/);
  });

  describe.skipIf(!existsSync(rutaSw))('sw.js generado por el build', () => {
    const sw = readFileSync(rutaSw, 'utf8');

    it('incluye skipWaiting y clientsClaim', () => {
      expect(sw).toMatch(/skipWaiting\(\)/);
      expect(sw).toMatch(/clientsClaim\(\)/);
    });

    it('usa un nombre de caché versionado y limpia las versiones anteriores', () => {
      expect(sw).toMatch(/setCacheNameDetails\(\{\s*prefix:\s*['"]ecolearn-v2-['"]\s*\}\)/);
      expect(sw).toMatch(/cleanupOutdatedCaches\(\)/);
    });
  });
});
