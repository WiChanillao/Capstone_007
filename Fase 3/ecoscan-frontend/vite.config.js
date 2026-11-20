import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        // Nombre de caché versionado. cleanupOutdatedCaches() se registra en
        // activate y elimina las precachés del bundle anterior sin limpieza manual.
        cacheId: 'ecolearn-v2-',
        cleanupOutdatedCaches: true,
      },
      manifest: {
        name: 'EcoLearn Chile — Clasificador Inteligente',
        short_name: 'EcoLearn',
        description: 'Clasificación inteligente de cartón, plástico y aluminio para la Región Metropolitana.',
        theme_color: '#10b981',
        background_color: '#020617',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
          }
        ]
      }
    })
  ],
})