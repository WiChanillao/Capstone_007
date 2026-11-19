-- =====================================================================
-- EcoScan Chile - Datos completos (extraídos de App.jsx)
-- Archivo 3 de 3: ejecutar DESPUÉS de 01 y 02.
-- Se puede ejecutar más de una vez sin duplicar datos.
-- =====================================================================
USE ecoscan;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- Escáner IA: contenedor gris para el aluminio
-- ---------------------------------------------------------------------
INSERT INTO contenedor (id_contenedor, nombre, color) VALUES
  (3, 'Contenedor Gris', 'gris')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), color = VALUES(color);

UPDATE material SET id_contenedor = 3 WHERE nombre = 'Aluminio';

-- Tipos de instrucción: 1-2 Cartón (id_material 1), 3-4 Aluminio (3), 5-6 Plástico (2)
INSERT INTO instruccion (id_instruccion, id_material, tipo) VALUES
  (1, 1, 'RECICLAR'), (2, 1, 'REUTILIZAR'),
  (3, 3, 'RECICLAR'), (4, 3, 'REUTILIZAR'),
  (5, 2, 'RECICLAR'), (6, 2, 'REUTILIZAR')
ON DUPLICATE KEY UPDATE id_material = VALUES(id_material), tipo = VALUES(tipo);

INSERT INTO paso_instruccion (id_paso, id_instruccion, orden, texto) VALUES
  -- Cartón y Papel: reciclar
  (1, 1, 1, 'Limpia el cartón o papel de grasas o restos de comida.'),
  (2, 1, 2, 'Retira cintas adhesivas, corchetes o plásticos pegados.'),
  (3, 1, 3, 'Desarma y aplasta las cajas para reducir volumen.'),
  -- Cartón y Papel: reutilizar
  (4, 2, 1, 'Úsalo como base para compostaje o mantillo de huertos.'),
  (5, 2, 2, 'Crea organizadores de escritorio o cajas de almacenamiento.'),
  (6, 2, 3, 'Reutiliza las cajas intactas para futuros envíos o mudanzas.'),
  -- Aluminio: reciclar
  (7, 3, 1, 'Enjuaga la lata para eliminar restos de líquido o alimento.'),
  (8, 3, 2, 'Deja secar el interior por completo.'),
  (9, 3, 3, 'Aplástala suavemente para optimizar espacio en el contenedor.'),
  -- Aluminio: reutilizar
  (10, 4, 1, 'Conviértela en macetero decorativo para suculentas.'),
  (11, 4, 2, 'Úsala como portalápices u organizador de escritorio.'),
  (12, 4, 3, 'Fabrica faroles decorativos o ceniceros reutilizables.'),
  -- Plástico: reciclar
  (13, 5, 1, 'Lava y enjuaga el envase plástico.'),
  (14, 5, 2, 'Retira la tapa y la etiqueta (si es de material distinto).'),
  (15, 5, 3, 'Aplasta la botella antes de depositarla en el contenedor.'),
  -- Plástico: reutilizar
  (16, 6, 1, 'Transforma botellas en maceteros autorregantes.'),
  (17, 6, 2, 'Crea embudos caseros o dispensadores.'),
  (18, 6, 3, 'Conviértelas en ecoladrillos para proyectos de construcción.')
ON DUPLICATE KEY UPDATE id_instruccion = VALUES(id_instruccion), orden = VALUES(orden), texto = VALUES(texto);

INSERT INTO recurso_externo (id_recurso, id_instruccion, nombre, url) VALUES
  (1,  1, 'Portal ReChile (MMA)',   'https://rechile.mma.gob.cl'),
  (2,  1, 'TriCiclos Chile',        'https://www.triciclos.cl'),
  (3,  2, 'Traperos de Emaús',      'https://www.emaus.cl'),
  (4,  2, 'Fundación Basura',       'https://www.fundacionbasura.org'),
  (5,  3, 'Kyklos Chile',           'https://www.kyklos.cl'),
  (6,  3, 'Portal ReChile (MMA)',   'https://rechile.mma.gob.cl'),
  (7,  4, 'Fundación Basura',       'https://www.fundacionbasura.org'),
  (8,  5, 'Comberplast Chile',      'https://www.comberplast.cl'),
  (9,  5, 'Portal ReChile (MMA)',   'https://rechile.mma.gob.cl'),
  (10, 6, 'Ecoladrillos Chile',     'https://www.fundacionbasura.org')
ON DUPLICATE KEY UPDATE id_instruccion = VALUES(id_instruccion), nombre = VALUES(nombre), url = VALUES(url);

INSERT INTO banner_impacto (id_banner, titulo, texto) VALUES
  (1, 'Tiempos Extremos de Degradación',
      'Una botella plástica PET tarda más de 500 años en descomponerse. En Chile, menos del 10% del plástico consumido se recicla.'),
  (2, 'Microplásticos en el Océano',
      'Para 2050, habrá más plástico que peces en el océano si no reducimos y reciclamos nuestros residuos urbanos.'),
  (3, 'Impacto en el Calentamiento Global',
      'Por cada tonelada de aluminio reciclada, se evita la emisión de casi 9 toneladas de CO₂ a la atmósfera.'),
  (4, 'Saturación en Rellenos Sanitarios de la RM',
      'Los rellenos sanitarios de Santiago (como Santa Marta o Tiltil) reciben miles de toneladas diarias que podrían valorizarse.')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), texto = VALUES(texto);

