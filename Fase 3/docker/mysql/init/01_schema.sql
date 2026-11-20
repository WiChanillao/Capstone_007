-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: ecoscan
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `ecoscan`
--

-- Arranque seguro: el script nunca elimina una base existente.



--
-- Table structure for table `banner_impacto`
--

DROP TABLE IF EXISTS `banner_impacto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banner_impacto` (
  `id_banner` smallint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(80) NOT NULL,
  `texto` varchar(300) NOT NULL,
  PRIMARY KEY (`id_banner`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comuna`
--

DROP TABLE IF EXISTS `comuna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comuna` (
  `id_comuna` smallint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  PRIMARY KEY (`id_comuna`),
  UNIQUE KEY `uq_comuna_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contenedor`
--

DROP TABLE IF EXISTS `contenedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contenedor` (
  `id_contenedor` smallint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(40) NOT NULL,
  `color` varchar(20) NOT NULL,
  PRIMARY KEY (`id_contenedor`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `escaneos`
--

DROP TABLE IF EXISTS `escaneos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escaneos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime DEFAULT NULL,
  `materiales_detectados` varchar(255) DEFAULT NULL,
  `modelo_usado` varchar(50) DEFAULT NULL,
  `total_objetos` int DEFAULT NULL,
  `id_sesion` varchar(36) DEFAULT NULL,
  `id_solicitud` char(32) DEFAULT NULL,
  `cant_carton` int NOT NULL DEFAULT '0',
  `cant_aluminio` int NOT NULL DEFAULT '0',
  `cant_plastico` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_escaneos_solicitud` (`id_sesion`, `id_solicitud`),
  KEY `ix_escaneos_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `habito`
--

DROP TABLE IF EXISTS `habito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habito` (
  `id_habito` smallint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(120) NOT NULL,
  `descripcion` varchar(300) NOT NULL,
  PRIMARY KEY (`id_habito`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `habito_cumplido`
--

DROP TABLE IF EXISTS `habito_cumplido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habito_cumplido` (
  `id_sesion` char(36) NOT NULL,
  `id_habito` smallint NOT NULL,
  `marcado` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_sesion`,`id_habito`),
  KEY `fk_hc_habito` (`id_habito`),
  CONSTRAINT `fk_hc_habito` FOREIGN KEY (`id_habito`) REFERENCES `habito` (`id_habito`),
  CONSTRAINT `fk_hc_sesion` FOREIGN KEY (`id_sesion`) REFERENCES `sesion` (`id_sesion`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inferencia`
--

DROP TABLE IF EXISTS `inferencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inferencia` (
  `id_inferencia` char(36) NOT NULL DEFAULT (uuid()),
  `id_sesion` char(36) DEFAULT NULL,
  `id_material` smallint DEFAULT NULL,
  `resultado` varchar(20) NOT NULL,
  `confianza` decimal(5,4) DEFAULT NULL,
  `latencia_ms` int NOT NULL,
  `fecha_hora` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_inferencia`),
  KEY `fk_inf_sesion` (`id_sesion`),
  KEY `fk_inf_material` (`id_material`),
  CONSTRAINT `fk_inf_material` FOREIGN KEY (`id_material`) REFERENCES `material` (`id_material`),
  CONSTRAINT `fk_inf_sesion` FOREIGN KEY (`id_sesion`) REFERENCES `sesion` (`id_sesion`) ON DELETE SET NULL,
  CONSTRAINT `ck_inf_confianza` CHECK ((`confianza` between 0 and 1)),
  CONSTRAINT `ck_inf_latencia` CHECK ((`latencia_ms` >= 0)),
  CONSTRAINT `ck_inf_ok_material` CHECK (((`resultado` = _utf8mb4'OK') = (`id_material` is not null))),
  CONSTRAINT `ck_inf_resultado` CHECK ((`resultado` in (_utf8mb4'OK',_utf8mb4'BORROSA',_utf8mb4'CONFIANZA_BAJA',_utf8mb4'SIN_DETECCION')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `instruccion`
--

DROP TABLE IF EXISTS `instruccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instruccion` (
  `id_instruccion` int NOT NULL AUTO_INCREMENT,
  `id_material` smallint NOT NULL,
  `tipo` varchar(10) NOT NULL,
  PRIMARY KEY (`id_instruccion`),
  UNIQUE KEY `uq_instruccion_material_tipo` (`id_material`,`tipo`),
  CONSTRAINT `fk_instruccion_material` FOREIGN KEY (`id_material`) REFERENCES `material` (`id_material`) ON DELETE CASCADE,
  CONSTRAINT `ck_instruccion_tipo` CHECK ((`tipo` in (_utf8mb4'RECICLAR',_utf8mb4'REUTILIZAR')))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `item_simulador`
--

DROP TABLE IF EXISTS `item_simulador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_simulador` (
  `id_item` smallint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `valor_defecto` smallint NOT NULL,
  `valor_max` smallint NOT NULL,
  `agua_litros` decimal(10,3) NOT NULL,
  `co2_kg` decimal(10,4) NOT NULL,
  `residuos_kg` decimal(10,4) NOT NULL,
  PRIMARY KEY (`id_item`),
  CONSTRAINT `ck_item_agua` CHECK ((`agua_litros` >= 0)),
  CONSTRAINT `ck_item_co2` CHECK ((`co2_kg` >= 0)),
  CONSTRAINT `ck_item_residuos` CHECK ((`residuos_kg` >= 0)),
  CONSTRAINT `ck_item_valores` CHECK ((`valor_defecto` <= `valor_max`))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `material`
--

DROP TABLE IF EXISTS `material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material` (
  `id_material` smallint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `id_contenedor` smallint DEFAULT NULL,
  PRIMARY KEY (`id_material`),
  UNIQUE KEY `uq_material_nombre` (`nombre`),
  KEY `fk_material_contenedor` (`id_contenedor`),
  CONSTRAINT `fk_material_contenedor` FOREIGN KEY (`id_contenedor`) REFERENCES `contenedor` (`id_contenedor`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paso_instruccion`
--

DROP TABLE IF EXISTS `paso_instruccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paso_instruccion` (
  `id_paso` int NOT NULL AUTO_INCREMENT,
  `id_instruccion` int NOT NULL,
  `orden` smallint NOT NULL,
  `texto` varchar(400) NOT NULL,
  PRIMARY KEY (`id_paso`),
  UNIQUE KEY `uq_paso_instruccion_orden` (`id_instruccion`,`orden`),
  CONSTRAINT `fk_paso_instruccion` FOREIGN KEY (`id_instruccion`) REFERENCES `instruccion` (`id_instruccion`) ON DELETE CASCADE,
  CONSTRAINT `ck_paso_orden` CHECK ((`orden` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `punto_limpio`
--

DROP TABLE IF EXISTS `punto_limpio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `punto_limpio` (
  `id_punto` int NOT NULL AUTO_INCREMENT,
  `id_comuna` smallint NOT NULL,
  `nombre` varchar(120) NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `horario` varchar(100) DEFAULT NULL,
  `lat` decimal(10,7) DEFAULT NULL,
  `lon` decimal(10,7) DEFAULT NULL,
  `fuente` varchar(60) NOT NULL DEFAULT 'investigacion_propia',
  `nota` varchar(250) DEFAULT NULL,
  `coords_aproximadas` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_punto`),
  KEY `fk_punto_comuna` (`id_comuna`),
  CONSTRAINT `fk_punto_comuna` FOREIGN KEY (`id_comuna`) REFERENCES `comuna` (`id_comuna`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `punto_material`
--

DROP TABLE IF EXISTS `punto_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `punto_material` (
  `id_punto` int NOT NULL,
  `id_material` smallint NOT NULL,
  PRIMARY KEY (`id_punto`,`id_material`),
  KEY `fk_pm_material` (`id_material`),
  CONSTRAINT `fk_pm_material` FOREIGN KEY (`id_material`) REFERENCES `material` (`id_material`),
  CONSTRAINT `fk_pm_punto` FOREIGN KEY (`id_punto`) REFERENCES `punto_limpio` (`id_punto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recurso_externo`
--

DROP TABLE IF EXISTS `recurso_externo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recurso_externo` (
  `id_recurso` int NOT NULL AUTO_INCREMENT,
  `id_instruccion` int NOT NULL,
  `nombre` varchar(120) NOT NULL,
  `url` varchar(500) NOT NULL,
  PRIMARY KEY (`id_recurso`),
  KEY `fk_recurso_instruccion` (`id_instruccion`),
  CONSTRAINT `fk_recurso_instruccion` FOREIGN KEY (`id_instruccion`) REFERENCES `instruccion` (`id_instruccion`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sesion`
--

DROP TABLE IF EXISTS `sesion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesion` (
  `id_sesion` char(36) NOT NULL DEFAULT (uuid()),
  `creada_en` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_sesion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-19  1:08:15
