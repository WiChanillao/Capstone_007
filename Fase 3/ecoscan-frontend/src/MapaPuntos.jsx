import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';

const CENTRO_RM = [-33.45, -70.65];

function escapar(texto) {
  return String(texto ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

/**
 * Mapa interactivo de Puntos Limpios RM con Leaflet + OpenStreetMap/CARTO.
 * No usa API keys. Los marcadores salen de los datos reales de MySQL.
 */
export default function MapaPuntos({ puntos, ubicacion, puntoActivo, onSeleccionar, estaAbierto }) {
  const contenedorRef = useRef(null);
  const mapaRef = useRef(null);
  const leafletRef = useRef(null);
  const grupoRef = useRef(null);
  const limitesRef = useRef(null);
  const marcadoresRef = useRef(new Map());
  const seleccionRef = useRef(null);
  const [listo, setListo] = useState(false);

  // Crear el mapa una sola vez (Leaflet se carga dinámicamente para no
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

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener noreferrer">CARTO</a>',
      }).addTo(mapa);

      grupoRef.current = L.layerGroup().addTo(mapa);
      mapaRef.current = mapa;
      mapa.whenReady(() => mapa.invalidateSize());
      setListo(true);
    });

    return () => {
      vivo = false;
      if (mapa) {
        mapa.remove();
        mapaRef.current = null;
        grupoRef.current = null;
        marcadores.clear();
      }
    };
  }, []);

  // Redibujar marcadores cuando cambian los filtros o la ubicación.
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
        html: `<div style="width:32px;height:32px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:${color};border:2px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center"><span style="transform:rotate(45deg);font-size:15px">♻️</span></div>`,
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
          <div style="font-size:12px;margin-top:3px">🕒 ${escapar(p.horario)}</div>
          <div style="font-size:11px;font-weight:700;margin-top:4px;color:${color}">${estado}</div>
          <div style="font-size:11px;margin-top:6px;color:#475569">${(p.materiales || []).map((m) => escapar(m)).join(' · ')}</div>
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
      limitesRef.current = L.latLngBounds(coords).pad(0.18);
      mapa.fitBounds(limitesRef.current, { maxZoom: 13 });
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
        className="h-[320px] sm:h-[420px] lg:h-[500px] w-full rounded-2xl border border-slate-700 overflow-hidden bg-slate-900"
      />
      <button
        type="button"
        onClick={() => {
          const mapa = mapaRef.current;
          if (mapa && limitesRef.current) mapa.fitBounds(limitesRef.current, { maxZoom: 13 });
        }}
        className="absolute top-3 right-3 z-[500] px-3 py-1.5 rounded-lg bg-slate-950/90 border border-slate-600 text-[11px] font-bold text-slate-100 hover:border-emerald-400 cursor-pointer"
      >
        ⤢ Ajustar mapa
      </button>
      <div className="absolute bottom-3 left-3 z-[500] flex flex-wrap gap-2 text-[10px] font-bold">
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-emerald-500/40 text-emerald-300">● Abierto</span>
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-rose-500/40 text-rose-300">● Cerrado</span>
        <span className="px-2 py-1 rounded-md bg-slate-950/90 border border-slate-500/40 text-slate-300">● Sin horario</span>
      </div>
    </div>
  );
}