-- ---------------------------------------------------------------------
-- Puntos Limpios RM (comunas: 1 Maipú, 2 Santiago Centro, 3 Providencia,
-- 4 Las Condes, 5 Puente Alto, 6 La Florida, 7 Ñuñoa, 8 San Bernardo, 9 Peñalolén)
-- ---------------------------------------------------------------------
INSERT INTO punto_limpio (id_punto, id_comuna, nombre, direccion, horario) VALUES
  (1,  1, 'Punto Limpio Parque Tres Poniente',   'Av. Tres Poniente con Borgoño',                              'Mar a Dom: 09:00 - 17:30 hrs'),
  (2,  1, 'Punto Limpio Ciudad Satélite',        'Av. Parque Sur con Alcalde Infante Larraín',                 'Lun a Sáb: 08:30 - 18:00 hrs'),
  (3,  2, 'Punto Limpio Parque Forestal',        'Av. Cardenal José María Caro (frente a Museo Bellas Artes)', 'Lun a Dom: 08:00 - 19:00 hrs'),
  (4,  3, 'Punto Limpio Parque Inés de Suárez',  'Av. Regimiento de Cazadores 1220',                           'Mar a Dom: 09:00 - 18:00 hrs'),
  (5,  4, 'Punto Limpio Parque Araucano',        'Av. Presidente Riesco 5698',                                 'Lun a Dom: 08:30 - 20:00 hrs'),
  (6,  5, 'Punto Limpio Mall Plaza Tobalaba',    'Av. Camilo Henríquez 3296',                                  'Lun a Dom: 10:00 - 19:00 hrs'),
  (7,  6, 'Punto Limpio Walker Martínez',        'Av. Walker Martínez 2245',                                   'Mar a Sáb: 09:00 - 18:00 hrs'),
  (8,  7, 'Punto Limpio Plaza Ñuñoa',            'Av. Irarrázaval 3550 (Sector Norte)',                        'Lun a Sáb: 09:00 - 18:00 hrs'),
  (9,  8, 'Punto Limpio Parque Garcia de la Huerta', 'América 504',                                            'Lun a Vie: 09:00 - 17:00 hrs'),
  (10, 9, 'Ecoparque Peñalolén',                 'Av. José Arrieta 10000',                                     'Mar a Dom: 09:00 - 17:30 hrs')
ON DUPLICATE KEY UPDATE id_comuna = VALUES(id_comuna), nombre = VALUES(nombre),
                        direccion = VALUES(direccion), horario = VALUES(horario);

-- Los 10 puntos reciben Cartón/Papel (1), Plástico (2) y Aluminio/Latas (3).
INSERT IGNORE INTO punto_material (id_punto, id_material)
SELECT p.id_punto, m.id_material
FROM punto_limpio p CROSS JOIN material m;

-- ---------------------------------------------------------------------
-- Eco-Simulador RM: factores por unidad (de las fórmulas de App.jsx)
-- Sliders: PET y latas hasta 50, cartón hasta 30.
-- ---------------------------------------------------------------------
UPDATE item_simulador SET valor_max = 50, agua_litros = 3,  co2_kg = 0.08, residuos_kg = 0.03
 WHERE nombre = 'Botellas Plásticas (PET)';
UPDATE item_simulador SET valor_max = 50, agua_litros = 2,  co2_kg = 0.17, residuos_kg = 0.015
 WHERE nombre = 'Latas de Bebida / Conservas';
UPDATE item_simulador SET valor_max = 30, agua_litros = 12, co2_kg = 0.25, residuos_kg = 0.12
 WHERE nombre = 'Cajas de Cartón / Envoltorios';

-- ---------------------------------------------------------------------
-- Desafío Verde RM
-- ---------------------------------------------------------------------
INSERT INTO habito (id_habito, titulo, descripcion) VALUES
  (1, 'Bolsas Reutilizables en la Feria o Vega',
      'Realiza tus compras semanales en la Feria Libre o Vega Central usando bolsas de género o carrito.'),
  (2, 'Dona Tapitas a Damas de Café',
      'Junta las tapas plásticas de botellas y llévalas a los puntos de donación para niños del Hospital Calvo Mackenna / San Borja.'),
  (3, 'Confecciona un Ecoladrillo Casero',
      'Rellena una botella PET limpia con plásticos flexibles no reciclables (envolturas de snacks, fideos, galletas).'),
  (4, 'Separación Limpia en Origen',
      'Lava y seca todos los envases plásticos y latas antes de llevarlos al Punto Limpio de tu comuna.')
ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), descripcion = VALUES(descripcion);

-- ---------------------------------------------------------------------
-- Verificación
-- ---------------------------------------------------------------------
SELECT 'contenedor' AS tabla, COUNT(*) AS filas FROM contenedor
UNION ALL SELECT 'material', COUNT(*) FROM material
UNION ALL SELECT 'instruccion', COUNT(*) FROM instruccion
UNION ALL SELECT 'paso_instruccion', COUNT(*) FROM paso_instruccion
UNION ALL SELECT 'recurso_externo', COUNT(*) FROM recurso_externo
UNION ALL SELECT 'banner_impacto', COUNT(*) FROM banner_impacto
UNION ALL SELECT 'comuna', COUNT(*) FROM comuna
UNION ALL SELECT 'punto_limpio', COUNT(*) FROM punto_limpio
UNION ALL SELECT 'punto_material', COUNT(*) FROM punto_material
UNION ALL SELECT 'item_simulador', COUNT(*) FROM item_simulador
UNION ALL SELECT 'habito', COUNT(*) FROM habito;
