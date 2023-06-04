-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: librarydbms
-- ------------------------------------------------------
-- Server version	10.6.12-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrator`
--

DROP TABLE IF EXISTS `administrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `administrator` (
  `admin_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login_id` varchar(50) NOT NULL,
  `passwd` varchar(100) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `sex` enum('Male','Female','Other') NOT NULL,
  `birth_date` date NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `login_id` (`login_id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`birth_date` < '2000-01-01')
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrator`
--

LOCK TABLES `administrator` WRITE;
/*!40000 ALTER TABLE `administrator` DISABLE KEYS */;
INSERT INTO `administrator` VALUES (1,'admin1','password1','John','Doe','Male','1990-05-20'),(2,'admin2','password2','Jane','Doe','Female','1995-01-12'),(3,'admin3','password3','Alice','Smith','Female','1992-09-06'),(4,'admin4','password4','Bob','Johnson','Male','1988-12-31'),(5,'admin5','password5','Chris','Lee','Other','1998-07-15');
/*!40000 ALTER TABLE `administrator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `author`
--

DROP TABLE IF EXISTS `author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `author` (
  `author_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `ISBN` varchar(50) NOT NULL,
  PRIMARY KEY (`author_id`),
  KEY `fk_author_book` (`ISBN`),
  KEY `idx_author` (`first_name`,`last_name`,`ISBN`),
  CONSTRAINT `fk_author_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `author`
--

LOCK TABLES `author` WRITE;
/*!40000 ALTER TABLE `author` DISABLE KEYS */;
INSERT INTO `author` VALUES (5,'F. Scott','Fitzgerald','5'),(10,'F. Scott','Fitzgerald','5'),(3,'Harper','Lee','3'),(8,'Harper','Lee','3'),(4,'J.D.','Salinger','4'),(9,'J.D.','Salinger','4');
/*!40000 ALTER TABLE `author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book`
--

DROP TABLE IF EXISTS `book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `book` (
  `ISBN` varchar(50) NOT NULL,
  `school_id` int(10) unsigned NOT NULL,
  `book_title` varchar(100) NOT NULL,
  `publisher` varchar(50) NOT NULL,
  `no_pages` int(10) unsigned NOT NULL,
  `summary` text NOT NULL,
  `available` int(10) unsigned NOT NULL DEFAULT 1,
  `img` longblob DEFAULT NULL,
  `sprache` varchar(50) DEFAULT 'English',
  `scadmin_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`ISBN`,`school_id`),
  KEY `fk_book_school` (`school_id`),
  KEY `fk_book_administrator` (`scadmin_id`),
  KEY `idx_book` (`ISBN`,`book_title`,`school_id`,`scadmin_id`),
  CONSTRAINT `fk_book_administrator` FOREIGN KEY (`scadmin_id`) REFERENCES `school_admin` (`scadmin_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_book_school` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book`
--

LOCK TABLES `book` WRITE;
/*!40000 ALTER TABLE `book` DISABLE KEYS */;
INSERT INTO `book` VALUES ('3',3,'To Kill a Mockingbird','J. B. Lippincott & Co.',281,'A novel set in the Southern United States during the Great Depression, and follows the story of a young girl named Scout Finch.',5,NULL,'English',3),('4',4,'The Catcher in the Rye','Little, Brown and Company',277,'A novel that tells the story of Holden Caulfield, a teenage boy who is expelled from his school and goes on a journey of self-discovery.',4,NULL,'English',NULL),('5',5,'The Great Gatsby','Charles Scribner\'s Sons',180,'A novel set in the Roaring Twenties, and follows the story of a young man named Jay Gatsby and his obsession with a woman named Daisy Buchanan.',5,NULL,'English',5);
/*!40000 ALTER TABLE `book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `borrowing`
--

DROP TABLE IF EXISTS `borrowing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `borrowing` (
  `borrowing_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` varchar(50) NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `borrowing_date` date NOT NULL DEFAULT current_timestamp(),
  `borrowing_status` enum('Waiting','Approved','Declined','Completed') DEFAULT 'Waiting',
  `scadmin_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`borrowing_id`),
  KEY `fk_borrowing_book` (`ISBN`),
  KEY `fk_borrowing_user` (`user_id`),
  KEY `fk_borrowing_scadmin` (`scadmin_id`),
  KEY `idx_borrowing` (`borrowing_id`,`ISBN`,`user_id`,`borrowing_date`,`borrowing_status`,`scadmin_id`),
  CONSTRAINT `fk_borrowing_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_borrowing_scadmin` FOREIGN KEY (`scadmin_id`) REFERENCES `school_admin` (`scadmin_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_borrowing_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `borrowing`
--

LOCK TABLES `borrowing` WRITE;
/*!40000 ALTER TABLE `borrowing` DISABLE KEYS */;
INSERT INTO `borrowing` VALUES (29,'5',5,'2023-06-03','Waiting',5),(34,'4',6,'2023-06-04','Approved',4);
/*!40000 ALTER TABLE `borrowing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category` (
  `category_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(50) NOT NULL,
  `ISBN` varchar(50) NOT NULL,
  PRIMARY KEY (`category_id`),
  KEY `fk_category_book` (`ISBN`),
  KEY `idx_category` (`category`,`ISBN`),
  CONSTRAINT `fk_category_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (3,'Classics','3'),(8,'Classics','3'),(4,'Classics','4'),(9,'Classics','4'),(5,'Classics','5'),(10,'Classics','5');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keywords`
--

DROP TABLE IF EXISTS `keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keywords` (
  `keyword_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `keyword` varchar(20) NOT NULL,
  `ISBN` varchar(50) NOT NULL,
  PRIMARY KEY (`keyword_id`),
  KEY `fk_keywords_book` (`ISBN`),
  CONSTRAINT `fk_keywords_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keywords`
--

LOCK TABLES `keywords` WRITE;
/*!40000 ALTER TABLE `keywords` DISABLE KEYS */;
INSERT INTO `keywords` VALUES (3,'Racism','3'),(4,'Coming of Age','3'),(5,'Alienation','4'),(8,'Racism','3'),(9,'Coming of Age','3'),(10,'Alienation','4');
/*!40000 ALTER TABLE `keywords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation`
--

DROP TABLE IF EXISTS `reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reservation` (
  `reservation_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` varchar(50) NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `reservation_date` date NOT NULL DEFAULT current_timestamp(),
  `reservation_to_date` date NOT NULL,
  `reservation_status` enum('Waiting Queue','Waiting','Declined','Approved') NOT NULL DEFAULT 'Waiting',
  `scadmin_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`reservation_id`),
  KEY `fk_reservation_book` (`ISBN`),
  KEY `fk_reservation_user` (`user_id`),
  KEY `fk_reservation_scadmin` (`scadmin_id`),
  KEY `idx_reservation` (`reservation_id`,`ISBN`,`user_id`,`reservation_date`,`reservation_to_date`,`reservation_status`),
  CONSTRAINT `fk_reservation_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reservation_scadmin` FOREIGN KEY (`scadmin_id`) REFERENCES `school_admin` (`scadmin_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reservation_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation`
--

LOCK TABLES `reservation` WRITE;
/*!40000 ALTER TABLE `reservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `review` (
  `review_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` varchar(50) NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `review_date` date NOT NULL DEFAULT current_timestamp(),
  `txt` text NOT NULL,
  `likert` varchar(50) DEFAULT NULL,
  `review_status` enum('Waiting','Approved','Declined') NOT NULL DEFAULT 'Waiting',
  `school_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`review_id`),
  KEY `fk_review_book` (`ISBN`),
  KEY `fk_review_user` (`user_id`),
  KEY `fk_review_school` (`school_id`),
  KEY `idx_review` (`review_id`,`user_id`,`review_status`,`ISBN`),
  CONSTRAINT `fk_review_book` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_review_school` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_review_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

LOCK TABLES `review` WRITE;
/*!40000 ALTER TABLE `review` DISABLE KEYS */;
INSERT INTO `review` VALUES (12,'4',6,'2023-06-04','iokjunikjn','32245','Approved',4);
/*!40000 ALTER TABLE `review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school`
--

DROP TABLE IF EXISTS `school`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `school` (
  `school_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `school_name` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `addrss` varchar(50) NOT NULL,
  `admin_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`school_id`),
  UNIQUE KEY `school_name` (`school_name`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `addrss` (`addrss`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_school_administrator` (`admin_id`),
  KEY `idx_school` (`school_id`,`school_name`),
  CONSTRAINT `fk_school_administrator` FOREIGN KEY (`admin_id`) REFERENCES `administrator` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school`
--

LOCK TABLES `school` WRITE;
/*!40000 ALTER TABLE `school` DISABLE KEYS */;
INSERT INTO `school` VALUES (3,'School C','Chicago','333333333','schoolc@example.com','Irakleous 66',3),(4,'School D','Houston','44444444','schoold@example.com','321 Maple St',4),(5,'School E','Miami','55555555','schoole@example.com','654 Pine Ave',5);
/*!40000 ALTER TABLE `school` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `school_admin`
--

DROP TABLE IF EXISTS `school_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `school_admin` (
  `scadmin_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login_id` varchar(50) NOT NULL,
  `passwd` varchar(100) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `sex` enum('Male','Female','Other') NOT NULL,
  `birth_date` date NOT NULL,
  `school_id` int(10) unsigned NOT NULL,
  `admin_id` int(10) unsigned DEFAULT NULL,
  `scadmin_status` enum('Declined','Waiting','Approved') NOT NULL DEFAULT 'Waiting',
  PRIMARY KEY (`scadmin_id`),
  UNIQUE KEY `login_id` (`login_id`),
  KEY `fk_school_admin_school` (`school_id`),
  KEY `fk_school_admin_administrator` (`admin_id`),
  KEY `idx_school_admin` (`scadmin_id`,`first_name`,`last_name`),
  CONSTRAINT `fk_school_admin_administrator` FOREIGN KEY (`admin_id`) REFERENCES `administrator` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_school_admin_school` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `CONSTRAINT_1` CHECK (`birth_date` < '2000-01-01')
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `school_admin`
--

LOCK TABLES `school_admin` WRITE;
/*!40000 ALTER TABLE `school_admin` DISABLE KEYS */;
INSERT INTO `school_admin` VALUES (3,'sadmin3','password3','Alice','Smith','Female','1992-09-06',3,1,'Declined'),(4,'sadmin4','password4','Bob','Johnson','Male','1988-12-31',4,1,'Approved'),(5,'sadmin5','password5','Chris','Lee','Other','1998-07-15',5,1,'Approved');
/*!40000 ALTER TABLE `school_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login_id` varchar(50) NOT NULL,
  `passwd` varchar(100) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `birth_date` date NOT NULL,
  `school_id` int(10) unsigned NOT NULL,
  `sex` enum('Male','Female','Other') NOT NULL,
  `job` enum('Student','Teacher') NOT NULL,
  `books_borrowed` int(10) unsigned NOT NULL DEFAULT 0,
  `user_status` enum('Waiting','Approved','Declined') NOT NULL DEFAULT 'Waiting',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `login_id` (`login_id`),
  KEY `fk_user_school` (`school_id`),
  KEY `idx_user` (`user_id`,`first_name`,`last_name`,`job`,`user_status`,`books_borrowed`),
  CONSTRAINT `fk_user_school` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `CONSTRAINT_1` CHECK (`birth_date` < '2018-01-01' and `job` = 'Student' or `birth_date` < '2000-01-01' and `job` = 'Teacher')
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (3,'user3','password3','Chris','Lee','2003-09-06',3,'Male','Student',1,'Waiting'),(4,'user4','password4','David','Kim','1998-12-31',4,'Male','Teacher',1,'Declined'),(5,'user5','password5','Emma','Wilson','2002-07-15',5,'Male','Student',1,'Approved'),(6,'malakas','123456789','Lakis','Lazopoulos','1967-11-11',4,'Other','Teacher',1,'Approved'),(7,'jik','123456789','jhk','hjk','2017-02-01',4,'Female','Student',0,'Approved');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-04 14:59:14
