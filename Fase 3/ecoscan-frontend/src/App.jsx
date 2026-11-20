import React, { useState, useRef, useEffect } from 'react';
import MapaPuntos from './MapaPuntos.jsx';

// URL del backend configurable por entorno (REC-105).
// Por defecto usa /api (mismo origen): funciona en local y cuando la app se comparte por túnel.
const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

// Base de datos estricta de los 3 materiales soportados (EcoLearn Chile)
const CONTENEDORES_POR_DEFECTO = {
  carton: 'Contenedor Azul',
  plastico: 'Contenedor Amarillo',
  aluminio: 'Contenedor Gris'
};

const GUIA_RESIDUOS_CHILE = {
  carton: {
    id: 'carton',
    nombre: 'Cartón y Papel',
    icono: '📦',
    colorGradient: 'from-amber-500 to-yellow-600',
    colorBorder: 'border-amber-500/50',
    contenedor: CONTENEDORES_POR_DEFECTO.carton,
    pasosReciclaje: [
      'Limpia el cartón o papel de grasas o restos de comida.',
      'Retira cintas adhesivas, corchetes o plásticos pegados.',
      'Desarma y aplasta las cajas para reducir volumen.'
    ],
    pasosReutilizar: [
      'Úsalo como base para compostaje o mantillo de huertos.',
      'Crea organizadores de escritorio o cajas de almacenamiento.',
      'Reutiliza las cajas intactas para futuros envíos o mudanzas.'
    ],
    linksReciclaje: [
      { nombre: 'Portal Santiago Recicla (MMA)', url: 'https://santiagorecicla.mma.gob.cl', desc: 'Mapa e inventario oficial de Puntos Limpios del MMA.' },
      { nombre: 'TriCiclos Chile', url: 'https://www.triciclos.cl', desc: 'Red nacional de estaciones y gestión de reciclaje.' }
    ],
    linksReutilizar: [
      { nombre: 'Traperos de Emaús', url: 'https://www.emaus.cl', desc: 'Donaciones de cajas y embalajes.' },
      { nombre: 'Fundación Basura', url: 'https://www.fundacionbasura.org', desc: 'Guías de reutilización y compostaje.' }
    ],
    videosReutilizar: [
      {
        id: 's73tbA8eP50',
        titulo: 'Transforma cartón en muebles organizadores',
        autor: 'kokoelkartonero'
      },
      {
        id: 'xbXrEsQ5Gzg',
        titulo: '3 manualidades para transformar cajas de zapatos',
        autor: 'showdemanualidades'
      }
    ]
  },
  aluminio: {
    id: 'aluminio',
    nombre: 'Lata de Aluminio',
    icono: '🥫',
    colorGradient: 'from-slate-400 to-zinc-600',
    colorBorder: 'border-slate-400/50',
    contenedor: CONTENEDORES_POR_DEFECTO.aluminio,
    pasosReciclaje: [
      'Enjuaga la lata para eliminar restos de líquido o alimento.',
      'Deja secar el interior por completo.',
      'Aplástala suavemente para optimizar espacio en el contenedor.'
    ],
    pasosReutilizar: [
      'Conviértela en macetero decorativo para suculentas.',
      'Úsala como portalápices u organizador de escritorio.',
      'Fabrica faroles decorativos o ceniceros reutilizables.'
    ],
    linksReciclaje: [
      { nombre: 'Kyklos Chile', url: 'https://www.kyklos.cl', desc: 'Programas de valorización de metales y latas.' },
      { nombre: 'Portal Santiago Recicla (MMA)', url: 'https://santiagorecicla.mma.gob.cl', desc: 'Puntos limpios regionales para latas de aluminio.' }
    ],
    linksReutilizar: [
      { nombre: 'Fundación Basura', url: 'https://www.fundacionbasura.org', desc: 'Talleres de suprarreciclaje para latas.' }
    ],
    videosReutilizar: [
      {
        id: 'DqOcio35YmU',
        titulo: '6 ideas para hacer macetas con latas',
        autor: 'Galletasafortunadas'
      },
      {
        id: 'z8E5ziNvr2A',
        titulo: 'Cómo hacer macetas de latas de aluminio',
        autor: 'Jardín y casa sin filtro'
      }
    ]
  },
  plastico: {
    id: 'plastico',
    nombre: 'Plástico (PET / HDPE)',
    icono: '🍾',
    colorGradient: 'from-emerald-500 to-teal-600',
    colorBorder: 'border-emerald-500/50',
    contenedor: CONTENEDORES_POR_DEFECTO.plastico,
    pasosReciclaje: [
      'Lava y enjuaga el envase plástico.',
      'Retira la tapa y la etiqueta (si es de material distinto).',
      'Aplasta la botella antes de depositarla en el contenedor.'
    ],
    pasosReutilizar: [
      'Transforma botellas en maceteros autorregantes.',
      'Crea embudos caseros o dispensadores.',
      'Conviértelas en ecoladrillos para proyectos de construcción.'
    ],
    linksReciclaje: [
      { nombre: 'Comberplast Chile', url: 'https://www.comberplast.cl', desc: 'Planta de reciclaje y transformación de plásticos.' },
      { nombre: 'Portal Santiago Recicla (MMA)', url: 'https://santiagorecicla.mma.gob.cl', desc: 'Puntos Limpios para plásticos PET 1 y HDPE 2.' }
    ],
    linksReutilizar: [
      { nombre: 'Fundación Basura', url: 'https://www.fundacionbasura.org', desc: 'Guía para confeccionar ecoladrillos.' }
    ],
    videosReutilizar: [
      {
        id: 'lhhggoTyiPY',
        titulo: '3 ideas con botellas de plástico recicladas',
        autor: 'Creativos en Acción'
      },
      {
        id: 'xCaI-5WVRlY',
        titulo: '20 manualidades con botellas de plástico',
        autor: 'GO GREEN'
      }
    ]
  }
};

// Mensajes rotativos de concientización
const MENSAJES_CLIMATICOS = [
  {
    icono: '⏳',
    titulo: 'Tiempos Extremos de Degradación',
    texto: 'Una botella plástica PET tarda más de 500 años en descomponerse. En Chile, menos del 10% del plástico consumido se recicla.'
  },
  {
    icono: '🌊',
    titulo: 'Microplásticos en el Océano',
    texto: 'Para 2050, habrá más plástico que peces en el océano si no reducimos y reciclamos nuestros residuos urbanos.'
  },
  {
    icono: '🌡️',
    titulo: 'Impacto en el Calentamiento Global',
    texto: 'Por cada tonelada de aluminio reciclada, se evita la emisión de casi 9 toneladas de CO₂ a la atmósfera.'
  },
  {
    icono: '🏙️',
    titulo: 'Saturación en Rellenos Sanitarios de la RM',
    texto: 'Los rellenos sanitarios de Santiago (Santa Marta o Tiltil) reciben miles de toneladas diarias de plástico, cartón y latas.'
  }
];

// Galería interactiva del Eco-Simulador: consejos + videos verificados (19-11-2026).
// Las imágenes son miniaturas oficiales descargadas localmente; los videos son de terceros.
const CONSEJOS_GALERIA = [
  {
    id: 'plastico',
    etiqueta: 'Plástico',
    icono: '🍾',
    titulo: 'Enjuaga y aplasta el PET',
    texto: 'Enjuaga la botella, retira la tapa y la etiqueta si son de otro material, y aplástala para que ocupe menos espacio. Así facilitas el reciclaje del plástico PET y HDPE.',
    imagen: '/galeria/plastico.jpg',
    video: {
      id: 'Rn7mCLIew6c',
      titulo: '¿Qué pasa con la basura que generamos?',
      autor: 'EcologíaVerde'
    }
  },
  {
    id: 'carton',
    etiqueta: 'Cartón',
    icono: '📦',
    titulo: 'Cartón limpio, seco y aplastado',
    texto: 'Retira grapas, cintas y restos de comida. Si el cartón está limpio y seco, sepáralo del resto y aplasta las cajas: ocuparás menos espacio en tu casa y en el punto limpio.',
    imagen: '/galeria/carton.jpg',
    video: {
      id: 'M3z-YPsumOw',
      titulo: 'Campaña de concienciación para fomentar el reciclaje',
      autor: 'Ayuntamiento de Móstoles'
    }
  },
  {
    id: 'aluminio',
    etiqueta: 'Aluminio',
    icono: '🥫',
    titulo: 'Una lata bien separada vuelve a ser aluminio',
    texto: 'Vacia y enjuaga la lata, déjala secar y aplástala suavemente. Reciclar aluminio ahorra mucha energía frente a producirlo desde cero.',
    imagen: '/galeria/aluminio.jpg',
    video: {
      id: 'XVoQayZfakE',
      titulo: 'Spot Agüita: ¡Pon la basura en su lugar!',
      autor: 'ANA Perú'
    }
  }
];

