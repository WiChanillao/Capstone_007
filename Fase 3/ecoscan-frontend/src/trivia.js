// Banco de trivia educativa del Desafío Verde (REC-162).
// Todas las afirmaciones están respaldadas por el código de App.jsx vigente en
// main @ 62c73a2; se indican las líneas de origen en cada pregunta. No se
// inventan cifras ni datos legales. Los colores corresponden a la configuración
// de esta app y pueden variar por comuna: ver la señalización local.

export const PREGUNTAS_POR_RONDA = 5;

export const BANCO_TRIVIA = [
  {
    id: 'pet-enjuagar',
    pregunta: '¿Qué material se debe enjuagar y aplastar antes de reciclar?',
    opciones: ['Cartón mojado', 'Botellas PET', 'Latas con comida'],
    correcta: 1,
    explicacion: 'El PET limpio y aplastado ocupa menos espacio y contamina menos el resto del papel.',
    fuente: 'App.jsx:393-396 (banco original)',
  },
  {
    id: 'tapitas-donacion',
    pregunta: '¿Dónde se entregan las tapitas plásticas en este proyecto?',
    opciones: ['A cualquier contenedor de basura', 'A puntos de donación para hospitales', 'Al compostaje'],
    correcta: 1,
    explicacion: 'Las tapas se juntan y se donan a campañas solidarias; no van al compostaje.',
    fuente: 'App.jsx:399-402 (banco original)',
  },
  {
    id: 'materiales-scanner',
    pregunta: '¿Cuántos materiales detecta el Eco-Scanner?',
    opciones: ['Dos', 'Tres', 'Cinco'],
    correcta: 1,
    explicacion: 'El modelo detecta Cartón, Aluminio y Plástico (mAP@50 oficial 0.562).',
    fuente: 'App.jsx:405-408 (banco original)',
  },
  {
    id: 'contenedor-carton',
    pregunta: 'Según la configuración de esta app, ¿qué contenedor corresponde al cartón?',
    opciones: ['Azul', 'Amarillo', 'Gris'],
    correcta: 0,
    explicacion: 'CONTENEDORES_POR_DEFECTO asocia cartón con Contenedor Azul. El color puede variar por comuna; revisa la señalización local.',
    fuente: 'App.jsx:58-62',
  },
  {
    id: 'contenedor-plastico',
    pregunta: 'Según la configuración de esta app, ¿qué contenedor corresponde al plástico?',
    opciones: ['Azul', 'Amarillo', 'Gris'],
    correcta: 1,
    explicacion: 'CONTENEDORES_POR_DEFECTO asocia plástico con Contenedor Amarillo. El color puede variar por comuna; revisa la señalización local.',
    fuente: 'App.jsx:58-62',
  },
  {
    id: 'contenedor-aluminio',
    pregunta: 'Según la configuración de esta app, ¿qué contenedor corresponde al aluminio?',
    opciones: ['Azul', 'Amarillo', 'Gris'],
    correcta: 2,
    explicacion: 'CONTENEDORES_POR_DEFECTO asocia aluminio con Contenedor Gris. El color puede variar por comuna; revisa la señalización local.',
    fuente: 'App.jsx:58-62',
  },
  {
    id: 'carton-seco',
    pregunta: '¿Cómo conviene entregar las cajas de cartón según la galería de la app?',
    opciones: ['Mojadas y arrugadas', 'Limpias, secas y aplastadas', 'Con cinta adhesiva pegada'],
    correcta: 1,
    explicacion: 'La guía pide retirar grapas, cintas y restos de comida; si está limpio y seco, aplasta las cajas.',
    fuente: 'App.jsx:223-224',
  },
  {
    id: 'carton-retirar',
    pregunta: '¿Qué se debe retirar del cartón antes de reciclarlo?',
    opciones: ['Cintas adhesivas, corchetes o plásticos pegados', 'La tinta de impresión', 'El logo del fabricante'],
    correcta: 0,
    explicacion: 'Es uno de los pasos de la guía de cartón.',
    fuente: 'App.jsx:74-75',
  },
  {
    id: 'carton-grasas',
    pregunta: '¿Qué contagio evita la guía al limpiar cartón y papel?',
    opciones: ['Grasas o restos de comida', 'Polvo de la caja', 'Etiquetas de envío'],
    correcta: 0,
    explicacion: 'La guía pide limpiar grasas o restos de comida antes de separar el cartón.',
    fuente: 'App.jsx:73',
  },
  {
    id: 'carton-compostaje',
    pregunta: '¿Qué reutilización de cartón sugiere la app para huertos?',
    opciones: ['Base para compostaje o mantillo', 'Combustible para barbacoa', 'Relleno de contenedores'],
    correcta: 0,
    explicacion: 'Aparece en las sugerencias de reutilización de la guía de cartón.',
    fuente: 'App.jsx:78',
  },
  {
    id: 'donar-cajas',
    pregunta: 'Según los enlaces de la app, ¿a qué organización se pueden donar cajas y embalajes?',
    opciones: ['Traperos de Emaús', 'Comberplast Chile', 'Kyklos Chile'],
    correcta: 0,
    explicacion: 'El enlace de reutilización de cartón dice “Donaciones de cajas y embalajes”.',
    fuente: 'App.jsx:87',
  },
  {
    id: 'lata-preparar',
    pregunta: '¿Qué secuencia se indica para una lata de aluminio?',
    opciones: ['Vaciar, enjuagar, secar y aplastar suavemente', 'Congelar, pintar y enterrar', 'Lavar con aceite y dejar llena'],
    correcta: 0,
    explicacion: 'Es el paso de reciclaje de aluminio en la guía y en la galería.',
    fuente: 'App.jsx:111-113, 237',
  },
  {
    id: 'aluminio-energia',
    pregunta: '¿Qué beneficio ambiental se menciona al reciclar aluminio?',
    opciones: ['Ahorra mucha energía frente a producirlo desde cero', 'Elimina por completo los rellenos sanitarios', 'No requiere separación'],
    correcta: 0,
    explicacion: 'Afirmación general de la galería, sin cifras.',
    fuente: 'App.jsx:237',
  },
  {
    id: 'lata-macetero',
    pregunta: '¿Qué reutilización de latas aparece en la app?',
    opciones: ['Macetero decorativo o portalápices', 'Batería casera', 'Envase para líquidos calientes'],
    correcta: 0,
    explicacion: 'Está en las sugerencias de reutilización de aluminio.',
    fuente: 'App.jsx:116-118',
  },
  {
    id: 'fundacion-basura',
    pregunta: '¿Qué organización ofrece talleres de suprarreciclaje para latas en los enlaces?',
    opciones: ['Fundación Basura', 'TriCiclos Chile', 'Kyklos Chile'],
    correcta: 0,
    explicacion: 'El enlace de reutilización de aluminio lo indica.',
    fuente: 'App.jsx:125',
  },
  {
    id: 'botella-tapa-etiqueta',
    pregunta: '¿Qué hacer con la tapa y la etiqueta de una botella si son de otro material?',
    opciones: ['Dejarlas puestas siempre', 'Retirarlas', 'Quemarlas'],
    correcta: 1,
    explicacion: 'La guía de plástico y el consejo del PET lo indican.',
    fuente: 'App.jsx:149, 211',
  },
  {
    id: 'botella-aplastar',
    pregunta: '¿Por qué se recomienda aplastar la botella antes de depositarla?',
    opciones: ['Para ocupar menos espacio', 'Para cambiar su color', 'Para que pese más'],
    correcta: 0,
    explicacion: 'Razón indicada en el consejo del PET.',
    fuente: 'App.jsx:211',
  },
  {
    id: 'tipos-plastico',
    pregunta: '¿Qué tipos de plástico nombra la guía de la app?',
    opciones: ['PET y HDPE', 'PVC y vidrio', 'Solo poliestireno'],
    correcta: 0,
    explicacion: 'El título de la guía es “Plástico (PET / HDPE)” y el consejo menciona ambos.',
    fuente: 'App.jsx:142, 211',
  },
  {
    id: 'botella-ecoladrillo',
    pregunta: '¿Qué proyecto de reutilización con botellas se sugiere?',
    opciones: ['Ecoladrillos para construcción', 'Cables eléctricos', 'Compostaje directo'],
    correcta: 0,
    explicacion: 'Está en las sugerencias de reutilización de plástico.',
    fuente: 'App.jsx:155',
  },
  {
    id: 'comberplast',
    pregunta: 'Según los enlaces de la app, ¿qué empresa es planta de reciclaje y transformación de plásticos?',
    opciones: ['Comberplast Chile', 'Traperos de Emaús', 'Fundación Basura'],
    correcta: 0,
    explicacion: 'Descripción del enlace en la guía de plástico.',
    fuente: 'App.jsx:158',
  },
  {
    id: 'punto-satelite',
    pregunta: '¿En qué comuna está el Punto Limpio Ciudad Satélite?',
    opciones: ['Maipú', 'Ñuñoa', 'La Florida'],
    correcta: 0,
    explicacion: 'Dato del listado de Puntos Limpios RM.',
    fuente: 'App.jsx:250-255',
  },
  {
    id: 'punto-tres-poniente',
    pregunta: '¿Qué materiales acepta el Punto Limpio Parque Tres Poniente?',
    opciones: ['Cartón, Plástico HDPE y Aluminio', 'Solo vidrio', 'Solo pilas'],
    correcta: 0,
    explicacion: 'Dato del listado de Puntos Limpios RM.',
    fuente: 'App.jsx:257-261',
  },
  {
    id: 'punto-forestal',
    pregunta: '¿Cómo se llama el punto limpio de Santiago Centro en la app?',
    opciones: ['Parque Araucano', 'Parque Forestal', 'Parque Inés de Suárez'],
    correcta: 1,
    explicacion: 'Dato del listado de Puntos Limpios RM.',
    fuente: 'App.jsx:264-268',
  },
  {
    id: 'mma-santiago-recicla',
    pregunta: '¿Qué enlace oficial del Ministerio del Medio Ambiente aparece para consultar puntos limpios?',
    opciones: ['Santiago Recicla (MMA)', 'Google Maps', 'Mercado Público'],
    correcta: 0,
    explicacion: 'URL santiagorecicla.mma.gob.cl en los enlaces de reciclaje.',
    fuente: 'App.jsx:83, 122, 159',
  },
  {
    id: 'horarios-puntos',
    pregunta: '¿Dónde se muestran los horarios de los puntos limpios en la app?',
    opciones: ['En un archivo descargable', 'En el listado de Puntos Limpios RM, junto a cada punto', 'Sólo en el mapa sin texto'],
    correcta: 1,
    explicacion: 'Cada entrada del listado incluye un campo de horario.',
    fuente: 'App.jsx:254, 261, 268',
  },
];

