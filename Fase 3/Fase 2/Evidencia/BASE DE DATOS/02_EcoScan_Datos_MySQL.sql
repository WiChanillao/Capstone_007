-- =====================================================================
-- EcoScan Chile - Datos iniciales (observados en la app)
-- Archivo 2 de 2: ejecutar DESPUÉS de 01_EcoScan_Esquema_MySQL.sql
-- =====================================================================
USE ecoscan;
SET NAMES utf8mb4;

INSERT INTO contenedor (nombre, color) VALUES
  ('Contenedor Azul', 'azul'),
  ('Contenedor Amarillo', 'amarillo');

INSERT INTO material (nombre, id_contenedor) VALUES
  ('Cartón y Papel', 1),
  ('Plástico (PET/HDPE)', 2),
  ('Aluminio', NULL);

INSERT INTO comuna (nombre) VALUES
  ('Maipú'), ('Santiago Centro'), ('Providencia'), ('Las Condes'), ('Puente Alto'),
  ('La Florida'), ('Ñuñoa'), ('San Bernardo'), ('Peñalolén');

INSERT INTO punto_limpio (id_comuna, nombre, direccion, horario) VALUES
  (1, 'Punto Limpio Parque Tres Poniente', 'Av. Tres Poniente con Borgoño', 'Mar a Dom 09:00 - 17:30 hrs');

-- Factores de impacto y máximos: completar con los del código del simulador
INSERT INTO item_simulador (nombre, valor_defecto, valor_max, agua_litros, co2_kg, residuos_kg) VALUES
  ('Botellas Plásticas (PET)', 8, 30, 0, 0, 0),
  ('Latas de Bebida / Conservas', 6, 30, 0, 0, 0),
  ('Cajas de Cartón / Envoltorios', 4, 30, 0, 0, 0);
