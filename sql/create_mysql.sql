set character_set_client = 'utf8';
set character_set_connection = 'utf8';
set character_set_results = 'utf8';

CREATE DATABASE IF NOT EXISTS 5e;

CREATE TABLE 5e.user (
  `id` int NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `modified_at` varchar(255) DEFAULT NULL,
  `roles` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE 5e.words (
  `id` int NOT NULL AUTO_INCREMENT,
  `en` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `cn` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `json_file` text NOT NULL,
  `source` varchar(255) NOT NULL,
  `version` char(10) NOT NULL,
  `is_key` tinyint NOT NULL DEFAULT '0',
  `proofread` tinyint NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified_by` int NOT NULL,
  `category` char(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `modified_by` (`modified_by`),
  FULLTEXT KEY `text` (`en`,`cn`),
  CONSTRAINT `words_ibfk_1` FOREIGN KEY (`modified_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=387420 DEFAULT CHARSET=utf8mb3;

CREATE TABLE 5e.source (
  `file` varchar(255) NOT NULL,
  `word_id` int NOT NULL,
  `version` char(10) DEFAULT NULL,
  PRIMARY KEY (`file`,`word_id`),
  KEY `word_id` (`word_id`),
  CONSTRAINT `source_ibfk_1` FOREIGN KEY (`word_id`) REFERENCES `words` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE 5e.term (
  `en` varchar(255) NOT NULL,
  `category` char(50) NOT NULL,
  `cn` varchar(255) NOT NULL,
  PRIMARY KEY (`en`,`category`),
  KEY `en_category` (`en`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;