// Puntos Limpios RM (Filtrados a Cartón, Plástico y Aluminio)
const PUNTOS_RM = [
  {
    comuna: 'Maipú',
    nombre: 'Punto Limpio Ciudad Satélite',
    direccion: 'Av. Parque Sur con Alcalde Infante Larraín',
    materiales: ['Cartón', 'Plástico PET', 'Aluminio'],
    horario: 'Lun a Sáb: 08:30 - 18:00 hrs'
  },
  {
    comuna: 'Maipú',
    nombre: 'Punto Limpio Parque Tres Poniente',
    direccion: 'Av. Tres Poniente con Borgoño',
    materiales: ['Cartón', 'Plástico HDPE', 'Aluminio'],
    horario: 'Mar a Dom: 09:00 - 17:30 hrs'
  },
  {
    comuna: 'Santiago Centro',
    nombre: 'Punto Limpio Parque Forestal',
    direccion: 'Av. Cardenal José María Caro (frente a Museo Bellas Artes)',
    materiales: ['Cartón', 'Plástico PET', 'Aluminio'],
    horario: 'Lun a Dom: 08:00 - 19:00 hrs'
  },
  {
    comuna: 'Providencia',
    nombre: 'Punto Limpio Parque Inés de Suárez',
    direccion: 'Av. Regimiento de Cazadores 1220',
    materiales: ['Cartón', 'Plástico (PET/HDPE)', 'Aluminio'],
    horario: 'Mar a Dom: 09:00 - 18:00 hrs'
  },
  {
    comuna: 'Las Condes',
    nombre: 'Punto Limpio Parque Araucano',
    direccion: 'Av. Presidente Riesco 5698',
    materiales: ['Cartón', 'Plástico', 'Aluminio'],
    horario: 'Lun a Dom: 08:30 - 20:00 hrs'
  },
  {
    comuna: 'Puente Alto',
    nombre: 'Punto Limpio Mall Plaza Tobalaba',
    direccion: 'Av. Camilo Henríquez 3296',
    materiales: ['Cartón', 'Plástico PET', 'Aluminio'],
    horario: 'Lun a Dom: 10:00 - 19:00 hrs'
  },
  {
    comuna: 'La Florida',
    nombre: 'Punto Limpio Walker Martínez',
    direccion: 'Av. Walker Martínez 2245',
    materiales: ['Cartón', 'Plástico PET/HDPE', 'Aluminio'],
    horario: 'Mar a Sáb: 09:00 - 18:00 hrs'
  },
  {
    comuna: 'Ñuñoa',
    nombre: 'Punto Limpio Plaza Ñuñoa',
    direccion: 'Av. Irarrázaval 3550 (Sector Norte)',
    materiales: ['Cartón', 'Plástico', 'Aluminio'],
    horario: 'Lun a Sáb: 09:00 - 18:00 hrs'
  },
  {
    comuna: 'San Bernardo',
    nombre: 'Punto Limpio Parque Garcia de la Huerta',
    direccion: 'América 504',
    materiales: ['Cartón', 'Plástico PET', 'Aluminio'],
    horario: 'Lun a Vie: 09:00 - 17:00 hrs'
  },
  {
    comuna: 'Peñalolén',
    nombre: 'Ecoparque Peñalolén',
    direccion: 'Av. José Arrieta 10000',
    materiales: ['Cartón', 'Plástico', 'Aluminio'],
    horario: 'Mar a Dom: 09:00 - 17:30 hrs'
  }
];

// Estado “abierto/cerrado” calculado desde el horario ya publicado en la app.
const DIAS = { Dom: 0, Lun: 1, Mar: 2, Mié: 3, Jue: 4, Vie: 5, Sáb: 6 };

function estaAbiertoAhora(punto, fecha = new Date()) {
  const m = String(punto.horario || '').match(/([A-Za-zÁÉÍÓÚáéíóú]+)\s+a\s+([A-Za-zÁÉÍÓÚáéíóú]+).*?(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})/);
  if (!m) return null;
  const desde = DIAS[m[1]] ?? DIAS[m[1].normalize('NFD').replace(/[\u0300-\u036f]/g, '')];
  const hasta = DIAS[m[2]] ?? DIAS[m[2].normalize('NFD').replace(/[\u0300-\u036f]/g, '')];
  if (desde === undefined || hasta === undefined) return null;
  const dia = fecha.getDay();
  const enRango = desde <= hasta ? dia >= desde && dia <= hasta : dia >= desde || dia <= hasta;
  if (!enRango) return false;
  const minutos = fecha.getHours() * 60 + fecha.getMinutes();
  const apertura = Number(m[3]) * 60 + Number(m[4]);
  const cierre = Number(m[5]) * 60 + Number(m[6]);
  return minutos >= apertura && minutos <= cierre;
}

function linkCómoLlegar(punto, ubicacion) {
  const destino = encodeURIComponent(punto.nombre + ', ' + punto.direccion + ', ' + punto.comuna + ', Santiago, Chile');
  if (ubicacion) {
    return 'https://www.google.com/maps/dir/?api=1&origin=' +
      encodeURIComponent(ubicacion.lat + ',' + ubicacion.lon) + '&destination=' + destino;
  }
  return 'https://www.google.com/maps/search/?api=1&query=' + destino;
}

// Reglas automáticas segun los habitos reales cargados desde MySQL.
// El progreso NUNCA se marca a mano: solo se deriva de los escaneos.
const REGLAS_DESAFIOS = {
  1: (s) => (s.materiales.plastico || 0) >= 3,                                  // bolsas reutilizables / compras
  2: (s) => (s.materiales.plastico || 0) >= 3,                                  // donacion de tapitas
  3: (s) => (s.materiales.plastico || 0) >= 1,                                  // ecoladrillo
  4: (s) => ['carton', 'plastico', 'aluminio'].every(m => (s.materiales[m] || 0) > 0) // separacion en origen
};

// Detalle interactivo de cada reto: meta, avance real, material relacionado y
// pasos educativos. Las metas son las mismas que usan las reglas de arriba.
const DETALLES_DESAFIOS = {
  1: {
    meta: 3,
    progreso: (s) => s.materiales.plastico || 0,
    material: 'Plástico',
    unidad: 'escaneos de plástico',
    pasos: ['Escanea un envase plástico en el Eco-Scanner.', 'Repite hasta completar 3 escaneos.', 'Lleva tu bolsa reutilizable a la feria o vega.'],
  },
  2: {
    meta: 3,
    progreso: (s) => s.materiales.plastico || 0,
    material: 'Plástico',
    unidad: 'escaneos de plástico',
    pasos: ['Escanea tapitas y envases plásticos.', 'Junta las tapas limpias y secas.', 'Entrégalas en un punto de donación.'],
  },
  3: {
    meta: 1,
    progreso: (s) => s.materiales.plastico || 0,
    material: 'Plástico',
    unidad: 'escaneos de plástico',
    pasos: ['Escanea una botella PET.', 'Límpiala y rellénala con plásticos flexibles.', 'Úsala como ecoladrillo en tu casa.'],
  },
  4: {
    meta: 3,
    progreso: (s) => ['carton', 'aluminio', 'plastico'].filter((m) => (s.materiales[m] || 0) > 0).length,
    material: 'Todos',
    unidad: 'materiales separados',
    pasos: ['Escanea una pieza de cartón.', 'Escanea una lata de aluminio.', 'Escanea un envase plástico y lleva todo al punto limpio.'],
  },
};

// Trivia educativa: es información, no modifica estadísticas ni desafíos.
const TRIVIA_VERDE = [
  {
    pregunta: '¿Qué material se debe enjuagar y aplastar antes de reciclar?',
    opciones: ['Cartón mojado', 'Botellas PET', 'Latas con comida'],
    correcta: 1,
    explicacion: 'El PET limpio y aplastado ocupa menos espacio y contamina menos el resto del papel.',
  },
  {
    pregunta: '¿Dónde se entregan las tapitas plásticas en este proyecto?',
    opciones: ['A cualquier contenedor de basura', 'A puntos de donación para hospitales', 'Al compostaje'],
    correcta: 1,
    explicacion: 'Las tapas se juntan y se donan a campañas solidarias; no van al compostaje.',
  },
  {
    pregunta: '¿Cuántos materiales detecta el Eco-Scanner?',
    opciones: ['Dos', 'Tres', 'Cinco'],
    correcta: 1,
    explicacion: 'El modelo detecta Cartón, Aluminio y Plástico (mAP@50 oficial 0.562).',
  },
];

