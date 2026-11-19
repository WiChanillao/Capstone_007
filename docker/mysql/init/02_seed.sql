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



--
-- Dumping data for table `banner_impacto`
--

LOCK TABLES `banner_impacto` WRITE;
/*!40000 ALTER TABLE `banner_impacto` DISABLE KEYS */;
INSERT INTO `banner_impacto` VALUES (1,'Tiempos Extremos de Degradaci├│n','Una botella pl├ística PET tarda m├ís de 500 a├▒os en descomponerse. En Chile, menos del 10% del pl├ístico consumido se recicla.'),(2,'Micropl├ísticos en el Oc├®ano','Para 2050, habr├í m├ís pl├ístico que peces en el oc├®ano si no reducimos y reciclamos nuestros residuos urbanos.'),(3,'Impacto en el Calentamiento Global','Por cada tonelada de aluminio reciclada, se evita la emisi├│n de casi 9 toneladas de COÔéé a la atm├│sfera.'),(4,'Saturaci├│n en Rellenos Sanitarios de la RM','Los rellenos sanitarios de Santiago (como Santa Marta o Tiltil) reciben miles de toneladas diarias que podr├¡an valorizarse.');
/*!40000 ALTER TABLE `banner_impacto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `comuna`
--

LOCK TABLES `comuna` WRITE;
/*!40000 ALTER TABLE `comuna` DISABLE KEYS */;
INSERT INTO `comuna` VALUES (6,'La Florida'),(4,'Las Condes'),(1,'Maip├║'),(7,'├æu├▒oa'),(9,'Pe├▒alol├®n'),(3,'Providencia'),(5,'Puente Alto'),(8,'San Bernardo'),(2,'Santiago Centro');
/*!40000 ALTER TABLE `comuna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `contenedor`
--

LOCK TABLES `contenedor` WRITE;
/*!40000 ALTER TABLE `contenedor` DISABLE KEYS */;
INSERT INTO `contenedor` VALUES (1,'Contenedor Azul','azul'),(2,'Contenedor Amarillo','amarillo'),(3,'Contenedor Gris','gris');
/*!40000 ALTER TABLE `contenedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `escaneos`
--

LOCK TABLES `escaneos` WRITE;
/*!40000 ALTER TABLE `escaneos` DISABLE KEYS */;
INSERT INTO `escaneos` VALUES (1,'2026-11-18 21:15:42','Aluminio','best.pt',1,NULL,0,0,0),(2,'2026-11-18 21:48:31','Aluminio','best.pt',1,NULL,0,0,0),(3,'2026-11-18 21:48:31','Ninguno','best.pt',0,NULL,0,0,0),(4,'2026-11-18 21:52:02','Carton','best.pt',1,NULL,0,0,0),(5,'2026-11-18 21:52:20','Carton','best.pt',1,NULL,0,0,0),(6,'2026-11-18 22:09:13','Aluminio','best.pt',1,NULL,0,0,0),(7,'2026-11-18 22:09:17','Aluminio','best.pt',1,NULL,0,0,0),(8,'2026-11-18 22:09:51','Carton','best.pt',1,NULL,0,0,0),(9,'2026-11-18 22:09:52','Ninguno','best.pt',0,NULL,0,0,0),(10,'2026-11-18 22:09:52','Carton','best.pt',1,NULL,0,0,0),(11,'2026-11-18 22:09:52','Carton','best.pt',1,NULL,0,0,0),(12,'2026-11-18 22:09:52','Carton','best.pt',1,NULL,0,0,0),(13,'2026-11-18 22:09:52','Carton','best.pt',1,NULL,0,0,0),(14,'2026-11-18 22:09:52','Carton','best.pt',1,NULL,0,0,0),(15,'2026-11-18 22:09:53','Carton','best.pt',1,NULL,0,0,0),(16,'2026-11-18 22:09:53','Carton','best.pt',1,NULL,0,0,0),(17,'2026-11-18 22:09:53','Carton','best.pt',1,NULL,0,0,0),(18,'2026-11-18 22:09:53','Aluminio','best.pt',1,NULL,0,0,0),(19,'2026-11-18 22:09:53','Aluminio','best.pt',1,NULL,0,0,0),(20,'2026-11-18 22:09:53','Aluminio','best.pt',3,NULL,0,0,0),(21,'2026-11-18 22:09:53','Aluminio','best.pt',1,NULL,0,0,0),(22,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(23,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(24,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(25,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(26,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(27,'2026-11-18 22:09:54','Aluminio','best.pt',1,NULL,0,0,0),(28,'2026-11-18 22:09:54','Plastico, Carton','best.pt',2,NULL,0,0,0),(29,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(30,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(31,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(32,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(33,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(34,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(35,'2026-11-18 22:09:55','Plastico','best.pt',1,NULL,0,0,0),(36,'2026-11-18 22:09:56','Plastico','best.pt',2,NULL,0,0,0),(37,'2026-11-18 22:09:56','Plastico','best.pt',2,NULL,0,0,0),(38,'2026-11-18 22:10:21','Carton','best.pt',1,NULL,0,0,0),(39,'2026-11-18 22:10:36','Plastico','best.pt',1,NULL,0,0,0),(40,'2026-11-18 22:10:51','Plastico','best.pt',1,NULL,0,0,0),(41,'2026-11-18 22:11:06','Plastico','best.pt',1,NULL,0,0,0),(42,'2026-11-18 22:11:21','Aluminio','best.pt',1,NULL,0,0,0),(43,'2026-11-18 22:11:36','Aluminio','best.pt',1,NULL,0,0,0),(44,'2026-11-18 22:11:51','Aluminio','best.pt',1,NULL,0,0,0),(45,'2026-11-18 22:12:07','Aluminio','best.pt',1,NULL,0,0,0),(46,'2026-11-18 22:12:22','Aluminio','best.pt',1,NULL,0,0,0),(47,'2026-11-18 22:12:37','Aluminio','best.pt',1,NULL,0,0,0),(48,'2026-11-18 22:22:09','Aluminio','best.pt',1,NULL,0,0,0);
/*!40000 ALTER TABLE `escaneos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `habito`
--

LOCK TABLES `habito` WRITE;
/*!40000 ALTER TABLE `habito` DISABLE KEYS */;
INSERT INTO `habito` VALUES (1,'Bolsas Reutilizables en la Feria o Vega','Realiza tus compras semanales en la Feria Libre o Vega Central usando bolsas de g├®nero o carrito.'),(2,'Dona Tapitas a Damas de Caf├®','Junta las tapas pl├ísticas de botellas y ll├®valas a los puntos de donaci├│n para ni├▒os del Hospital Calvo Mackenna / San Borja.'),(3,'Confecciona un Ecoladrillo Casero','Rellena una botella PET limpia con pl├ísticos flexibles no reciclables (envolturas de snacks, fideos, galletas).'),(4,'Separaci├│n Limpia en Origen','Lava y seca todos los envases pl├ísticos y latas antes de llevarlos al Punto Limpio de tu comuna.');
/*!40000 ALTER TABLE `habito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `habito_cumplido`
--

LOCK TABLES `habito_cumplido` WRITE;
/*!40000 ALTER TABLE `habito_cumplido` DISABLE KEYS */;
/*!40000 ALTER TABLE `habito_cumplido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inferencia`
--

LOCK TABLES `inferencia` WRITE;
/*!40000 ALTER TABLE `inferencia` DISABLE KEYS */;
INSERT INTO `inferencia` VALUES ('010ab020-62c4-47f2-86cd-14007f4b96b6',NULL,1,'OK',0.8000,120,'2026-10-09 05:28:21'),('01606f63-10da-4f5b-a4bd-e232c9745cfb',NULL,3,'OK',0.9400,112,'2026-10-10 21:20:48'),('08bb5a5f-fa06-4b26-9956-215ffcd5b26d',NULL,3,'OK',0.9400,115,'2026-10-10 21:20:49'),('099a2cc3-a9ff-4265-bf79-c1b90716ad0c',NULL,3,'OK',0.9600,96,'2026-10-09 05:28:22'),('0bbf32e4-a601-468c-b1b3-c93ae4c64e8a',NULL,NULL,'CONFIANZA_BAJA',0.3100,115,'2026-10-09 05:28:24'),('1027606e-7a56-4f9a-a355-054c8d8e7c6c',NULL,1,'OK',0.8800,107,'2026-10-09 05:28:21'),('134ced4d-6407-44b2-a047-4815385cb3b3',NULL,NULL,'CONFIANZA_BAJA',0.3200,124,'2026-10-09 05:28:21'),('13dd2bc6-397c-4925-a951-656ea9792696',NULL,NULL,'CONFIANZA_BAJA',NULL,118,'2026-10-10 21:20:47'),('14654928-48e3-4767-99d7-168ee27bfcfc',NULL,2,'OK',0.5700,120,'2026-10-10 21:20:50'),('1ee5eab3-396b-4104-a768-494936a46171',NULL,3,'OK',0.9400,96,'2026-10-09 05:28:22'),('21e4da85-2dbd-48ab-8391-f05143bc7125',NULL,2,'OK',0.8200,99,'2026-10-09 05:28:23'),('26c4b4e7-7e7e-4924-928c-c1fde8c0cb6d',NULL,3,'OK',0.9100,94,'2026-10-09 05:28:23'),('28cefd63-b803-4004-8cca-9599cad1ce1b',NULL,2,'OK',0.5100,103,'2026-10-10 21:20:50'),('350a01a3-bb34-433a-9e31-2d1980d4400e',NULL,2,'OK',0.7200,126,'2026-10-10 21:20:50'),('35be7c64-a927-46d0-882f-41ae659d6387',NULL,1,'OK',0.8900,112,'2026-10-09 05:28:22'),('35ee7c92-04ea-44af-88c5-bfb43ff575b5',NULL,2,'OK',0.6300,112,'2026-10-10 21:20:51'),('3646dcb9-49f5-44fc-a218-742f0a53d442',NULL,1,'OK',0.8300,102,'2026-10-10 21:20:48'),('3c5ba3b6-53e6-43c6-920c-c94ccd710d3a',NULL,1,'OK',0.7500,105,'2026-10-10 21:20:48'),('41c62caa-b64d-41c4-a7e8-5f4993e89328',NULL,2,'OK',0.5100,105,'2026-10-09 05:28:24'),('44be0029-7080-4dfc-8e0a-428033bff719',NULL,3,'OK',0.9200,117,'2026-10-10 21:20:49'),('44c538a1-3945-40ee-beab-57ac0a77a3d4',NULL,3,'OK',0.9300,117,'2026-10-10 21:20:49'),('455d41e7-e5fc-499f-a11b-8a20f90f2375',NULL,2,'OK',0.9400,101,'2026-10-09 05:28:23'),('506f9055-d3f5-4c77-9969-f191c4e298a3',NULL,1,'OK',0.8700,94,'2026-10-09 05:28:21'),('522d1ba7-d706-43f3-aa57-cb48d0311dc2',NULL,NULL,'CONFIANZA_BAJA',NULL,132,'2026-10-10 21:20:47'),('5bca70ad-a73c-45f0-bca2-0d2601ae3484',NULL,NULL,'CONFIANZA_BAJA',0.3900,98,'2026-10-09 05:28:24'),('65278ce8-84db-404d-bb00-e2762c636f19',NULL,1,'OK',0.8400,126,'2026-10-10 21:20:48'),('6661f116-3353-4a64-95e1-537c66d34f87',NULL,3,'OK',0.9400,97,'2026-10-10 21:20:49'),('689c8bd0-1aa7-472d-a7ec-8aff2e0fa649',NULL,1,'OK',0.6900,116,'2026-10-09 05:28:21'),('6dbfa6b2-43b7-4fa7-98e3-8d608f5d0013',NULL,NULL,'CONFIANZA_BAJA',NULL,110,'2026-10-09 05:28:21'),('705f1a5f-68fa-4a1a-9e1f-2ec6c22b3efe',NULL,3,'OK',0.9300,96,'2026-10-10 21:20:49'),('70ab1d8c-917f-432f-99b1-d02940be4051',NULL,1,'OK',0.8400,112,'2026-10-09 05:28:22'),('75f97f38-8890-4366-a673-cef7df60b03a',NULL,1,'OK',0.6200,100,'2026-10-10 21:20:48'),('77c80278-fe03-402c-983f-5abb65dffd4e',NULL,2,'OK',0.4100,113,'2026-10-09 05:28:21'),('7a1c5d7b-9729-4631-8485-08707cb58fa5',NULL,2,'OK',0.8200,102,'2026-10-10 21:20:50'),('7baa9b88-b349-4d00-aed2-64975e93da74',NULL,NULL,'CONFIANZA_BAJA',NULL,110,'2026-10-10 21:20:48'),('8a699829-d203-44c5-94c4-81a7e03dfc6d',NULL,NULL,'CONFIANZA_BAJA',NULL,106,'2026-10-10 21:20:47'),('8c8cbc36-57a3-458b-8302-b6aeaf68ed9b',NULL,3,'OK',0.8600,93,'2026-10-09 05:28:22'),('92362261-8e80-43b8-9c60-88f76f24dca6',NULL,NULL,'CONFIANZA_BAJA',NULL,111,'2026-10-10 21:20:48'),('931f13d5-b1ff-4e88-9bac-3a67673aaf07',NULL,3,'OK',0.9300,96,'2026-10-10 21:20:49'),('a2228c85-e1ff-4f28-976e-74da9695cb59',NULL,2,'OK',0.6900,116,'2026-10-10 21:20:51'),('a408ac7b-40e1-428b-bbf1-5bcb343fb9b5',NULL,3,'OK',0.9200,99,'2026-10-09 05:28:22'),('ac0f67e7-fd45-4df9-adae-b098d2744484',NULL,2,'OK',0.7700,128,'2026-10-09 05:28:24'),('ae599aae-56d6-446f-9bc6-397ef8a51655',NULL,2,'OK',0.9300,104,'2026-10-09 05:28:24'),('b09b3926-cab4-4ab7-b151-93506c2654a7',NULL,2,'OK',0.6500,118,'2026-10-10 21:20:50'),('bc0f2e0c-3f46-4536-984f-42e8acc9957a',NULL,3,'OK',0.9400,102,'2026-10-10 21:20:48'),('be9502f1-33e5-4284-bdbf-e16d3f84f7cd',NULL,3,'OK',0.9300,100,'2026-10-10 21:20:49'),('c6ebf34c-baaa-47f0-90b3-ee140b3a687f',NULL,3,'OK',0.9300,146,'2026-10-09 05:28:22'),('d37bc54d-0bc6-49c6-8acd-f945812115ed',NULL,3,'OK',0.9400,95,'2026-10-10 21:20:49'),('d5f61031-aec3-4c0b-8af2-f33eec491658',NULL,3,'OK',0.9500,98,'2026-10-09 05:28:23'),('d68832fe-54c4-4bc1-a1a3-784d2d0c3324',NULL,3,'OK',0.9000,111,'2026-10-09 05:28:23'),('d915f599-945d-49a6-9f22-737af8f7a2da',NULL,3,'OK',0.8500,101,'2026-10-09 05:28:23'),('dab8036d-7743-4a4c-bed3-bdcef9faceaf',NULL,2,'OK',0.8000,119,'2026-10-09 05:28:24'),('ddfe9735-356e-4102-b90a-d359c57f53c8',NULL,2,'OK',0.4100,116,'2026-10-10 21:20:50'),('dfe9b656-565b-43e1-a031-c0d71a77f40f',NULL,1,'OK',0.7900,121,'2026-10-10 21:20:47'),('e77d7281-729d-4456-b092-0444887f9385',NULL,3,'OK',0.9200,122,'2026-10-09 05:28:23'),('e9678b6b-d81f-4a5e-a0fc-d45e6277d8b9',NULL,2,'OK',0.9200,96,'2026-10-09 05:28:23'),('ee13fbd4-8674-436d-89f7-ae9b01701259',NULL,2,'OK',0.8800,119,'2026-10-09 05:28:24'),('ee61726d-addc-4788-af9d-0e431793a0ff',NULL,NULL,'CONFIANZA_BAJA',0.3200,124,'2026-10-10 21:20:50'),('eeafc6ae-22f3-4283-95bc-325c36155945',NULL,2,'OK',0.8000,100,'2026-10-10 21:20:50'),('f4cc5f30-5022-43d8-8249-dd694f37d130',NULL,1,'OK',0.8600,108,'2026-10-09 05:28:22');
/*!40000 ALTER TABLE `inferencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `instruccion`
--

LOCK TABLES `instruccion` WRITE;
/*!40000 ALTER TABLE `instruccion` DISABLE KEYS */;
INSERT INTO `instruccion` VALUES (1,1,'RECICLAR'),(2,1,'REUTILIZAR'),(5,2,'RECICLAR'),(6,2,'REUTILIZAR'),(3,3,'RECICLAR'),(4,3,'REUTILIZAR');
/*!40000 ALTER TABLE `instruccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `item_simulador`
--

LOCK TABLES `item_simulador` WRITE;
/*!40000 ALTER TABLE `item_simulador` DISABLE KEYS */;
INSERT INTO `item_simulador` VALUES (1,'Botellas Pl├ísticas (PET)',8,50,3.000,0.0800,0.0300),(2,'Latas de Bebida / Conservas',6,50,2.000,0.1700,0.0150),(3,'Cajas de Cart├│n / Envoltorios',4,30,12.000,0.2500,0.1200);
/*!40000 ALTER TABLE `item_simulador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `material`
--

LOCK TABLES `material` WRITE;
/*!40000 ALTER TABLE `material` DISABLE KEYS */;
INSERT INTO `material` VALUES (1,'Cart├│n y Papel',1),(2,'Pl├ístico (PET/HDPE)',2),(3,'Aluminio',3);
/*!40000 ALTER TABLE `material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `paso_instruccion`
--

LOCK TABLES `paso_instruccion` WRITE;
/*!40000 ALTER TABLE `paso_instruccion` DISABLE KEYS */;
INSERT INTO `paso_instruccion` VALUES (1,1,1,'Limpia el cart├│n o papel de grasas o restos de comida.'),(2,1,2,'Retira cintas adhesivas, corchetes o pl├ísticos pegados.'),(3,1,3,'Desarma y aplasta las cajas para reducir volumen.'),(4,2,1,'├Üsalo como base para compostaje o mantillo de huertos.'),(5,2,2,'Crea organizadores de escritorio o cajas de almacenamiento.'),(6,2,3,'Reutiliza las cajas intactas para futuros env├¡os o mudanzas.'),(7,3,1,'Enjuaga la lata para eliminar restos de l├¡quido o alimento.'),(8,3,2,'Deja secar el interior por completo.'),(9,3,3,'Apl├ístala suavemente para optimizar espacio en el contenedor.'),(10,4,1,'Convi├®rtela en macetero decorativo para suculentas.'),(11,4,2,'├Üsala como portal├ípices u organizador de escritorio.'),(12,4,3,'Fabrica faroles decorativos o ceniceros reutilizables.'),(13,5,1,'Lava y enjuaga el envase pl├ístico.'),(14,5,2,'Retira la tapa y la etiqueta (si es de material distinto).'),(15,5,3,'Aplasta la botella antes de depositarla en el contenedor.'),(16,6,1,'Transforma botellas en maceteros autorregantes.'),(17,6,2,'Crea embudos caseros o dispensadores.'),(18,6,3,'Convi├®rtelas en ecoladrillos para proyectos de construcci├│n.');
/*!40000 ALTER TABLE `paso_instruccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `punto_limpio`
--

LOCK TABLES `punto_limpio` WRITE;
/*!40000 ALTER TABLE `punto_limpio` DISABLE KEYS */;
INSERT INTO `punto_limpio` VALUES (1,1,'Punto Limpio Parque Tres Poniente','Av. Tres Poniente con Borgo├▒o','Mar a Dom: 09:00 - 17:30 hrs',-33.5170000,-70.7350000),(2,1,'Punto Limpio Ciudad Sat├®lite','Av. Parque Sur con Alcalde Infante Larra├¡n','Lun a S├íb: 08:30 - 18:00 hrs',-33.4980000,-70.7680000),(3,2,'Punto Limpio Parque Forestal','Av. Cardenal Jos├® Mar├¡a Caro (frente a Museo Bellas Artes)','Lun a Dom: 08:00 - 19:00 hrs',-33.4330000,-70.6410000),(4,3,'Punto Limpio Parque In├®s de Su├írez','Av. Regimiento de Cazadores 1220','Mar a Dom: 09:00 - 18:00 hrs',-33.4260000,-70.6170000),(5,4,'Punto Limpio Parque Araucano','Av. Presidente Riesco 5698','Lun a Dom: 08:30 - 20:00 hrs',-33.4040000,-70.5750000),(6,5,'Punto Limpio Mall Plaza Tobalaba','Av. Camilo Henr├¡quez 3296','Lun a Dom: 10:00 - 19:00 hrs',-33.5870000,-70.5910000),(7,6,'Punto Limpio Walker Mart├¡nez','Av. Walker Mart├¡nez 2245','Mar a S├íb: 09:00 - 18:00 hrs',-33.5170000,-70.5980000),(8,7,'Punto Limpio Plaza ├æu├▒oa','Av. Irarr├ízaval 3550 (Sector Norte)','Lun a S├íb: 09:00 - 18:00 hrs',-33.4580000,-70.6130000),(9,8,'Punto Limpio Parque Garcia de la Huerta','Am├®rica 504','Lun a Vie: 09:00 - 17:00 hrs',-33.6010000,-70.6990000),(10,9,'Ecoparque Pe├▒alol├®n','Av. Jos├® Arrieta 10000','Mar a Dom: 09:00 - 17:30 hrs',-33.4340000,-70.5450000);
/*!40000 ALTER TABLE `punto_limpio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `punto_material`
--

LOCK TABLES `punto_material` WRITE;
/*!40000 ALTER TABLE `punto_material` DISABLE KEYS */;
INSERT INTO `punto_material` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3);
/*!40000 ALTER TABLE `punto_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `recurso_externo`
--

LOCK TABLES `recurso_externo` WRITE;
/*!40000 ALTER TABLE `recurso_externo` DISABLE KEYS */;
INSERT INTO `recurso_externo` VALUES (1,1,'Portal ReChile (MMA)','https://rechile.mma.gob.cl'),(2,1,'TriCiclos Chile','https://www.triciclos.cl'),(3,2,'Traperos de Ema├║s','https://www.emaus.cl'),(4,2,'Fundaci├│n Basura','https://www.fundacionbasura.org'),(5,3,'Kyklos Chile','https://www.kyklos.cl'),(6,3,'Portal ReChile (MMA)','https://rechile.mma.gob.cl'),(7,4,'Fundaci├│n Basura','https://www.fundacionbasura.org'),(8,5,'Comberplast Chile','https://www.comberplast.cl'),(9,5,'Portal ReChile (MMA)','https://rechile.mma.gob.cl'),(10,6,'Ecoladrillos Chile','https://www.fundacionbasura.org');
/*!40000 ALTER TABLE `recurso_externo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sesion`
--

LOCK TABLES `sesion` WRITE;
/*!40000 ALTER TABLE `sesion` DISABLE KEYS */;
INSERT INTO `sesion` VALUES ('06b6eb6d-ad12-424d-8085-0841ceb03db3','2026-11-19 02:53:32'),('08851f68-560d-4fa1-8f47-c0f3398039fa','2026-11-19 02:27:29'),('0f931d76-bdb0-4c24-a102-bc654f029af2','2026-11-19 03:02:12'),('13f72007-14db-4a06-baf1-1d6d148c2fa4','2026-11-19 02:25:04'),('15a15d2b-0102-48ec-b05d-50f1c29f66a7','2026-11-19 03:07:33'),('1664d2d5-2ebd-469a-b77d-22ae0df819bc','2026-11-19 02:25:04'),('233cf87f-0bfc-4c3a-9348-8b9af32ff90e','2026-11-19 02:40:57'),('2a0c4604-1694-4a1c-9399-bd5692553c69','2026-11-19 03:04:10'),('3af1cd44-4218-4326-ab2d-9639b52190ba','2026-11-19 03:00:55'),('4394e76f-0be6-4ea3-9f36-b87f7facba99','2026-11-19 03:07:32'),('43e8b550-1dab-4dd1-9846-7eb4f724f042','2026-11-19 02:27:29'),('47e0b472-e6c1-4d64-b980-fb6574f2b877','2026-11-19 03:04:07'),('51a7c404-cdd2-4746-ae39-fa7d931577b2','2026-11-19 02:25:04'),('5d1dfd05-5eeb-4421-b5bf-549bd7805b64','2026-11-19 02:00:12'),('5f73856e-7211-46d9-b9ba-be9973414d31','2026-11-19 03:07:32'),('5fcf1598-053a-4a44-9a91-409ab8e5f7a3','2026-11-19 02:27:29'),('60998b51-6743-4291-a75a-7835cffa2b40','2026-11-19 02:01:54'),('60a67ad6-774a-4f4d-b205-49cc0b8e8c57','2026-11-19 03:03:33'),('683f9a7c-6b30-4cbd-ac81-889994cfa45b','2026-11-19 02:00:12'),('68cd1135-1e0c-4608-a6dd-1b268566c04b','2026-11-19 02:52:43'),('6ae2271a-cdb9-4ac0-8de7-deac4c635c4a','2026-11-19 02:27:29'),('71b693f6-be56-4b92-9acc-8894309669b0','2026-11-19 02:00:12'),('900ea30d-c9fe-48b1-a6cf-172dca299817','2026-11-19 02:55:05'),('9ab59aa7-5f82-4c87-8679-e1b8342b854d','2026-11-19 03:04:07'),('9fb6c855-128c-4fa1-91fd-a81d4b983538','2026-11-19 02:51:23'),('a3fa557f-b2f6-4070-bd12-8c1f8400d168','2026-11-19 03:00:55'),('a43fab21-6991-42ee-a37e-eafc5e079bc0','2026-11-19 02:23:41'),('a5a5ad99-d60d-4de1-a8c9-30353ebbfd0c','2026-11-19 02:00:12'),('ad5b30da-8235-4c59-828b-1939b365b402','2026-11-19 02:40:57'),('b5021f17-169a-4882-a660-b9377cba1e14','2026-11-19 02:49:14'),('b6baf863-99fb-4bf9-97d9-cfa7b81a95fa','2026-11-19 02:25:04'),('b6dd74f9-daad-4054-9b7a-c74fd61fccd8','2026-11-19 03:04:10'),('b88ca483-a975-4d63-9f95-9338a24b72ba','2026-11-19 03:07:32'),('ba5bc1be-3f75-4eb2-b67c-395a64104832','2026-11-19 02:49:14'),('ba659555-6bd7-4dd3-8720-0856e39d0b6d','2026-11-19 03:02:13'),('c4359b83-f2a6-4866-8b9f-77e3fba8d157','2026-11-19 03:07:32'),('c814d4a9-7a39-4db9-b9ca-7147d19ebee6','2026-11-19 03:07:33'),('cb55b426-510a-4e61-bc54-28614340abf1','2026-11-19 03:02:13'),('d8b06b20-1275-4717-a8fe-768442374f67','2026-11-19 03:03:33'),('f385ef5c-ad22-4f4e-999a-ac0db2b171b7','2026-11-19 03:02:12'),('f6621dad-e5a1-4ef6-8ffe-b1ef9950a001','2026-11-19 02:23:41'),('f999c72f-d30e-474e-98b2-e30113462b0d','2026-11-19 02:23:41');
/*!40000 ALTER TABLE `sesion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-19  1:08:15