function mulberry32(semilla) {
  let a = semilla >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function barajar(items, rng) {
  const copia = [...items];
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [copia[i], copia[j]] = [copia[j], copia[i]];
  }
  return copia;
}

export function iniciarRonda(estado) {
  let vistas = estado.vistas ?? [];
  let ciclos = estado.ciclos ?? 0;

  // Reiniciar sólo cuando se agotó el banco completo.
  if (vistas.length >= estado.banco.length) {
    vistas = [];
    ciclos += 1;
  }

  const disponibles = estado.banco.filter((p) => !vistas.includes(p.id));
  const ronda = barajar(disponibles, estado.rng).slice(0, estado.porRonda);

  return {
    ...estado,
    vistas: [...vistas, ...ronda.map((p) => p.id)],
    ronda,
    indice: 0,
    opcion: null,
    aciertos: 0,
    respondidas: 0,
    rondaNumero: (estado.rondaNumero ?? 0) + 1,
    ciclos,
    terminada: false,
  };
}

export function crearEstadoTrivia({
  banco = BANCO_TRIVIA,
  semilla = 1,
  porRonda = PREGUNTAS_POR_RONDA,
} = {}) {
  return iniciarRonda({
    banco,
    porRonda,
    rng: mulberry32(semilla),
    vistas: [],
    ronda: [],
    indice: 0,
    opcion: null,
    aciertos: 0,
    respondidas: 0,
    rondaNumero: 0,
    ciclos: 0,
    terminada: false,
  });
}

export function preguntaActual(estado) {
  return estado.ronda[estado.indice] ?? null;
}

export function responderEnTrivia(estado, opcion) {
  if (estado.terminada || estado.opcion !== null) return estado;
  const pregunta = preguntaActual(estado);
  if (!pregunta || !Number.isInteger(opcion) || opcion < 0 || opcion >= pregunta.opciones.length) {
    return estado;
  }
  return {
    ...estado,
    opcion,
    respondidas: estado.respondidas + 1,
    aciertos: estado.aciertos + (opcion === pregunta.correcta ? 1 : 0),
  };
}

export function avanzarEnTrivia(estado) {
  if (estado.terminada || estado.opcion === null) return estado;
  if (estado.indice + 1 >= estado.ronda.length) {
    return { ...estado, terminada: true };
  }
  return { ...estado, indice: estado.indice + 1, opcion: null };
}