export default function App() {
  const [pestaña, setPestaña] = useState('inicio');

  // Estados de escáner y cámara
  const [elementosDetectados, setElementosDetectados] = useState([]);
  const [modosAccion, setModosAccion] = useState({
    carton: 'reciclar',
    aluminio: 'reciclar',
    plastico: 'reciclar'
  });
  const [imagenVista, setImagenVista] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [usandoCamara, setUsandoCamara] = useState(false);
  const [comunaSeleccionada, setComunaSeleccionada] = useState('Todas');
  const [materialSeleccionado, setMaterialSeleccionado] = useState('Todos');
  const [puntosRM, setPuntosRM] = useState(PUNTOS_RM);
  const [puntoMapaActivo, setPuntoMapaActivo] = useState(null);
  const [consejoIndice, setConsejoIndice] = useState(0);
  const [videoAbierto, setVideoAbierto] = useState(null);
  const [ubicacion, setUbicacion] = useState(null);
  const [geoError, setGeoError] = useState('');
  const [errorEscaneo, setErrorEscaneo] = useState('');
  const [confianzas, setConfianzas] = useState({});
  const [ultimoArchivo, setUltimoArchivo] = useState(null);
  const [contenedores, setContenedores] = useState(CONTENEDORES_POR_DEFECTO);

  // Interactividad del Desafío Verde (no altera los datos: solo navega y explica).
  const [desafioAbierto, setDesafioAbierto] = useState(null);
  const [retoActivo, setRetoActivo] = useState(null);
  const [triviaIndice, setTriviaIndice] = useState(0);
  const [triviaOpcion, setTriviaOpcion] = useState(null);
  const [triviaAciertos, setTriviaAciertos] = useState(0);
  const [triviaRespondidas, setTriviaRespondidas] = useState(0);
  const [celebracion, setCelebracion] = useState(false);

  // Impacto del Eco-Simulador: solo lectura, calculado en MySQL desde los escaneos.
  const [impacto, setImpacto] = useState(null);
  
  // Refs
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const sesionRef = useRef(null);

  // Estadísticas reales del usuario: se actualizan solas con cada escaneo.
  const [estadisticas, setEstadisticas] = useState({
    totalEscaneos: 0,
    materiales: { carton: 0, aluminio: 0, plastico: 0 }
  });

  // Catálogo de hábitos; el estado "completado" se calcula, nunca se marca a mano.
  const [desafios, setDesafios] = useState([
    {
      id: 1,
      titulo: 'Separación de Cartón, Plástico y Aluminio',
      desc: 'Escanea los tres materiales para completar la separación en origen.',
      icono: '♻️'
    },
    {
      id: 2,
      titulo: 'Dona Tapitas a Damas de Café',
      desc: 'Escanea 3 envases plásticos para registrar tu aporte.',
      icono: '❤️'
    },
    {
      id: 3,
      titulo: 'Compacta tus Envasados',
      desc: 'Alcanza 5 escaneos de envases.',
      icono: '🗜️'
    },
    {
      id: 4,
      titulo: 'Entrega en Punto Limpio Comunales',
      desc: 'Alcanza 10 escaneos y llevarás un registro de tus entregas.',
      icono: '📍'
    }
  ]);

  const [indexMensaje, setIndexMensaje] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndexMensaje((prevIndex) => (prevIndex + 1) % MENSAJES_CLIMATICOS.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  // Detener transmisión de cámara al cambiar de pestaña o desmontar
  useEffect(() => {
    return () => {
      detenerCamara();
    };
  }, [pestaña]);

  // Sesión anónima: permite contar solo las fotos enviadas por este usuario.
  const asegurarSesion = async () => {
    if (sesionRef.current) return sesionRef.current;
    let id = null;
    try { id = localStorage.getItem('ecolearn_id_sesion'); } catch (e) { id = null; }
    if (!id) {
      try {
        const res = await fetch(API_URL + '/db/sesiones', { method: 'POST' });
        if (res.ok) {
          const datos = await res.json();
          id = datos.id_sesion;
        }
      } catch (e) { id = null; }
      if (!id) id = 'local-' + Date.now() + '-' + Math.random().toString(36).slice(2);
      try { localStorage.setItem('ecolearn_id_sesion', id); } catch (e) { /* modo privado */ }
    }
    sesionRef.current = id;
    return id;
  };

  // Refresca impacto y estadísticas leyendo MySQL; se llama al cargar y tras cada escaneo.
  const refrescarImpacto = async () => {
    const id = await asegurarSesion();
    const res = await fetch(API_URL + '/db/impacto?id_sesion=' + encodeURIComponent(id));
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const datos = await res.json();
    setImpacto(datos);
    setEstadisticas({
      totalEscaneos: datos.escaneos,
      materiales: { carton: 0, aluminio: 0, plastico: 0, ...(datos.materiales || {}) }
    });
    return datos;
  };

  useEffect(() => {
    refrescarImpacto().catch(() => {});
  }, []);

  // Catálogos reales desde el backend, con respaldo local si no responde.
  useEffect(() => {
    const base = API_URL;
    fetch(base + '/db/materiales')
      .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
      .then(filas => {
        if (!Array.isArray(filas) || filas.length === 0) return;
        const mapa = { ...CONTENEDORES_POR_DEFECTO };
        filas.forEach(f => {
          const nombre = norm(f.nombre || '');
          if (nombre.includes('carton') || nombre.includes('papel')) mapa.carton = f.contenedor || mapa.carton;
          else if (nombre.includes('plastico')) mapa.plastico = f.contenedor || mapa.plastico;
          else if (nombre.includes('aluminio')) mapa.aluminio = f.contenedor || mapa.aluminio;
        });
        setContenedores(mapa);
      })
      .catch(() => {});

    fetch(base + '/db/puntos')
      .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
      .then(filas => {
        if (!Array.isArray(filas) || filas.length === 0) return;
        setPuntosRM(filas.map(p => ({
          comuna: p.comuna,
          nombre: p.nombre,
          direccion: p.direccion,
          horario: p.horario,
          materiales: String(p.materiales || '').split(',').map(m => m.trim()).filter(Boolean),
          lat: p.lat === null || p.lat === undefined ? null : Number(p.lat),
          lon: p.lon === null || p.lon === undefined ? null : Number(p.lon),
          fuente: p.fuente || 'investigacion_propia',
          nota: p.nota || '',
          coordsAproximadas: p.coords_aproximadas === 1 || p.coords_aproximadas === true,
        })));
      })
      .catch(() => {});

    fetch(base + '/db/habitos')
      .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
      .then(filas => {
        if (!Array.isArray(filas) || filas.length === 0) return;
        const iconos = ['🛍️', '❤️', '🧱', '♻️'];
        setDesafios(filas.map((h, i) => ({
          id: h.id_habito,
          titulo: h.titulo,
          desc: h.descripcion,
          icono: iconos[i % iconos.length]
        })));
      })
      .catch(() => {});
  }, []);

  const mensajeActual = MENSAJES_CLIMATICOS[indexMensaje];

  const norm = (s) => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  const distanciaKm = (lat1, lon1, lat2, lon2) => {
    const r = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
    return 2 * r * Math.asin(Math.sqrt(a));
  };

  const comunasDisponibles = ['Todas', ...Array.from(new Set(puntosRM.map(p => p.comuna)))];
  const materialesDisponibles = ['Todos', 'Cartón', 'Plástico', 'Aluminio', 'Reciclables (por confirmar)'];
  const puntosFiltrados = puntosRM.filter(p => {
    const porComuna = comunaSeleccionada === 'Todas' || p.comuna === comunaSeleccionada;
    const porMaterial = materialSeleccionado === 'Todos' ||
      p.materiales.some(m => norm(m).includes(norm(materialSeleccionado)));
    return porComuna && porMaterial;
  }).map(p => ({
    ...p,
    distanciaKm: ubicacion && p.lat !== null && p.lon !== null
      ? distanciaKm(ubicacion.lat, ubicacion.lon, p.lat, p.lon)
      : null
  })).sort((a, b) => {
    if (a.distanciaKm === null || b.distanciaKm === null) return a.nombre.localeCompare(b.nombre);
    return a.distanciaKm - b.distanciaKm;
  });

  const toggleModoAccion = (matId, modo) => {
    setModosAccion(prev => ({ ...prev, [matId]: modo }));
  };

  // Acceso flexible a Cámara Web (Laptop/PC) o Trasera (Móviles)
  const iniciarCamara = async () => {
    detenerCamara();
    setImagenVista(null);
    setElementosDetectados([]);
    try {
      let stream;
      try {
        // 1. Intenta primero cámara trasera (móviles)
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
        });
      } catch (e) {
        // 2. Si falla (por ejemplo en Laptop/PC sin cámara trasera), solicita webcam genérica
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }
      streamRef.current = stream;
      setUsandoCamara(true);
    } catch (err) {
      alert("No se pudo acceder a la cámara. Asegúrate de dar permisos en tu navegador o verificar que otra aplicación no la esté utilizando.");
      console.error("Error al acceder a la cámara:", err);
    }
  };

  useEffect(() => {
    if (usandoCamara && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
    }
  }, [usandoCamara]);

  const detenerCamara = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setUsandoCamara(false);
  };

  const capturarFoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const dataUrl = canvas.toDataURL('image/jpeg');
    setImagenVista(dataUrl);
    detenerCamara();

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'captura_camara.jpg', { type: 'image/jpeg' });
        procesarPrediccionBackend(file);
      }
    }, 'image/jpeg');
  };

  // Cálculos del Eco-Simulador: vienen del backend, nunca se editan en la pantalla.
  const impactoActual = impacto || {
    escaneos: estadisticas.totalEscaneos,
    materiales: estadisticas.materiales,
    impacto: { agua_litros: 0, co2_kg: 0, residuos_kg: 0 },
    equivalencias: { duchas_5min: 0, km_auto: 0 },
    ventana_dias: 30
  };
  const aguaAhorradaL = Number(impactoActual.impacto?.agua_litros || 0);
  const duchasEquivalentes = Number(impactoActual.equivalencias?.duchas_5min ?? (aguaAhorradaL / 60).toFixed(1));
  const co2EvitadoKg = Number(impactoActual.impacto?.co2_kg || 0).toFixed(2);
  const kmRedMovilidad = Number(impactoActual.equivalencias?.km_auto ?? (Number(co2EvitadoKg) * 7.5).toFixed(1));
  const kgBasuraDesviada = Number(impactoActual.impacto?.residuos_kg || 0).toFixed(2);

  // Galería: solo navega entre información, nunca modifica los datos del simulador.
  const consejoActual = CONSEJOS_GALERIA[consejoIndice];
  const moverConsejo = (paso) =>
    setConsejoIndice((i) => (i + paso + CONSEJOS_GALERIA.length) % CONSEJOS_GALERIA.length);

  const desafiosAuto = desafios.map(d => ({
    ...d,
    completado: Boolean(REGLAS_DESAFIOS[d.id] && REGLAS_DESAFIOS[d.id](estadisticas))
  }));
  const completadosCount = desafiosAuto.filter(d => d.completado).length;
  const porcentajeDesafios = Math.round((completadosCount / (desafiosAuto.length || 1)) * 100);
  const retoActivoActual = desafiosAuto.find(d => d.id === retoActivo) || null;

  const responderTrivia = (indiceOpcion) => {
    if (triviaOpcion !== null) return;
    setTriviaOpcion(indiceOpcion);
    setTriviaRespondidas((n) => n + 1);
    if (indiceOpcion === TRIVIA_VERDE[triviaIndice].correcta) {
      setTriviaAciertos((n) => n + 1);
    }
  };

  const siguienteTrivia = () => {
    setTriviaIndice((i) => (i + 1) % TRIVIA_VERDE.length);
    setTriviaOpcion(null);
  };

  // Felicitación fugaz cuando un reto se completa solo con un escaneo nuevo.
  const completadosPrevios = useRef(completadosCount);
  useEffect(() => {
    if (completadosCount > completadosPrevios.current) {
      setCelebracion(true);
      const temporizador = setTimeout(() => setCelebracion(false), 5000);
      completadosPrevios.current = completadosCount;
      return () => clearTimeout(temporizador);
    }
    completadosPrevios.current = completadosCount;
  }, [completadosCount]);

  // Procesa la imagen mediante API backend (sin resultados falsos si falla)
  const procesarPrediccionBackend = async (file) => {
    setCargando(true);
    setErrorEscaneo('');
    setElementosDetectados([]);
    setConfianzas({});
    setUltimoArchivo(file);

    const controller = new AbortController();
    const temporizador = setTimeout(() => controller.abort(), 10000);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('id_sesion', await asegurarSesion());
      const res = await fetch(API_URL + '/predict', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });
      if (!res.ok) {
        let detalle = null;
        try { detalle = await res.json(); } catch (e) { detalle = null; }
        const codigo = detalle?.detail?.codigo || detalle?.detail;
        if (codigo === 'BORROSA') {
          throw new Error('La foto salió borrosa. Toma otra con buena luz y sin movimiento.');
        }
        throw new Error('HTTP ' + res.status);
      }
      const data = await res.json();

      if ((data.detecciones_rechazadas || []).length > 0 && (data.detecciones || []).length === 0) {
        setUltimoArchivo(file);
        setErrorEscaneo('La confianza fue menor al ' + Math.round((data.umbral_confianza || 0.5) * 100) + '%. Repite la captura con la etiqueta bien visible.');
        return;
      }

      const encontrados = new Set();
      const conf = {};
      (data.detecciones || []).forEach((item) => {
        const c = (item.clase || '').toLowerCase();
        let material = null;
        if (['carton', 'cartón', 'paper', 'cardboard', 'caja', 'papel'].some(k => c.includes(k))) material = 'carton';
        else if (['lata', 'can', 'aluminio', 'metal'].some(k => c.includes(k))) material = 'aluminio';
        else if (['plastico', 'plástico', 'plastic', 'botella', 'pet', 'hdpe'].some(k => c.includes(k))) material = 'plastico';
        if (material) {
          encontrados.add(material);
          const valor = Number(item.confianza) || 0;
          conf[material] = Math.max(conf[material] || 0, valor);
        }
      });

      if (encontrados.size === 0) {
        setErrorEscaneo('La imagen se analizó, pero no se detectaron cartón, plástico ni aluminio. Prueba con otra foto más clara.');
        return;
      }
      setElementosDetectados(Array.from(encontrados));
      setConfianzas(conf);
      // La métrica se vuelve a leer desde MySQL: nadie la modifica a mano.
      try { await refrescarImpacto(); } catch (e) { /* conserva el último valor válido */ }
    } catch (e) {
      const motivo = e.name === 'AbortError'
        ? 'El análisis superó los 10 segundos.'
        : 'No se pudo analizar la imagen en este momento.';
      setErrorEscaneo(motivo + ' Revisa tu conexión y vuelve a intentarlo.');
    } finally {
      clearTimeout(temporizador);
      setCargando(false);
    }
  };

  const convertirSiEsHeic = async (file) => {
    const nombre = (file.name || '').toLowerCase();
    const tipo = (file.type || '').toLowerCase();
    if (!tipo.includes('heic') && !tipo.includes('heif') && !nombre.endsWith('.heic') && !nombre.endsWith('.heif')) {
      return file;
    }
    const { default: heic2any } = await import('heic2any');
    const convertido = await heic2any({ blob: file, toType: 'image/jpeg', quality: 0.9 });
    const blob = Array.isArray(convertido) ? convertido[0] : convertido;
    return new File([blob], nombre.replace(/\.(heic|heif)$/, '.jpg'), {
      type: 'image/jpeg',
      lastModified: Date.now(),
    });
  };

  const handleSubirArchivo = async (e) => {
    detenerCamara();
    const file = e.target.files[0];
    if (!file) return;
    const nombre = (file.name || '').toLowerCase();
    const esImagen = file.type.startsWith('image/') || /\.(heic|heif|jpg|jpeg|png|webp)$/.test(nombre);
    if (!esImagen) {
      setErrorEscaneo('Formato no soportado. Sube una imagen JPG, PNG, WEBP, HEIC o HEIF.');
      e.target.value = '';
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorEscaneo('La imagen supera el límite de 10 MB. Elije una foto más pequeña.');
      e.target.value = '';
      return;
    }
    try {
      const archivo = await convertirSiEsHeic(file);
      const reader = new FileReader();
      reader.onload = (event) => setImagenVista(event.target.result);
      reader.readAsDataURL(archivo);
      procesarPrediccionBackend(archivo);
    } catch (err) {
      setErrorEscaneo('No se pudo convertir la foto HEIC/HEIF. Prueba exportándola como JPEG.');
      console.error(err);
    }
    e.target.value = '';
  };

  const reintentarEscaneo = () => {
    if (ultimoArchivo) procesarPrediccionBackend(ultimoArchivo);
  };

  const usarMiUbicacion = () => {
    setGeoError('');
    if (!navigator.geolocation) {
      setGeoError('Este navegador no permite geolocalización. Puedes usar “Cómo llegar” sin tu ubicación.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setUbicacion({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      () => setGeoError('No se obtuvo tu ubicación. Revisa el permiso del navegador o usa “Cómo llegar” sin ella.'),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  return (
    <div className="min-h-[100dvh] overflow-x-hidden bg-[#041016] text-slate-100 font-sans p-4 sm:p-6 md:p-10 selection:bg-emerald-500 selection:text-slate-950">
      
      {/* Header EcoLearn */}
      <header className="max-w-5xl mx-auto mb-6 pb-6 border-b border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-2xl">
              🌱
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                EcoLearn Chile
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                RM v2.5
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Clasificación IA: Cartón • Plástico • Aluminio</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 text-slate-300 border border-slate-800 text-xs font-semibold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Ley REP Chile 20.920
          </span>
        </div>
      </header>

      {/* Navegación Superior */}
      <nav className="max-w-5xl mx-auto mb-8 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800 flex flex-wrap gap-1 shadow-lg">
        <button
          onClick={() => setPestaña('inicio')}
          className={`flex-1 min-w-[110px] py-3 px-3 rounded-xl font-bold text-xs sm:text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
            pestaña === 'inicio'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
          }`}
        >
          <span>🏠</span> Menú Principal
        </button>

        <button
          onClick={() => setPestaña('escaner')}
          className={`flex-1 min-w-[110px] py-3 px-3 rounded-xl font-bold text-xs sm:text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
            pestaña === 'escaner'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
          }`}
        >
          <span>📸</span> Escáner IA
        </button>

        <button
          onClick={() => setPestaña('puntos_rm')}
          className={`flex-1 min-w-[110px] py-3 px-3 rounded-xl font-bold text-xs sm:text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
            pestaña === 'puntos_rm'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
          }`}
        >
          <span>📍</span> Puntos Limpios RM
        </button>

        <button
          onClick={() => setPestaña('simulador')}
          className={`flex-1 min-w-[110px] py-3 px-3 rounded-xl font-bold text-xs sm:text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
            pestaña === 'simulador'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
          }`}
        >
          <span>📊</span> Eco-Simulador RM
        </button>

        <button
          onClick={() => setPestaña('desafio')}
          className={`flex-1 min-w-[110px] py-3 px-3 rounded-xl font-bold text-xs sm:text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
            pestaña === 'desafio'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
          }`}
        >
          <span>🏆</span> Desafío Verde RM
        </button>

      </nav>

      {/* CONTENIDO PRINCIPAL */}
      <main className="max-w-5xl mx-auto space-y-8">

        {/* ---------------- PESTAÑA 0: MENÚ PRINCIPAL ---------------- */}
        {pestaña === 'inicio' && (
          <div className="space-y-10 animate-fade-in">
            {/* Hero Section */}
            <section className="bg-gradient-to-br from-slate-900 via-teal-950/40 to-slate-950 border border-slate-800 rounded-3xl p-8 sm:p-12 text-center relative overflow-hidden shadow-2xl">
              <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-emerald-500/10 rounded-full pointer-events-none"></div>
              <div className="max-w-2xl mx-auto space-y-4 relative z-10">
                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-widest inline-block">
                  Plataforma Educativa & Ambiental Chile
                </span>
                <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
                  Inteligencia Artificial al servicio del <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">Planeta</span>
                </h2>
                <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
                  EcoLearn Chile nació para transformar la cultura del reciclaje en la Región Metropolitana, combinando visión por computadora y educación comunitaria para dar un destino limpio a nuestros residuos.
                </p>
                <div className="pt-4 flex flex-wrap justify-center gap-3">
                  <button 
                    onClick={() => setPestaña('escaner')}
                    className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black text-xs sm:text-sm shadow-xl shadow-emerald-500/20 transition-all hover:scale-105 cursor-pointer"
                  >
                    📸 Probar Escáner IA
                  </button>
                  <button 
                    onClick={() => setPestaña('puntos_rm')}
                    className="px-6 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-bold text-xs sm:text-sm transition-all hover:scale-105 cursor-pointer"
                  >
                    📍 Buscar Puntos Limpios
                  </button>
                </div>
              </div>
            </section>

            {/* ¿Por qué creamos esta plataforma? */}
            <section className="space-y-6">
              <div className="text-center max-w-xl mx-auto">
                <h3 className="text-2xl font-black text-white">¿Por qué creamos EcoLearn Chile?</h3>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  Tres pilares fundamentales que impulsaron el desarrollo de esta herramienta.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-2xl">
                    🧠
                  </div>
                  <h4 className="text-lg font-bold text-white">Confusión al Clasificar</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Muchos ciudadanos quieren reciclar pero no saben exactamente cómo preparar cada material (retirar tapas, secar o lavar), provocando que lotes enteros se contaminen y terminen en vertederos.
                  </p>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center text-2xl">
                    🇨🇱
                  </div>
                  <h4 className="text-lg font-bold text-white">Apoyo a la Ley REP</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    La Ley de Responsabilidad Extendida del Productor (Ley 20.920) exige metas ambiciosas de recolección. EcoLearn acerca esta normativa a las personas facilitando la acción ciudadana diaria.
                  </p>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center text-2xl">
                    🏙️
                  </div>
                  <h4 className="text-lg font-bold text-white">Crisis de Vertederos RM</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Los rellenos sanitarios de la Región Metropolitana están al límite de su capacidad. Fomentar la reducción, reutilización y reciclaje de cartón, plástico y aluminio es urgente.
                  </p>
                </div>
              </div>
            </section>

            {/* Datos Interesantes & Impacto */}
            <section className="bg-slate-950/80 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
              <div className="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-xl font-black text-emerald-400 flex items-center gap-2">
                    <span>📊</span> Datos Interesantes sobre Reciclaje en Chile
                  </h3>
                  <p className="text-xs text-slate-400">Estadísticas clave para tomar conciencia de nuestro impacto.</p>
                </div>
                <span className="text-[10px] bg-slate-900 text-slate-400 px-3 py-1 rounded-full border border-slate-800 self-start sm:self-auto">
                  Fuente: MMA & Alianza Basura Cero
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 text-center">
                  <span className="text-3xl sm:text-4xl font-black text-emerald-400 block mb-1">&lt;10%</span>
                  <span className="text-[11px] font-bold text-slate-200 block">Tasa de Reciclaje</span>
                  <p className="text-[10px] text-slate-400 mt-1">Del plástico domiciliario en Chile es reciclado actualmente.</p>
                </div>

                <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 text-center">
                  <span className="text-3xl sm:text-4xl font-black text-amber-400 block mb-1">500+</span>
                  <span className="text-[11px] font-bold text-slate-200 block">Años de Degradación</span>
                  <p className="text-[10px] text-slate-400 mt-1">Tarda una botella PET en desintegrarse en la naturaleza.</p>
                </div>

                <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 text-center">
                  <span className="text-3xl sm:text-4xl font-black text-teal-400 block mb-1">95%</span>
                  <span className="text-[11px] font-bold text-slate-200 block">Ahorro Energético</span>
                  <p className="text-[10px] text-slate-400 mt-1">Al reciclar latas de aluminio en comparación a extraer material virgen.</p>
                </div>

                <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 text-center">
                  <span className="text-3xl sm:text-4xl font-black text-cyan-400 block mb-1">10</span>
                  <span className="text-[11px] font-bold text-slate-200 block">Puntos Limpios RM</span>
                  <p className="text-[10px] text-slate-400 mt-1">Con dirección, horario y ruta en Google Maps.</p>
                </div>
              </div>
            </section>

            {/* Módulos del Sistema */}
            <section className="space-y-4">
              <h3 className="text-xl font-bold text-white text-center">Módulos de la Plataforma</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div onClick={() => setPestaña('escaner')} className="bg-slate-900/40 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 p-5 rounded-2xl cursor-pointer transition-all">
                  <span className="text-2xl block mb-2">📸</span>
                  <h4 className="text-sm font-bold text-white">Escáner IA</h4>
                  <p className="text-xs text-slate-400 mt-1">Sube o toma una foto para identificar cartón, latas o plásticos al instante.</p>
                </div>

                <div onClick={() => setPestaña('puntos_rm')} className="bg-slate-900/40 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 p-5 rounded-2xl cursor-pointer transition-all">
                  <span className="text-2xl block mb-2">📍</span>
                  <h4 className="text-sm font-bold text-white">Puntos Limpios</h4>
                  <p className="text-xs text-slate-400 mt-1">Encuentra centros de acopio autorizados según tu comuna en la RM.</p>
                </div>

                <div onClick={() => setPestaña('simulador')} className="bg-slate-900/40 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 p-5 rounded-2xl cursor-pointer transition-all">
                  <span className="text-2xl block mb-2">📊</span>
                  <h4 className="text-sm font-bold text-white">Eco-Simulador</h4>
                  <p className="text-xs text-slate-400 mt-1">Calcula los litros de agua y kg de CO₂ que ahorras al reciclar.</p>
                </div>

                <div onClick={() => setPestaña('desafio')} className="bg-slate-900/40 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 p-5 rounded-2xl cursor-pointer transition-all">
                  <span className="text-2xl block mb-2">🏆</span>
                  <h4 className="text-sm font-bold text-white">Desafío Verde</h4>
                  <p className="text-xs text-slate-400 mt-1">Completa metas ecológicas e impulsa un cambio positivo en tu hogar.</p>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ---------------- PESTAÑA 1: ESCÁNER IA ---------------- */}
        {pestaña === 'escaner' && (
          <div className="space-y-8 animate-fade-in">

            {/* Banner Dinámico Rotativo */}
            <div className="bg-gradient-to-r from-teal-950/80 via-slate-900 to-slate-950 border border-teal-500/40 rounded-2xl p-4 shadow-lg flex items-center justify-between gap-4 transition-all duration-500">
              <div className="flex items-center gap-3">
                <span className="text-3xl animate-bounce">{mensajeActual.icono}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                      Impacto Ambiental Santiago
                    </span>
                    <h4 className="text-xs sm:text-sm font-bold text-white">{mensajeActual.titulo}</h4>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {mensajeActual.texto}
                  </p>
                </div>
              </div>

              <button 
                onClick={() => setIndexMensaje((prev) => (prev + 1) % MENSAJES_CLIMATICOS.length)}
                className="hidden sm:block p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 shrink-0 transition-all cursor-pointer"
                title="Siguiente dato"
              >
                ➡️ Siguiente
              </button>
            </div>

            {/* SECCIÓN DE CÁMARA / SUBIDA DE IMAGEN */}
            <section className="glass-panel rounded-3xl p-6 sm:p-10 relative overflow-hidden shadow-2xl text-center bg-slate-950/60 border border-slate-800">
              <div className="max-w-xl mx-auto space-y-5 flex flex-col items-center">
                
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
                  ✨ Detección Inteligente YOLOv11
                </div>

                <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
                  Usa tu cámara o sube una imagen
                </h2>

                <p className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-md">
                  Activa la cámara web de tu ordenador o móvil para tomar una foto en tiempo real, o selecciona una foto desde tu galería.
                </p>

                {/* El reto elegido en Desafío Verde guía al usuario, sin marcar metas a mano */}
                {retoActivoActual && (
                  <div data-testid="reto-activo" className="w-full max-w-md flex items-center justify-between gap-3 px-4 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-left">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-wide text-emerald-400">🎯 Reto activo</p>
                      <p className="text-xs font-bold text-white">{retoActivoActual.titulo}</p>
                      <p className="text-[11px] text-slate-400">
                        {(() => {
                          const d = DETALLES_DESAFIOS[retoActivoActual.id];
                          return d ? `${Math.min(d.progreso(estadisticas), d.meta)} de ${d.meta} ${d.unidad}` : 'Escanea para avanzar';
                        })()}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setRetoActivo(null)}
                      aria-label="Cerrar reto activo"
                      className="shrink-0 px-2 py-1 rounded-lg border border-slate-700 text-slate-400 hover:text-white text-xs cursor-pointer"
                    >
                      ✕
                    </button>
                  </div>
                )}

                {/* Input oculto para subir archivo */}
                <input 
                  type="file" 
                  accept="image/*,.heic,.heif,image/heic,image/heif" 
                  ref={fileInputRef} 
                  className="hidden" 
                  onChange={handleSubirArchivo} 
                />

                {/* BOTONES PRINCIPALES DE OPCIONES */}
                {!usandoCamara && (
                  <div className="pt-2 flex flex-col sm:flex-row justify-center items-center gap-3 w-full">
                    <button 
                      onClick={iniciarCamara}
                      className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black text-sm shadow-xl shadow-emerald-500/20 transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <span className="text-lg">📷</span> Usar Cámara en Vivo
                    </button>

                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-bold text-sm transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2 cursor-pointer"
                    >
                      <span className="text-lg">📁</span> Elegir foto
                    </button>
                  </div>
                )}

                {/* VISUALIZADOR DE CÁMARA EN TIEMPO REAL */}
                {usandoCamara && (
                  <div className="w-full max-w-md mt-2 space-y-3">
                    <div className="relative rounded-2xl overflow-hidden border border-emerald-500/50 shadow-2xl bg-slate-950">
                      <video 
                        ref={videoRef} 
                        autoPlay 
                        playsInline 
                        muted
                        className="w-full h-64 object-cover"
                      ></video>
                      <div className="absolute top-3 left-3 bg-slate-900/95 text-emerald-400 text-[10px] font-bold px-2.5 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                        Cámara Activa
                      </div>
                    </div>

                    <div className="flex justify-center gap-3">
                      <button 
                        onClick={capturarFoto}
                        className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs shadow-lg transition-all flex items-center gap-2 cursor-pointer"
                      >
                        📸 Capturar Foto
                      </button>
                      <button 
                        onClick={detenerCamara}
                        className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs border border-slate-700 transition-all cursor-pointer"
                      >
                        ❌ Cancelar
                      </button>
                    </div>
                  </div>
                )}

                {cargando && (
                  <div className="flex items-center justify-center gap-3 text-xs text-emerald-400 font-medium pt-2">
                    <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
                    Analizando residuos con EcoLearn...
                  </div>
                )}

                {errorEscaneo && !cargando && (
                  <div className="w-full max-w-md rounded-2xl border border-amber-500/40 bg-amber-950/30 p-4 text-left" role="alert">
                    <p className="text-xs font-bold text-amber-300">⚠️ No se pudo completar el análisis</p>
                    <p className="text-[11px] text-amber-100/80 mt-1">{errorEscaneo}</p>
                    {ultimoArchivo && (
                      <button
                        onClick={reintentarEscaneo}
                        className="mt-3 px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-black cursor-pointer"
                      >
                        🔁 Reintentar
                      </button>
                    )}
                  </div>
                )}

                {/* VISTA PREVIA DE IMAGEN CAPTURADA O CARGADA */}
                {imagenVista && !usandoCamara && (
                  <div className="w-full max-w-md mt-4 relative group rounded-2xl overflow-hidden border border-slate-700/60 shadow-xl bg-slate-950 mx-auto">
                    <img 
                      src={imagenVista} 
                      alt="Vista previa" 
                      className="w-full h-64 object-cover object-center"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80"></div>
                    <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center">
                      <span className="text-[11px] font-bold bg-slate-900/90 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700">
                        🖼️ Imagen Procesada
                      </span>
                      {elementosDetectados.length > 0 && (
                        <span className="text-[11px] font-bold bg-emerald-500 text-slate-950 px-2.5 py-1 rounded-lg shadow">
                          {elementosDetectados.length} material(es) detectado(s)
                        </span>
                      )}
                    </div>
                  </div>
                )}

              </div>
            </section>

            {/* ESTADO VACÍO */}
            {elementosDetectados.length === 0 && !cargando && !usandoCamara && !errorEscaneo && (
              <div className="text-center py-12 px-4 border border-dashed border-slate-800 rounded-3xl bg-slate-950/40">
                <span className="text-4xl block mb-2">🔍</span>
                <h3 className="text-base font-bold text-slate-300">Esperando imagen...</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                  Al capturar o elegir una imagen, EcoLearn identificará si contiene Cartón, Aluminio o Plástico y te desplegará la guía exacta para cada material.
                </p>
              </div>
            )}

            {/* RESULTADOS DE DETECCIÓN MULTIMATERIAL */}
            {elementosDetectados.length > 0 && (
              <div className="space-y-6 animate-fade-in">
                
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
                    <span>🎯</span> Materiales Identificados ({elementosDetectados.length}):
                  </h3>
                  <span className="text-xs text-slate-400">Instrucciones específicas por residuo</span>
                </div>

                {elementosDetectados.map((matKey) => {
                  const infoMat = GUIA_RESIDUOS_CHILE[matKey];
                  if (!infoMat) return null;

                  const modoActual = modosAccion[matKey] || 'reciclar';

                  return (
                    <section key={matKey} className="rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 border border-slate-800 bg-slate-950/60 hover:border-emerald-500/30 transition-all">
                      
                      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-6 border-b border-slate-800">
                        <div className="flex items-center gap-4">
                          <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${infoMat.colorGradient} flex items-center justify-center text-3xl shadow-lg shrink-0`}>
                            {infoMat.icono}
                          </div>
                          <div>
                            <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest">
                              Residuo Detectado
                            </span>
                            <h3 className="text-2xl sm:text-3xl font-black text-white">{infoMat.nombre}</h3>
                            <p className="text-xs text-slate-400 mt-1">
                              Destino recomendado: <span className="text-slate-200 font-semibold">{contenedores[matKey] || infoMat.contenedor}</span>
                            </p>
                            {matKey === 'aluminio' && (
                              <p className="text-[10px] font-bold text-amber-300/90 mt-0.5">
                                ⚠️ Contenedor según BD: {contenedores.aluminio}. Pendiente de confirmación oficial (brecha B-3 / REC-93).
                              </p>
                            )}
                            {confianzas[matKey] !== undefined && (
                              <p className="text-[11px] font-bold text-cyan-300 mt-1">
                                Confianza del modelo: {Math.round(confianzas[matKey] * 100)}%
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="w-full md:w-auto bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800 flex gap-1">
                          <button
                            onClick={() => toggleModoAccion(matKey, 'reciclar')}
                            className={`flex-1 md:flex-initial px-5 py-2.5 rounded-xl font-extrabold text-xs transition-all duration-300 cursor-pointer ${
                              modoActual === 'reciclar'
                                ? 'bg-emerald-500 text-slate-950 shadow-md'
                                : 'text-slate-400 hover:text-white'
                            }`}
                          >
                            ♻️ ¿Cómo Reciclar?
                          </button>
                          <button
                            onClick={() => toggleModoAccion(matKey, 'reutilizar')}
                            className={`flex-1 md:flex-initial px-5 py-2.5 rounded-xl font-extrabold text-xs transition-all duration-300 cursor-pointer ${
                              modoActual === 'reutilizar'
                                ? 'bg-amber-500 text-slate-950 shadow-md'
                                : 'text-slate-400 hover:text-white'
                            }`}
                          >
                            💡 ¿Cómo Reutilizar?
                          </button>
                        </div>
                      </div>

                      <div className="bg-slate-950/50 rounded-2xl p-5 border border-slate-800/80 space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          📋 Pasos de preparación ({modoActual === 'reciclar' ? 'Reciclaje' : 'Reutilización'}):
                        </h4>
                        <ul className="space-y-2.5 pt-1">
                          {(modoActual === 'reciclar' ? infoMat.pasosReciclaje : infoMat.pasosReutilizar).map((paso, index) => (
                            <li key={index} className="flex items-start gap-3 text-sm text-slate-200 font-medium">
                              <span className="w-5 h-5 rounded-full bg-slate-800 text-emerald-400 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5 border border-slate-700">
                                {index + 1}
                              </span>
                              <span>{paso}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Videos de reutilización: se abren en el modal, sin autoplay */}
                      {modoActual === 'reutilizar' && (
                        <div className="bg-slate-950/50 rounded-2xl p-5 border border-slate-800/80 space-y-3">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                              🎬 Videos: cómo reutilizar {infoMat.nombre.toLowerCase()}
                            </h4>
                            <span className="text-[10px] text-slate-500">YouTube · sin autoplay</span>
                          </div>
                          <div
                            data-testid={`videos-reutilizar-${matKey}`}
                            className="grid grid-cols-1 sm:grid-cols-2 gap-3"
                          >
                            {(infoMat.videosReutilizar || []).map((video) => (
                              <button
                                key={video.id}
                                type="button"
                                data-testid={`video-reutilizar-${video.id}`}
                                aria-label={`Ver video: ${video.titulo}`}
                                onClick={() => setVideoAbierto(video)}
                                className="group flex gap-3 p-2 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-emerald-500/40 text-left cursor-pointer transition-all"
                              >
                                <span className="relative shrink-0 w-28 h-16 rounded-lg overflow-hidden bg-black">
                                  <img
                                    src={`https://img.youtube.com/vi/${video.id}/hqdefault.jpg`}
                                    alt=""
                                    loading="lazy"
                                    className="w-full h-full object-cover"
                                  />
                                  <span className="absolute inset-0 flex items-center justify-center bg-slate-950/30 text-lg group-hover:bg-slate-950/10">
                                    ▶
                                  </span>
                                </span>
                                <span className="min-w-0">
                                  <span className="block text-[11px] font-bold text-white leading-snug">{video.titulo}</span>
                                  <span className="block text-[10px] text-slate-400 mt-1">{video.autor} · YouTube</span>
                                </span>
                              </button>
                            ))}
                          </div>
                          <p className="text-[10px] text-slate-500">
                            Los videos se reproducen solo al abrirlos. Contenido de terceros; EcoLearn no se hace responsable de su contenido.
                          </p>
                        </div>
                      )}

                      <div>
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                          🇨🇱 Enlaces e iniciativas recomendadas para {infoMat.nombre}:
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {(modoActual === 'reciclar' ? infoMat.linksReciclaje : infoMat.linksReutilizar).map((link, idx) => (
                            <a
                              key={idx}
                              href={link.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition-all group"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-sm text-emerald-400 group-hover:underline">
                                  {link.nombre}
                                </span>
                                <span className="text-xs text-slate-400">🔗</span>
                              </div>
                              <p className="text-xs text-slate-400 mt-1">{link.desc}</p>
                            </a>
                          ))}
                        </div>
                      </div>

                    </section>
                  );
                })}
              </div>
            )}

          </div>
        )}

        {/* ---------------- PESTAÑA 2: PUNTOS LIMPIOS RM ---------------- */}
        {pestaña === 'puntos_rm' && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-slate-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="min-w-0">
                  <h2 className="text-2xl font-black text-white">📍 Puntos Limpios RM</h2>
                  <p className="text-xs text-slate-400 mt-1">Estaciones de reciclaje en la Región Metropolitana.</p>
                </div>

                <div className="flex flex-col md:flex-row md:items-center gap-3 shrink-0">
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-400 font-bold">Comuna:</label>
                    <select 
                      value={comunaSeleccionada}
                      onChange={(e) => setComunaSeleccionada(e.target.value)}
                      className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl px-3 py-2 outline-none focus:border-emerald-500 cursor-pointer"
                    >
                      {comunasDisponibles.map((c, i) => (
                        <option key={i} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-400 font-bold">Material:</label>
                    <select
                      value={materialSeleccionado}
                      onChange={(e) => setMaterialSeleccionado(e.target.value)}
                      className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl px-3 py-2 outline-none focus:border-emerald-500 cursor-pointer"
                    >
                      {materialesDisponibles.map((m, i) => (
                        <option key={i} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={usarMiUbicacion}
                    className="px-3 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-bold whitespace-nowrap self-start md:self-auto cursor-pointer hover:bg-emerald-500/20"
                  >
                    📍 Usar mi ubicación
                  </button>
                </div>
              </div>

              <p className="text-[11px] text-amber-300/80">
                Cobertura actual: {puntosRM.length} puntos en {comunasDisponibles.length - 1} comunas de la RM. Incluye puntos de listado externo sin validar oficialmente; materiales sujetos a confirmación (REC-65).
              </p>
              {(ubicacion || geoError) && (
                <div className="flex flex-wrap items-center gap-2 text-[11px]">
                  {ubicacion && (
                    <span className="text-slate-300">
                      Ubicación autorizada: {ubicacion.lat.toFixed(4)}, {ubicacion.lon.toFixed(4)} — puntos ordenados por cercanía.
                    </span>
                  )}
                  {geoError && <span className="text-amber-300">{geoError}</span>}
                </div>
              )}

              {/* Mapa interactivo: mismo dataset filtrado, sin APIs de pago */}
              <div className="space-y-2 pt-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs font-bold text-slate-200">🗺️ Mapa interactivo</p>
                  <span className="text-[11px] text-slate-400">
                    {puntosFiltrados.length} {puntosFiltrados.length === 1 ? 'punto visible' : 'puntos visibles'} · haz clic en un marcador para ver detalles
                  </span>
                </div>
                <MapaPuntos
                  puntos={puntosFiltrados}
                  ubicacion={ubicacion}
                  puntoActivo={puntoMapaActivo}
                  onSeleccionar={setPuntoMapaActivo}
                  estaAbierto={estaAbiertoAhora}
                />
                <p className="text-[10px] text-slate-500">
                  Mapa base © OpenStreetMap / CARTO. Los marcadores usan las coordenadas reales cargadas desde MySQL; arrastra para moverte y usa los controles + / − para acercar.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                {puntosFiltrados.map((punto, idx) => (
                  <div key={idx} className={`bg-slate-900/80 border rounded-2xl p-5 transition-all space-y-3 ${
                    puntoMapaActivo?.nombre === punto.nombre
                      ? 'border-emerald-500/70 shadow-lg shadow-emerald-500/10'
                      : 'border-slate-800 hover:border-emerald-500/30'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {punto.comuna}
                        </span>
                        <h4 className="text-base font-bold text-white mt-1.5">{punto.nombre}</h4>
                        {(punto.fuente === 'listado_externo_2026-11-19' || punto.coordsAproximadas) && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {punto.fuente === 'listado_externo_2026-11-19' && (
                              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                                Externo · sin validar
                              </span>
                            )}
                            {punto.coordsAproximadas && (
                              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-600">
                                Coordenada aproximada
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      <span className="text-xl">🏢</span>
                    </div>

                    <p className="text-xs text-slate-300">📍 {punto.direccion}</p>
                    {punto.nota && <p className="text-[10px] leading-relaxed text-slate-400 italic">{punto.nota}</p>}
                    {punto.distanciaKm !== null && (
                      <p className="text-[11px] font-bold text-cyan-300">📏 A {punto.distanciaKm.toFixed(1)} km de tu ubicación</p>
                    )}
                    <p className="text-xs text-slate-400">🕒 {punto.horario || 'Horario por confirmar'}</p>
                    <div className="flex items-center justify-between gap-2 pt-1">
                      {(() => {
                        const abierto = estaAbiertoAhora(punto);
                        return (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                            abierto === null
                              ? 'bg-slate-800 text-slate-300 border-slate-700'
                              : abierto
                                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                                : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                          }`}>
                            {abierto === null ? 'Horario por confirmar' : abierto ? '● Abierto ahora' : '○ Cerrado ahora'}
                          </span>
                        );
                      })()}
                      <div className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={() => setPuntoMapaActivo(punto)}
                          className="text-[11px] font-bold text-cyan-300 hover:underline cursor-pointer"
                        >
                          🗺️ Ver en mapa
                        </button>
                        <a
                          href={linkCómoLlegar(punto, ubicacion)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] font-bold text-emerald-400 hover:underline"
                        >
                          🧭 Cómo llegar
                        </a>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {punto.materiales.map((m, i) => (
                        <span key={i} className="text-[10px] bg-slate-950 text-slate-300 px-2 py-0.5 rounded border border-slate-800">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ---------------- PESTAÑA 3: ECO-SIMULADOR RM ---------------- */}
        {pestaña === 'simulador' && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-slate-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
              <div>
                <h2 className="text-2xl font-black text-white">📊 Eco-Simulador de Impacto RM</h2>
                <p className="text-xs text-slate-400 mt-1">Impacto real de tus escaneos en los últimos 30 días. Datos de MySQL, sin carga manual.</p>
              </div>

              <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs font-bold text-slate-200">
                    📷 Residuos detectados por IA · últimos {impactoActual.ventana_dias || 30} días
                  </p>
                  <span className="text-[11px] text-slate-400">
                    Escaneos reales: <b className="text-emerald-400">{impactoActual.escaneos ?? 0}</b>
                  </span>
                </div>

                {[
                  { clave: 'plastico', etiqueta: '🍾 Plástico (PET / HDPE)', barra: 'bg-emerald-500', texto: 'text-emerald-400' },
                  { clave: 'aluminio', etiqueta: '🥫 Aluminio', barra: 'bg-sky-400', texto: 'text-sky-300' },
                  { clave: 'carton', etiqueta: '📦 Cartón', barra: 'bg-amber-500', texto: 'text-amber-400' },
                ].map((item) => {
                  const valor = Number((impactoActual.materiales || {})[item.clave] || 0);
                  const maximo = Math.max(1, ...Object.values(impactoActual.materiales || {}).map(Number));
                  return (
                    <div key={item.clave} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-300">{item.etiqueta}</span>
                        <span className={`font-black ${item.texto}`}>{valor} detectados</span>
                      </div>
                      <div className="h-2.5 w-full rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${item.barra} transition-all duration-500`}
                          style={{ width: `${Math.min(100, (valor / maximo) * 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}

                <p className="text-[11px] text-slate-400 border-t border-slate-800 pt-3">
                  Solo lectura: las cantidades las genera el modelo al analizar cada foto. No hay controles manuales.
                </p>
              </div>

              {/* Resultados */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
                  <span className="text-3xl block mb-1">💧</span>
                  <span className="text-2xl font-black text-cyan-400">{aguaAhorradaL} L</span>
                  <p className="text-xs font-bold text-slate-200 mt-1">Agua Conservada</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Equivale a ~{duchasEquivalentes} duchas de 5 min</p>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
                  <span className="text-3xl block mb-1">🌍</span>
                  <span className="text-2xl font-black text-emerald-400">{co2EvitadoKg} kg</span>
                  <p className="text-xs font-bold text-slate-200 mt-1">CO₂ Evitado</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Equivale a ~{kmRedMovilidad} km no recorridos en auto</p>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
                  <span className="text-3xl block mb-1">⚖️</span>
                  <span className="text-2xl font-black text-amber-400">{kgBasuraDesviada} kg</span>
                  <p className="text-xs font-bold text-slate-200 mt-1">Basura Desviada</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">No irá a vertederos de la RM</p>
                </div>
              </div>

              <div className="border-t border-slate-800 pt-5">
                <p className="text-[11px] text-slate-400">
                  🔄 Este indicador se actualiza solo cuando escaneas una imagen en el Eco-Scanner. Fuente: MySQL <code className="text-emerald-400">ecoscan.escaneos</code>.
                </p>
              </div>

              {/* Galería interactiva: solo navega contenido informativo, nunca edita datos */}
              <div className="border-t border-slate-800 pt-6 space-y-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-black text-white">💡 Consejos para reciclar mejor</h3>
                    <p className="text-xs text-slate-400 mt-1">Usa las flechas para cambiar la foto y el consejo. No modifica tus datos.</p>
                  </div>
                  <span className="text-[11px] font-bold text-emerald-300">
                    Consejo {consejoIndice + 1} de {CONSEJOS_GALERIA.length}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-900 min-h-[230px]">
                    <img
                      src={consejoActual.imagen}
                      alt={`Consejo de reciclaje: ${consejoActual.etiqueta}`}
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/10 to-transparent" />
                    <button
                      type="button"
                      aria-label="Consejo anterior"
                      onClick={() => moverConsejo(-1)}
                      className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-950/85 border border-slate-600 text-white text-2xl font-black hover:border-emerald-400 cursor-pointer"
                    >
                      ‹
                    </button>
                    <button
                      type="button"
                      aria-label="Consejo siguiente"
                      onClick={() => moverConsejo(1)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-950/85 border border-slate-600 text-white text-2xl font-black hover:border-emerald-400 cursor-pointer"
                    >
                      ›
                    </button>
                    <span className="absolute bottom-3 left-3 text-[10px] font-bold px-2 py-1 rounded-md bg-emerald-500/90 text-slate-950">
                      {consejoActual.etiqueta}
                    </span>
                  </div>

                  <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between gap-4">
                    <div>
                      <span className="text-2xl">{consejoActual.icono}</span>
                      <h4 className="text-base font-black text-white mt-2">{consejoActual.titulo}</h4>
                      <p className="text-xs text-slate-300 leading-relaxed mt-2">{consejoActual.texto}</p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex gap-1.5">
                        {CONSEJOS_GALERIA.map((c, i) => (
                          <button
                            key={c.id}
                            type="button"
                            aria-label={`Ir al consejo ${i + 1}`}
                            onClick={() => setConsejoIndice(i)}
                            className={`h-2 rounded-full transition-all cursor-pointer ${
                              i === consejoIndice ? 'w-6 bg-emerald-400' : 'w-2 bg-slate-700 hover:bg-slate-600'
                            }`}
                          />
                        ))}
                      </div>
                      <button
                        type="button"
                        onClick={() => setVideoAbierto(consejoActual.video)}
                        className="px-3 py-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 text-xs font-bold hover:bg-emerald-500/20 cursor-pointer"
                      >
                        ▶ Ver video: {consejoActual.video.titulo}
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-bold text-slate-200">🎬 Videos: para qué sirve reciclar</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    Videos de terceros alojados en YouTube. No se reproducen automáticamente.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                    {CONSEJOS_GALERIA.map((c) => (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => setVideoAbierto(c.video)}
                        className="group text-left bg-slate-900/80 border border-slate-800 hover:border-emerald-500/40 rounded-xl p-3 flex gap-3 items-center cursor-pointer transition-all"
                      >
                        <img src={c.imagen} alt="" className="w-20 h-14 object-cover rounded-lg border border-slate-700" />
                        <span className="min-w-0">
                          <span className="block text-[11px] font-bold text-white leading-snug">{c.video.titulo}</span>
                          <span className="block text-[10px] text-slate-400 mt-1">{c.video.autor} · ▶ Ver</span>
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ---------------- PESTAÑA 4: DESAFÍO VERDE RM ---------------- */}
        {pestaña === 'desafio' && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-slate-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">🏆 Desafío Verde Sustentable</h2>
                  <p className="text-xs text-slate-400 mt-1">Toca un reto para ver cómo lograrlo. No hay carga manual: el avance se calcula solo con tus escaneos.</p>
                  {porcentajeDesafios === 100 && (
                    <p className="text-[11px] font-black text-amber-300 mt-2">🥇 Insignia obtenida: Guardián Verde</p>
                  )}
                  {celebracion && (
                    <p data-testid="celebracion" className="text-[11px] font-black text-emerald-300 mt-2">🎉 ¡Reto completado! Sigue escaneando.</p>
                  )}
                </div>

                <div className="bg-slate-900 px-4 py-2 rounded-2xl border border-slate-800 text-right">
                  <span className="text-xs font-bold text-slate-400">Progreso:</span>
                  <span className="text-base font-black text-emerald-400 ml-2">{porcentajeDesafios}%</span>
                  <div className="w-32 h-1.5 bg-slate-800 rounded-full mt-2 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-emerald-400 to-teal-300 rounded-full transition-all duration-500" style={{ width: `${porcentajeDesafios}%` }} />
                  </div>
                  <p className="text-[10px] text-slate-400">Según tus escaneos</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 text-center">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Escaneos</p>
                  <p className="text-2xl font-black text-white">{estadisticas.totalEscaneos}</p>
                </div>
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 text-center">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Cartón</p>
                  <p className="text-2xl font-black text-amber-400">{estadisticas.materiales.carton || 0}</p>
                </div>
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 text-center">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Aluminio</p>
                  <p className="text-2xl font-black text-sky-300">{estadisticas.materiales.aluminio || 0}</p>
                </div>
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 text-center">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Plástico</p>
                  <p className="text-2xl font-black text-emerald-400">{estadisticas.materiales.plastico || 0}</p>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-300">Tus retos <span className="text-xs font-normal text-slate-500">— toca uno para abrirlo</span></h3>
                {desafiosAuto.map((desafio) => {
                  const detalle = DETALLES_DESAFIOS[desafio.id];
                  const meta = detalle ? detalle.meta : 1;
                  const progreso = detalle
                    ? Math.min(detalle.progreso(estadisticas), meta)
                    : (desafio.completado ? 1 : 0);
                  const porcentajeReto = Math.round((progreso / meta) * 100);
                  const abierto = desafioAbierto === desafio.id;
                  return (
                    <div
                      key={desafio.id}
                      data-testid={`desafio-card-${desafio.id}`}
                      className={`rounded-2xl border overflow-hidden transition-all ${
                        desafio.completado
                          ? 'bg-emerald-950/20 border-emerald-500/40'
                          : 'bg-slate-900/60 border-slate-800'
                      }`}
                    >
                      <button
                        type="button"
                        aria-expanded={abierto}
                        aria-label={`Ver detalles de ${desafio.titulo}`}
                        onClick={() => setDesafioAbierto(abierto ? null : desafio.id)}
                        className="w-full p-4 flex items-center justify-between gap-4 text-left cursor-pointer hover:bg-slate-800/40 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{desafio.icono}</span>
                          <div>
                            <h4 className={`text-sm font-bold ${desafio.completado ? 'text-emerald-300 line-through' : 'text-white'}`}>
                              {desafio.titulo}
                            </h4>
                            <p className="text-xs text-slate-400">{desafio.desc}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <div className={`w-6 h-6 rounded-lg border flex items-center justify-center ${
                            desafio.completado ? 'bg-emerald-500 border-emerald-400 text-slate-950 font-black' : 'border-slate-700'
                          }`}>
                            {desafio.completado && '✓'}
                          </div>
                          <span className="text-slate-500 text-xs">{abierto ? '▲' : '▼'}</span>
                        </div>
                      </button>

                      {abierto && (
                        <div data-testid={`desafio-detalle-${desafio.id}`} className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-800/70">
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-400 rounded-full transition-all duration-500" style={{ width: `${porcentajeReto}%` }} />
                            </div>
                            <span className="text-[11px] font-bold text-emerald-300 shrink-0">{progreso}/{meta}</span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            {progreso} de {meta} {detalle ? detalle.unidad : 'escaneos'} · {porcentajeReto}%
                          </p>
                          {detalle && (
                            <ol className="list-decimal list-inside space-y-1 text-xs text-slate-300">
                              {detalle.pasos.map((paso, i) => <li key={i}>{paso}</li>)}
                            </ol>
                          )}
                          <div className="flex flex-wrap gap-2 pt-1">
                            <button
                              type="button"
                              onClick={() => { setRetoActivo(desafio.id); setPestaña('escaner'); }}
                              className="px-3 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black cursor-pointer"
                            >
                              Aceptar reto y escanear
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setMaterialSeleccionado(detalle ? detalle.material : 'Todos');
                                setComunaSeleccionada('Todas');
                                setPestaña('puntos_rm');
                              }}
                              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 cursor-pointer"
                            >
                              Ver puntos limpios
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Trivia: interacción educativa, sin afectar el progreso real */}
            <div className="bg-slate-950/60 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-black text-white">🎮 Reto rápido: trivia del reciclaje</h3>
                  <p className="text-xs text-slate-400 mt-1">Responde para aprender: tus respuestas no cambian los desafíos ni las estadísticas.</p>
                </div>
                <span className="text-xs font-bold text-emerald-300">Aciertos: {triviaAciertos} / {triviaRespondidas}</span>
              </div>

              <div data-testid="trivia-pregunta" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-3">
                <p className="text-sm font-bold text-white">
                  {triviaIndice + 1}. {TRIVIA_VERDE[triviaIndice].pregunta}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {TRIVIA_VERDE[triviaIndice].opciones.map((opcion, i) => {
                    const respondida = triviaOpcion !== null;
                    const esCorrecta = i === TRIVIA_VERDE[triviaIndice].correcta;
                    return (
                      <button
                        key={i}
                        type="button"
                        data-testid={`trivia-opcion-${i}`}
                        disabled={respondida}
                        onClick={() => responderTrivia(i)}
                        className={`px-3 py-2 rounded-xl border text-xs font-bold text-left transition-colors ${
                          respondida && esCorrecta
                            ? 'bg-emerald-500/20 border-emerald-400 text-emerald-200'
                            : respondida && i === triviaOpcion
                              ? 'bg-rose-500/20 border-rose-400 text-rose-200'
                              : 'bg-slate-900 border-slate-700 text-slate-200 hover:border-emerald-500/50 cursor-pointer'
                        }`}
                      >
                        {String.fromCharCode(65 + i)}) {opcion}
                      </button>
                    );
                  })}
                </div>
                {triviaOpcion !== null && (
                  <div data-testid="trivia-feedback" className="text-xs text-slate-300 bg-slate-900 rounded-xl p-3">
                    <span className={`font-black ${triviaOpcion === TRIVIA_VERDE[triviaIndice].correcta ? 'text-emerald-300' : 'text-rose-300'}`}>
                      {triviaOpcion === TRIVIA_VERDE[triviaIndice].correcta ? '✅ Correcto.' : '❌ No exactamente.'}
                    </span>{' '}
                    {TRIVIA_VERDE[triviaIndice].explicacion}
                  </div>
                )}
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={siguienteTrivia}
                    disabled={triviaOpcion === null}
                    className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-bold text-slate-200 border border-slate-700 cursor-pointer"
                  >
                    Siguiente pregunta →
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="max-w-5xl mx-auto mt-12 pt-6 border-t border-slate-800/80 text-center text-xs text-slate-400 space-y-1">
        <p>EcoLearn Chile — Tecnología y Conciencia Ambiental para la Región Metropolitana.</p>
        <p className="text-[10px] text-slate-400">Soporta: Cartón • Plástico PET/HDPE • Latas de Aluminio</p>
      </footer>

      {/* Modal de videos: no autoplay, fuente externa identificada */}
      {videoAbierto && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-label={videoAbierto.titulo}
          onClick={() => setVideoAbierto(null)}
          onKeyDown={(e) => { if (e.key === 'Escape') setVideoAbierto(null); }}
        >
          <div
            className="w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-2xl p-4 space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-sm font-black text-white">{videoAbierto.titulo}</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">{videoAbierto.autor} · YouTube</p>
              </div>
              <button
                type="button"
                aria-label="Cerrar video"
                onClick={() => setVideoAbierto(null)}
                className="w-9 h-9 rounded-full border border-slate-600 text-white font-bold hover:border-emerald-400 cursor-pointer shrink-0"
              >
                ✕
              </button>
            </div>
            <div className="aspect-video w-full rounded-xl overflow-hidden bg-black">
              <iframe
                className="w-full h-full"
                src={`https://www.youtube-nocookie.com/embed/${videoAbierto.id}?rel=0`}
                title={videoAbierto.titulo}
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
            <p className="text-[10px] text-slate-500">
              El video se reproduce solo al abrirlo. Contenido de terceros; EcoLearn no se hace responsable de su contenido.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}