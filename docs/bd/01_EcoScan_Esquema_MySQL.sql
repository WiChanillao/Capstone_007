-- =====================================================================
-- EcoScan Chile - Modelo relacional simplificado (14 tablas)
-- Motor: MySQL 8.0.16+ (necesario para CHECK y DEFAULT (UUID()))
-- Archivo 1 de 2: esquema (base de datos + tablas)
-- =====================================================================
CREATE DATABASE IF NOT EXISTS ecoscan
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE ecoscan;

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- Módulo Escáner IA
-- ---------------------------------------------------------------------
CREATE TABLE contenedor (
  id_contenedor SMALLINT    NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(40) NOT NULL,
  color         VARCHAR(20) NOT NULL,
  PRIMARY KEY (id_contenedor)
) ENGINE=InnoDB;

CREATE TABLE material (
  id_material   SMALLINT    NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(80) NOT NULL,
  id_contenedor SMALLINT    NULL,   -- NULL mientras no se confirme (Aluminio)
  PRIMARY KEY (id_material),
  UNIQUE KEY uq_material_nombre (nombre),
  CONSTRAINT fk_material_contenedor
    FOREIGN KEY (id_contenedor) REFERENCES contenedor (id_contenedor)
) ENGINE=InnoDB;

CREATE TABLE instruccion (
  id_instruccion INT         NOT NULL AUTO_INCREMENT,
  id_material    SMALLINT    NOT NULL,
  tipo           VARCHAR(10) NOT NULL,
  PRIMARY KEY (id_instruccion),
  UNIQUE KEY uq_instruccion_material_tipo (id_material, tipo),
  CONSTRAINT fk_instruccion_material
    FOREIGN KEY (id_material) REFERENCES material (id_material)
    ON DELETE CASCADE,
  CONSTRAINT ck_instruccion_tipo CHECK (tipo IN ('RECICLAR','REUTILIZAR'))
) ENGINE=InnoDB;

CREATE TABLE paso_instruccion (
  id_paso        INT          NOT NULL AUTO_INCREMENT,
  id_instruccion INT          NOT NULL,
  orden          SMALLINT     NOT NULL,
  texto          VARCHAR(400) NOT NULL,
  PRIMARY KEY (id_paso),
  UNIQUE KEY uq_paso_instruccion_orden (id_instruccion, orden),
  CONSTRAINT fk_paso_instruccion
    FOREIGN KEY (id_instruccion) REFERENCES instruccion (id_instruccion)
    ON DELETE CASCADE,
  CONSTRAINT ck_paso_orden CHECK (orden > 0)
) ENGINE=InnoDB;

