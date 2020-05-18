-- phpMyAdmin SQL Dump
-- version 4.6.6deb4
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Temps de generació: 18-05-2020 a les 11:20:31
-- Versió del servidor: 10.1.44-MariaDB-0+deb9u1
-- Versió de PHP: 7.0.33-0+deb9u7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de dades: `opodipbot`
--
CREATE DATABASE IF NOT EXISTS `opodipbot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `opodipbot`;

-- --------------------------------------------------------

--
-- Estructura de la taula `categoria`
--

CREATE TABLE `categoria` (
  `idCategoria` int(11) NOT NULL,
  `nom` varchar(50) CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de la taula `historial_respostes`
--

CREATE TABLE `historial_respostes` (
  `idHistorial` int(11) NOT NULL,
  `idUsuari` int(11) NOT NULL,
  `idPregunta` int(11) NOT NULL,
  `encertada` bit(1) NOT NULL,
  `dataHora` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de la taula `pregunta`
--

CREATE TABLE `pregunta` (
  `idCategoria` int(11) NOT NULL,
  `idPregunta` int(11) NOT NULL,
  `descripcio` varchar(250) CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de la taula `preguntes_realitzades`
--

CREATE TABLE `preguntes_realitzades` (
  `idUsuari` int(11) NOT NULL,
  `idCategoria` int(11) NOT NULL,
  `idPregunta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de la taula `resposta`
--

CREATE TABLE `resposta` (
  `idPregunta` int(11) NOT NULL,
  `idResposta` int(11) NOT NULL,
  `descripcio` varchar(250) CHARACTER SET utf8mb4 NOT NULL,
  `esCorrecte` bit(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de la taula `usuari`
--

CREATE TABLE `usuari` (
  `idUsuari` int(11) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `idCategoriaActiva` int(11) NOT NULL,
  `idPreguntaPendent` int(11) DEFAULT NULL,
  `idRespostaPendent` int(11) DEFAULT NULL,
  `codiRespostaPendent` varchar(1) DEFAULT NULL,
  `dataAlta` datetime NOT NULL,
  `idHistorialStats` int(11) NOT NULL,
  `bloquejat` bit(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexos per taules bolcades
--

--
-- Index de la taula `categoria`
--
ALTER TABLE `categoria`
  ADD PRIMARY KEY (`idCategoria`);

--
-- Index de la taula `historial_respostes`
--
ALTER TABLE `historial_respostes`
  ADD PRIMARY KEY (`idHistorial`),
  ADD KEY `idUsuari` (`idUsuari`),
  ADD KEY `encertada` (`encertada`);

--
-- Index de la taula `pregunta`
--
ALTER TABLE `pregunta`
  ADD PRIMARY KEY (`idPregunta`),
  ADD KEY `fk_pregunta_categoria` (`idCategoria`);

--
-- Index de la taula `preguntes_realitzades`
--
ALTER TABLE `preguntes_realitzades`
  ADD KEY `idCategoria` (`idCategoria`),
  ADD KEY `idUsuari` (`idUsuari`);

--
-- Index de la taula `resposta`
--
ALTER TABLE `resposta`
  ADD PRIMARY KEY (`idPregunta`,`idResposta`),
  ADD KEY `idPregunta` (`idPregunta`);

--
-- Index de la taula `usuari`
--
ALTER TABLE `usuari`
  ADD PRIMARY KEY (`idUsuari`);

--
-- AUTO_INCREMENT per les taules bolcades
--

--
-- AUTO_INCREMENT per la taula `historial_respostes`
--
ALTER TABLE `historial_respostes`
  MODIFY `idHistorial` int(11) NOT NULL AUTO_INCREMENT;
--
-- Restriccions per taules bolcades
--

--
-- Restriccions per la taula `pregunta`
--
ALTER TABLE `pregunta`
  ADD CONSTRAINT `fk_pregunta_categoria` FOREIGN KEY (`idCategoria`) REFERENCES `categoria` (`idCategoria`);

--
-- Restriccions per la taula `resposta`
--
ALTER TABLE `resposta`
  ADD CONSTRAINT `fk_resposta_pregunta` FOREIGN KEY (`idPregunta`) REFERENCES `pregunta` (`idPregunta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
