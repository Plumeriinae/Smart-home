CREATE TABLE `number_of_clients` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  `num_of_clients` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='ne ne ne nism več s tabo,\nne ne ne bo me več kle.';

CREATE TABLE `MQTT` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `topic` varchar(80) NOT NULL,
  `message` varchar(80) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='topic';

