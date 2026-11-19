import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';

const CENTRO_RM = [-33.45, -70.65];

// Fuentes publicas, sin API key. Se prueba la primera y se cambia automaticamente
// si el proveedor bloquea las teselas; el usuario tambien puede alternar a mano.
const BASEMAPAS = [
  {
    id: 'osm',
    etiqueta: 'Calles OSM',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    subdominios: 'abc',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a>',
  },
  {
    id: 'voyager',
    etiqueta: 'Calles claras',
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    subdominios: 'abcd',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener noreferrer">CARTO</a>',
  },
  {
    id: 'satellite',
    etiqueta: 'Satelite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    subdominios: 'abc',
    overlay: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics',
  },
];

function escapar(texto) {
  return String(texto ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

/**
 * Mapa interactivo de Puntos Limpios RM con Leaflet.
 * No usa API keys. Los marcadores salen de los datos reales de MySQL.
 */
export default function MapaPuntos({ puntos, ubicacion, puntoActivo, onSeleccionar, estaAbierto }) {
  const contenedorRef = useRef(null);
  const mapaRef = useRef(null);
  const leafletRef = useRef(null);
  const grupoRef = useRef(null);
  const teselasRef = useRef(null);
  const etiquetasRef = useRef(null);
  const limitesRef = useRef(null);
  const marcadoresRef = useRef(new Map());
  const seleccionRef = useRef(null);
  const fallbacksRef = useRef(0);
  const [listo, setListo] = useState(false);
  const [indiceBase, setIndiceBase] = useState(0);

  // Crear el mapa una sola vez (Leaflet se carga dinamicamente para no
  // interferir con las pruebas unitarias en jsdom).
  useEffect(() => {
    let vivo = true;
    const marcadores = marcadoresRef.current;
    import('leaflet').then(({ default: L }) => {
      if (!vivo || !contenedorRef.current || mapaRef.current) return;
      leafletRef.current = L;
      const mapa = L.map(contenedorRef.current, {
        zoomControl: true,
        scrollWheelZoom: false,
        attributionControl: true,
      }).setView(CENTRO_RM, 11);

      grupoRef.current = L.layerGroup().addTo(mapa);
      mapaRef.current = mapa;
      mapa.whenReady(() => mapa.invalidateSize());
      setListo(true);
    });

    return () => {
      vivo = false;
      if (mapaRef.current) {
        mapaRef.current.remove();
        mapaRef.current = null;
        grupoRef.current = null;
        teselasRef.current = null;
        marcadores.clear();
      }
    };
  }, []);

  // Capa base con respaldo automatico si el proveedor no responde.
  useEffect(() => {
    if (!listo) return;
    const L = leafletRef.current;
    const mapa = mapaRef.current;
    if (!L || !mapa) return;

    if (teselasRef.current) mapa.removeLayer(teselasRef.current);
    if (etiquetasRef.current) mapa.removeLayer(etiquetasRef.current);
    const cfg = BASEMAPAS[indiceBase];
    const capa = L.tileLayer(cfg.url, {
      maxZoom: 19,
      subdomains: cfg.subdominios,
      attribution: cfg.attribution,
      crossOrigin: true,
    });

    let errores = 0;
    capa.on('tileerror', () => {
      errores += 1;
      if (errores >= 3 && fallbacksRef.current < BASEMAPAS.length - 1) {
        fallbacksRef.current += 1;
        setIndiceBase((i) => (i + 1) % BASEMAPAS.length);
      }
    });
    capa.addTo(mapa);
    capa.bringToBack();
    teselasRef.current = capa;

    if (cfg.overlay) {
      const etiquetas = L.tileLayer(cfg.overlay, {
        maxZoom: 19,
        subdomains: 'abc',
        attribution: '&copy; Esri',
        pane: 'shadowPane',
      });
      etiquetas.addTo(mapa);
      etiquetasRef.current = etiquetas;
    }

    return () => {
      if (teselasRef.current === capa) {
        mapa.removeLayer(capa);
        teselasRef.current = null;
      }
      if (etiquetasRef.current) {
        mapa.removeLayer(etiquetasRef.current);
        etiquetasRef.current = null;
      }
    };
  }, [listo, indiceBase]);

  // Redibujar marcadores cuando cambian los filtros o la ubicacion.
  useEffect(() => {
    if (!listo) return;
    const L = leafletRef.current;
    const mapa = mapaRef.current;
    const grupo = grupoRef.current;
    if (!L || !mapa || !grupo) return;

    grupo.clearLayers();
    marcadoresRef.current.clear();
    const coords = [];

    puntos.forEach((p) => {
      if (!Number.isFinite(p.lat) || !Number.isFinite(p.lon)) return;
      coords.push([p.lat, p.lon]);
      const abierto = estaAbierto ? estaAbierto(p) : null;
      const color = abierto === true ? '#10b981' : abierto === false ? '#f43f5e' : '#64748b';
      const estado = abierto === true ? '● Abierto ahora' : abierto === false ? '○ Cerrado ahora' : 'Horario por confirmar';
      const icono = L.divIcon({
        className: 'punto-limpio-marker',
        html: `<div style="width:32px;height:32px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:${color};border:3px solid #fff;box-shadow:0 3px 12px rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center"><span style="transform:rotate(45deg);font-size:15px">♻️</span></div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -30],
      });
      const marcador = L.marker([p.lat, p.lon], { icon: icono, title: p.nombre }).addTo(grupo);
      const destino = `https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lon}`;
      marcador.bindPopup(`
        <div style="min-width:220px;font-family:inherit;color:#0f172a">
          <div style="font-size:11px;font-weight:700;color:#047857">${escapar(p.comuna)}</div>
          <div style="font-size:14px;font-weight:800;margin:2px 0 6px">${escapar(p.nombre)}</div>
          <div style="font-size:12px">📍 ${escapar(p.direccion)}</div>
          <div style="font-size:12px;margin-top:3px">🕒 ${escapar(p.horario || 'Horario por confirmar')}</div>
          <div style="font-size:11px;font-weight:700;margin-top:4px;color:${color}">${estado}</div>
          <div style="font-size:11px;margin-top:6px;color:#475569">${(p.materiales || []).map((m) => escapar(m)).join(' · ')}</div>
          ${p.fuente === 'listado_externo_2026-11-19' || p.coordsAproximadas ? `<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px">
            ${p.fuente === 'listado_externo_2026-11-19' ? '<span style="font-size:9px;font-weight:700;padding:2px 5px;border-radius:4px;background:#fef3c7;color:#92400e">Externo · sin validar</span>' : ''}
            ${p.coordsAproximadas ? '<span style="font-size:9px;font-weight:700;padding:2px 5px;border-radius:4px;background:#e2e8f0;color:#334155">Coordenada aproximada</span>' : ''}
          </div>` : ''}
          ${p.nota ? `<div style="font-size:10px;margin-top:6px;color:#64748b;font-style:italic;line-height:1.35">${escapar(p.nota)}</div>` : ''}
          <a href="${escapar(destino)}" target="_blank" rel="noopener noreferrer"
             style="display:inline-block;margin-top:8px;font-size:12px;font-weight:700;color:#047857">🧭 Cómo llegar en Google Maps</a>
        </div>
      `);
      marcador.on('click', () => onSeleccionar?.(p));
      marcadoresRef.current.set(p.nombre, marcador);
    });

    if (ubicacion && Number.isFinite(ubicacion.lat) && Number.isFinite(ubicacion.lon)) {
      coords.push([ubicacion.lat, ubicacion.lon]);
      L.circleMarker([ubicacion.lat, ubicacion.lon], {
        radius: 8,
        color: '#fff',
        weight: 2,
        fillColor: '#38bdf8',
        fillOpacity: 1,
      }).addTo(grupo).bindPopup('📍 Tu ubicación');
    }

    if (coords.length) {
      limitesRef.current = L.latLngBounds(coords).pad(0.25);
      mapa.fitBounds(limitesRef.current, { maxZoom: 13, padding: [24, 24] });
    } else {
      mapa.setView(CENTRO_RM, 11);
    }
  }, [listo, puntos, ubicacion, estaAbierto, onSeleccionar]);

  // Mantener el tamaño correcto cuando cambia el ancho de la tarjeta.
  useEffect(() => {
    if (!listo || typeof ResizeObserver === 'undefined' || !contenedorRef.current) return;
    const obs = new ResizeObserver(() => mapaRef.current?.invalidateSize());
    obs.observe(contenedorRef.current);
    return () => obs.disconnect();
  }, [listo]);

  // Abrir el popup del punto seleccionado desde la lista de tarjetas.
  useEffect(() => {
    const actual = puntoActivo?.nombre ?? null;
    if (seleccionRef.current === actual) return;
    seleccionRef.current = actual;
    if (!actual) return;
    const marcador = marcadoresRef.current.get(actual);
    const mapa = mapaRef.current;
    if (marcador && mapa) {
      mapa.panTo(marcador.getLatLng(), { animate: true });
      marcador.openPopup();
    }
  }, [puntoActivo, puntos]);

  return (
    <div className="relative">
      <div
        ref={contenedorRef}
        role="application"
        aria-label="Mapa interactivo de puntos limpios en la Región Metropolitana"
        className="h-[340px] sm:h-[460px] lg:h-[540px] w-full rounded-2xl border border-slate-700 overflow-hidden bg-slate-900"
      />
      <div className="absolute top-3 left-3 z-[500] px-3 py-1.5 rounded-lg bg-slate-950/85 border border-emerald-500/40 text-[11px] font-black text-emerald-200 shadow-lg pointer-events-none">
        Región Metropolitana de Santiago
      </div>
      <div className="absolute top-3 right-3 z-[500] flex flex-col items-end gap-2">
        <button
          type="button"
          onClick={() => {
            fallbacksRef.current = 0;
            setIndiceBase((i) => (i + 1) % BASEMAPAS.length);
          }}
          className="px-3 py-1.5 rounded-lg bg-slate-950/90 border border-slate-600 text-[11px] font-bold text-slate-100 hover:border-emerald-400 cursor-pointer"
          title="Cambiar estilo del mapa"
        >
          🗺️ {BASEMAPAS[indiceBase].etiqueta} ▾
        </button>
        <button
          type="button"
          onClick={() => {
            const mapa = mapaRef.current;
            if (mapa && limitesRef.current) mapa.fitBounds(limitesRef.current, { maxZoom: 13, padding: [24, 24] });
          }}
          className="px-3 py-1.5 rounded-lg bg-slate-950/90 border border-slate-600 text-[11px] font-bold text-slate-100 hover:border-emerald-400 cursor-pointer"
        >
          ⤢ Ajustar mapa
        </button>
      </div>
      <div className="absolute bottom-3 left-3 z-[500] flex flex-wrap gap-2 text-[10px] font-bold">
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-emerald-500/40 text-emerald-300">● Abierto</span>
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-rose-500/40 text-rose-300">● Cerrado</span>
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-slate-500/40 text-slate-300">● Sin horario</span>
      </div>
    </div>
  );
}