CREATE TABLE recurso_externo (
  id_recurso     INT          NOT NULL AUTO_INCREMENT,
  id_instruccion INT          NOT NULL,
  nombre         VARCHAR(120) NOT NULL,
  url            VARCHAR(500) NOT NULL,
  PRIMARY KEY (id_recurso),
  CONSTRAINT fk_recurso_instruccion
    FOREIGN KEY (id_instruccion) REFERENCES instruccion (id_instruccion)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE banner_impacto (
  id_banner SMALLINT     NOT NULL AUTO_INCREMENT,
  titulo    VARCHAR(80)  NOT NULL,
  texto     VARCHAR(300) NOT NULL,
  PRIMARY KEY (id_banner)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Módulo Puntos Limpios RM
-- ---------------------------------------------------------------------
CREATE TABLE comuna (
  id_comuna SMALLINT    NOT NULL AUTO_INCREMENT,
  nombre    VARCHAR(60) NOT NULL,
  PRIMARY KEY (id_comuna),
  UNIQUE KEY uq_comuna_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE punto_limpio (
  id_punto  INT          NOT NULL AUTO_INCREMENT,
  id_comuna SMALLINT     NOT NULL,
  nombre    VARCHAR(120) NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  horario   VARCHAR(100) NULL,
  PRIMARY KEY (id_punto),
  CONSTRAINT fk_punto_comuna
    FOREIGN KEY (id_comuna) REFERENCES comuna (id_comuna)
) ENGINE=InnoDB;

CREATE TABLE punto_material (
  id_punto    INT      NOT NULL,
  id_material SMALLINT NOT NULL,
  PRIMARY KEY (id_punto, id_material),
  CONSTRAINT fk_pm_punto
    FOREIGN KEY (id_punto) REFERENCES punto_limpio (id_punto)
    ON DELETE CASCADE,
  CONSTRAINT fk_pm_material
    FOREIGN KEY (id_material) REFERENCES material (id_material)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Módulo Eco-Simulador RM
-- ---------------------------------------------------------------------
CREATE TABLE item_simulador (
  id_item       SMALLINT      NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(80)   NOT NULL,
  valor_defecto SMALLINT      NOT NULL,
  valor_max     SMALLINT      NOT NULL,
  agua_litros   DECIMAL(10,3) NOT NULL,
  co2_kg        DECIMAL(10,4) NOT NULL,
  residuos_kg   DECIMAL(10,4) NOT NULL,
  PRIMARY KEY (id_item),
  CONSTRAINT ck_item_agua     CHECK (agua_litros >= 0),
  CONSTRAINT ck_item_co2      CHECK (co2_kg >= 0),
  CONSTRAINT ck_item_residuos CHECK (residuos_kg >= 0),
  CONSTRAINT ck_item_valores  CHECK (valor_defecto <= valor_max)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Módulo Desafío Verde RM + sesiones e inferencias
-- ---------------------------------------------------------------------
CREATE TABLE habito (
  id_habito   SMALLINT     NOT NULL AUTO_INCREMENT,
  titulo      VARCHAR(120) NOT NULL,
  descripcion VARCHAR(300) NOT NULL,
  PRIMARY KEY (id_habito)
) ENGINE=InnoDB;

CREATE TABLE sesion (
  id_sesion CHAR(36)  NOT NULL DEFAULT (UUID()),
  creada_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- se guarda en UTC
  PRIMARY KEY (id_sesion)
) ENGINE=InnoDB;

CREATE TABLE habito_cumplido (
  id_sesion CHAR(36) NOT NULL,
  id_habito SMALLINT NOT NULL,
  marcado   BOOLEAN  NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id_sesion, id_habito),
  CONSTRAINT fk_hc_sesion
    FOREIGN KEY (id_sesion) REFERENCES sesion (id_sesion)
    ON DELETE CASCADE,
  CONSTRAINT fk_hc_habito
    FOREIGN KEY (id_habito) REFERENCES habito (id_habito)
) ENGINE=InnoDB;

CREATE TABLE inferencia (
  id_inferencia CHAR(36)      NOT NULL DEFAULT (UUID()),
  id_sesion     CHAR(36)      NULL,
  id_material   SMALLINT      NULL,
  resultado     VARCHAR(20)   NOT NULL,
  confianza     DECIMAL(5,4)  NULL,
  latencia_ms   INT           NOT NULL,
  fecha_hora    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- se guarda en UTC
  PRIMARY KEY (id_inferencia),
  CONSTRAINT fk_inf_sesion
    FOREIGN KEY (id_sesion) REFERENCES sesion (id_sesion)
    ON DELETE SET NULL,
  CONSTRAINT fk_inf_material
    FOREIGN KEY (id_material) REFERENCES material (id_material),
  CONSTRAINT ck_inf_resultado  CHECK (resultado IN ('OK','BORROSA','CONFIANZA_BAJA')),
  CONSTRAINT ck_inf_confianza  CHECK (confianza BETWEEN 0 AND 1),
  CONSTRAINT ck_inf_latencia   CHECK (latencia_ms >= 0),
  -- resultado OK <=> hay material identificado
  CONSTRAINT ck_inf_ok_material CHECK ((resultado = 'OK') = (id_material IS NOT NULL))
) ENGINE=InnoDB;
