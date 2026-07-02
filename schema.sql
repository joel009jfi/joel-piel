CREATE DATABASE IF NOT EXISTS joel_piel;
USE joel_piel;

-- Tabla: usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `Id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `direccion` text DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `rol` varchar(20) NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`Id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: categorias
CREATE TABLE IF NOT EXISTS `categorias` (
  `Id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(50) NOT NULL,
  PRIMARY KEY (`Id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: productos
CREATE TABLE IF NOT EXISTS `productos` (
  `Id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `imagen_url` varchar(255) DEFAULT NULL,
  `Id_categoria` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id_producto`),
  KEY `Id_categoria` (`Id_categoria`),
  CONSTRAINT `fk_producto_categoria` FOREIGN KEY (`Id_categoria`) REFERENCES `categorias` (`Id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: carrito
CREATE TABLE IF NOT EXISTS `carrito` (
  `id_carrito` int(11) NOT NULL AUTO_INCREMENT,
  `Id_usuario` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_carrito`),
  KEY `Id_usuario` (`Id_usuario`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `carrito_ibfk_1` FOREIGN KEY (`Id_usuario`) REFERENCES `usuarios` (`Id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `carrito_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`Id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: pedidos
CREATE TABLE IF NOT EXISTS `pedidos` (
  `Id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `Id_usuario` int(11) DEFAULT NULL,
  `fecha` timestamp NULL DEFAULT current_timestamp(),
  `total` decimal(10,2) DEFAULT NULL,
  `estado` varchar(50) DEFAULT 'Pendiente',
  `metodo_pago` varchar(50) DEFAULT 'Contraentrega',
  `archivado` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`Id_pedido`),
  KEY `Id_usuario` (`Id_usuario`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`Id_usuario`) REFERENCES `usuarios` (`Id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: detalle_pedido
CREATE TABLE IF NOT EXISTS `detalle_pedido` (
  `Id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `Id_pedido` int(11) DEFAULT NULL,
  `Id_producto` int(11) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`Id_detalle`),
  KEY `Id_pedido` (`Id_pedido`),
  KEY `Id_producto` (`Id_producto`),
  CONSTRAINT `detalle_pedido_ibfk_1` FOREIGN KEY (`Id_pedido`) REFERENCES `pedidos` (`Id_pedido`),
  CONSTRAINT `detalle_pedido_ibfk_2` FOREIGN KEY (`Id_producto`) REFERENCES `productos` (`Id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: envios
CREATE TABLE IF NOT EXISTS `envios` (
  `Id_envios` int(11) NOT NULL AUTO_INCREMENT,
  `Id_pedido` int(11) DEFAULT NULL,
  `direccion_envio` text DEFAULT NULL,
  `estado_envio` varchar(50) DEFAULT NULL,
  `fecha_envio` datetime DEFAULT NULL,
  `fecha_entrega_estimada` datetime DEFAULT NULL,
  `numero_guia` varchar(50) NOT NULL,
  `transportadora` varchar(100) NOT NULL,
  `total` decimal(10,0) NOT NULL,
  `agradecido` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`Id_envios`),
  KEY `Id_pedido` (`Id_pedido`),
  CONSTRAINT `envios_ibfk_1` FOREIGN KEY (`Id_pedido`) REFERENCES `pedidos` (`Id_pedido`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: pagos
CREATE TABLE IF NOT EXISTS `pagos` (
  `Id_pago` int(11) NOT NULL AUTO_INCREMENT,
  `id_pedido` int(11) DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `estado_pago` varchar(50) DEFAULT NULL,
  `fecha_pago` datetime DEFAULT NULL,
  PRIMARY KEY (`Id_pago`),
  KEY `id_pedido` (`id_pedido`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`Id_pedido`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla: contactos
CREATE TABLE IF NOT EXISTS `contactos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `asunto` varchar(50) DEFAULT NULL,
  `mensaje` text DEFAULT NULL,
  `respuesta` text DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `leido` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
