-- Borramos la base de datos si ya existe
DROP DATABASE IF EXISTS Don_Galleto;

-- Creamos la base de datos
CREATE DATABASE Don_Galleto;
USE Don_Galleto;

-- Tabla de tipos de usuario
CREATE TABLE TipoUsuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de usuarios
CREATE TABLE Usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  tipo_usuario_id INT NOT NULL,
  FOREIGN KEY (tipo_usuario_id) REFERENCES TipoUsuario(id)
);

-- Tabla de metodos de pago
CREATE TABLE MetodoPago(
id INT AUTO_INCREMENT PRIMARY KEY,
tipo VARCHAR (15) NOT NULL
);
-- Tabla de proveedores
CREATE TABLE Proveedores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_empresa VARCHAR(255) NOT NULL,
  nombre_promotor VARCHAR(255),
  telefono VARCHAR(20),
  email VARCHAR(255),
  calle VARCHAR(50),
  colonia VARCHAR(50),
  cp INT(7),
  numero INT(15)
);

-- Tabla de tipos de insumo
CREATE TABLE TipoInsumo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de insumos generales
CREATE TABLE AdministracionInsumos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  insumo_nombre VARCHAR(255) NOT NULL,
    proveedor_id INT NOT NULL,

  tipo_insumo_id INT NOT NULL,
  cantidad_existente DECIMAL(10,2) NOT NULL,
  unidad VARCHAR(20) NOT NULL,
  lote_id VARCHAR(255),
  fecha_registro DATE,
  fecha_caducidad DATE,
  FOREIGN KEY (tipo_insumo_id) REFERENCES TipoInsumo(id),
  FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)

);

-- Relación entre insumos y proveedores
CREATE TABLE InsumoProveedor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  proveedor_id INT NOT NULL,
  insumo_id INT NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  unidad VARCHAR(10) NOT NULL,
  FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id),
  FOREIGN KEY (insumo_id) REFERENCES AdministracionInsumos(id)
);

-- Tabla de recetas
CREATE TABLE Recetas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  gramaje_por_galleta DECIMAL(10,2) NOT NULL,
  galletas_por_lote INT NOT NULL,
  costo_por_galleta DECIMAL(10,2) NOT NULL,
  precio_venta DECIMAL(10,2) NOT NULL
);

-- Relación entre insumos y recetas
CREATE TABLE IngredientesReceta (
  id INT AUTO_INCREMENT PRIMARY KEY,
  receta_id INT NOT NULL,
  insumo_id INT NOT NULL,
  cantidad_necesaria DECIMAL(10,2) NOT NULL,
  unidad VARCHAR(20) NOT NULL,
  FOREIGN KEY (receta_id) REFERENCES Recetas(id),
  FOREIGN KEY (insumo_id) REFERENCES AdministracionInsumos(id)
);

-- Producción de galletas
CREATE TABLE InformeProduccion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  receta_id INT NOT NULL,
  cantidad_producida INT NOT NULL,
  fecha_produccion DATE NOT NULL,
  caducidad DATE NOT NULL,
  merma INT DEFAULT 0,
  motivo_merma VARCHAR(255),
  cantidad_disponible INT NOT NULL DEFAULT 0,
  FOREIGN KEY (receta_id) REFERENCES Recetas(id)
);

-- Tabla de ventas
CREATE TABLE InformeVentas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  total_venta DECIMAL(10,2) NOT NULL,
  descuento_aplicado DECIMAL(10,2) DEFAULT 0,
  cliente_pago DECIMAL(10,2) NOT NULL,
  cambio DECIMAL(10,2),
  fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);

-- Detalles de venta
CREATE TABLE DetalleVenta (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venta_id INT NOT NULL,
  receta_id INT NOT NULL,
  cantidad DECIMAL(10,2) NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (venta_id) REFERENCES InformeVentas(id),
  FOREIGN KEY (receta_id) REFERENCES Recetas(id)
);

-- Tabla de pedidos de insumos
CREATE TABLE PedidosInsumos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  insumo_id INT NOT NULL,
  proveedor_id INT NOT NULL,
  cantidad_solicitada INT NOT NULL,
  fecha_pedido DATE NOT NULL,
  FOREIGN KEY (insumo_id) REFERENCES AdministracionInsumos(id),
  FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
);

-- Tabla de estado de pedidos
CREATE TABLE EstadoPedido (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de pedidos de galletas
CREATE TABLE PedidoGalletas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  receta_id INT NOT NULL,
  cantidad INT NOT NULL,
  estado_pedido_id INT NOT NULL,
  fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
  FOREIGN KEY (receta_id) REFERENCES Recetas(id),
  FOREIGN KEY (estado_pedido_id) REFERENCES EstadoPedido(id)
);

-- Tabla de insumos recibidos
/* 
CREATE TABLE InsumosRecibidos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lote_id VARCHAR(255) NOT NULL,
  fecha_recepcion DATE NOT NULL,
  fecha_caducidad DATE NOT NULL,
  cantidad DECIMAL(10,2) NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  insumo_id INT NOT NULL,
  proveedor_id INT NOT NULL,
  FOREIGN KEY (insumo_id) REFERENCES AdministracionInsumos(id),
  FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
);
*/
-- Tabla de merma de insumos
CREATE TABLE MermaInsumos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cantidad_danada DECIMAL(10,2) NOT NULL,
  motivo_merma VARCHAR(255),
  insumo_id INT NOT NULL,
  FOREIGN KEY (insumo_id) REFERENCES AdministracionInsumos(id)
);

-- Disparador para reducir insumos al producir galletas
DELIMITER //
CREATE TRIGGER descontar_insumos_produccion
AFTER INSERT ON InformeProduccion
FOR EACH ROW
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE insumo_id INT;
  DECLARE cantidad_necesaria DECIMAL(10,2);
  
  -- Recorrer los ingredientes de la receta
  DECLARE cur CURSOR FOR 
    SELECT insumo_id, cantidad_necesaria * NEW.cantidad_producida
    FROM IngredientesReceta
    WHERE receta_id = NEW.receta_id;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN cur;

  read_loop: LOOP
    FETCH cur INTO insumo_id, cantidad_necesaria;
    IF done THEN
      LEAVE read_loop;
    END IF;
    
    -- Actualizar la cantidad de insumo disponible
    UPDATE AdministracionInsumos
    SET cantidad_existente = cantidad_existente - cantidad_necesaria
    WHERE id = insumo_id;
  END LOOP;

  CLOSE cur;
END;
//
DELIMITER ;

-- Procedimiento para hacer la venta 
DELIMITER //

CREATE PROCEDURE registrar_venta(
  IN p_usuario_id INT,
  IN p_total DECIMAL(10,2),
  IN p_pago DECIMAL(10,2),
  OUT p_cambio DECIMAL(10,2)
)
BEGIN
  DECLARE v_cambio DECIMAL(10,2);

  -- Aqui vamos a validar que el pago sea suficiente
  IF p_pago < p_total THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El pago es insuficiente para cubrir el total de la venta.';
  ELSE
    SET v_cambio = p_pago - p_total;
    INSERT INTO ModuloVentas (usuario_id, total_venta, cliente_pago, cambio, fecha_venta)
    VALUES (p_usuario_id, p_total, p_pago, v_cambio, NOW());
    SET p_cambio = v_cambio;
  END IF;
END //

DELIMITER ;

-- Insertar tipos de usuario
INSERT INTO TipoUsuario (nombre) VALUES 
('admin'),
('produccion'),
('cliente');

INSERT INTO MetodoPago(tipo) VALUES
('transferencias'),
('tarjeta'),
('efectivo');
-- Insertar usuarios
INSERT INTO Usuarios (nombre, email, password, tipo_usuario_id) VALUES 
('Admin Don Galleto', 'admin@dongalleto.com', 'password123', 1),
('Producción Don Galleto', 'produccion@dongalleto.com', 'password123', 2),
('Cliente Ejemplo', 'cliente@ejemplo.com', 'password123', 3);

-- Insertar proveedores
INSERT INTO Proveedores (nombre_empresa, nombre_promotor, telefono, email, calle, colonia, cp, numero) VALUES 
('Proveedor Harinas MX', 'Juan Pérez', '5551234567', 'juan@harinasmx.com', 'Av. Central', 'Centro', 12345, 10),
('Proveedor Huevo Express', 'María López', '5559876543', 'maria@huevoexpress.com', 'Calle Norte', 'Industrial', 67890, 20);

-- Insertar tipos de insumo
INSERT INTO TipoInsumo (nombre) VALUES 
('Harinas'),
('Huevos'),
('Lácteos'),
('Endulzantes');

-- Insertar insumos generales
INSERT INTO AdministracionInsumos (insumo_nombre, tipo_insumo_id, cantidad_existente, unidad, lote_id, fecha_registro, fecha_caducidad, proveedor_id) VALUES 
('Harina de trigo', 1, 100.00, 'kg', 'L001', '2024-03-01', '2024-06-01', '1'),
('Huevo fresco', 2, 200.00, 'pza', 'L002', '2024-03-01', '2024-04-15','1'),
('Azúcar blanca', 4, 50.00, 'kg', 'L003', '2024-03-01', '2024-07-01', '2'),
('Mantequilla sin sal', 3, 30.00, 'kg', 'L004', '2024-03-01', '2024-05-10', '1');

-- Insertar relación entre insumos y proveedores
INSERT INTO InsumoProveedor (proveedor_id, insumo_id, precio, unidad) VALUES 
(1, 1, 20.00, 'kg'),  -- Harina de trigo por Proveedor Harinas MX
(2, 2, 5.00, 'pza'), -- Huevo fresco por Proveedor Huevo Express
(1, 3, 15.00, 'kg'), -- Azúcar blanca por Proveedor Harinas MX
(2, 4, 50.00, 'kg'); -- Mantequilla sin sal por Proveedor Huevo Express

-- Insertar recetas
INSERT INTO Recetas (nombre, gramaje_por_galleta, galletas_por_lote, costo_por_galleta, precio_venta) VALUES 
('Galleta de Chocolate', 50.00, 20, 3.50, 10.00),
('Galleta de Vainilla', 45.00, 25, 3.00, 9.00);

-- Insertar ingredientes de las recetas
INSERT INTO IngredientesReceta (receta_id, insumo_id, cantidad_necesaria, unidad) VALUES 
(1, 1, 1.00, 'kg'),  -- Harina de trigo para Galleta de Chocolate
(1, 2, 2.00, 'pza'), -- Huevo fresco para Galleta de Chocolate
(2, 1, 0.80, 'kg'), -- Harina de trigo para Galleta de Vainilla
(2, 2, 1.50, 'pza'); -- Huevo fresco para Galleta de Vainilla

-- Insertar producción de galletas
INSERT INTO InformeProduccion (receta_id, cantidad_producida, fecha_produccion, caducidad, merma, motivo_merma, cantidad_disponible) VALUES 
(1, 100, '2024-03-15', '2024-03-25', 5, 'Rotura', 95),
(2, 120, '2024-03-16', '2024-03-26', 3, 'Forma defectuosa', 117);


 
-- Cambiar
INSERT INTO EstadoPedido (nombre) VALUES 
('pedido'),
('recibido'),
('en proceso'),
('completado'),
('cancelado');


-- Insertar pedidos de galletas
INSERT INTO PedidoGalletas (usuario_id, receta_id, cantidad, estado_pedido_id, fecha_pedido) VALUES 
(3, 1, 10, 1, '2024-03-20 14:00:00'), -- Pedido pendiente de Galleta de Chocolate
(3, 2, 15, 2, '2024-03-21 15:30:00'); -- Pedido completado de Galleta de Vainilla

-- Insertar ventas
INSERT INTO InformeVentas (usuario_id, total_venta, descuento_aplicado, cliente_pago, cambio, fecha_venta) VALUES 
(3, 100.00, 0.00, 100.00, 0.00, '2024-03-20 14:00:00'),
(3, 135.00, 5.00, 140.00, 5.00, '2024-03-21 15:30:00');

-- Insertar detalles de venta
INSERT INTO DetalleVenta (venta_id, receta_id, cantidad, precio_unitario) VALUES 
(1, 1, 10, 10.00), -- Detalle de venta para Galleta de Chocolate
(2, 2, 15, 9.00); -- Detalle de venta para Galleta de Vainilla

-- Insertar pedidos de insumos
INSERT INTO PedidosInsumos (insumo_id, proveedor_id, cantidad_solicitada, fecha_pedido) VALUES 
(1, 1, 50, '2024-03-10'), -- Pedido de Harina de trigo
(2, 2, 100, '2024-03-12'); -- Pedido de Huevo fresco



-- Insertar merma de insumos
INSERT INTO MermaInsumos (cantidad_danada, motivo_merma, insumo_id) VALUES 
(2.00, 'Derrame en almacén', 1), -- Merma de Harina de trigo
(5.00, 'Cáscara rota', 2); -- Merma de Huevo fresco

SELECT * FROM MetodoPago;
SELECT * FROM TipoUsuario;
SELECT * FROM Usuarios;
SELECT * FROM Proveedores;
SELECT * FROM TipoInsumo;
SELECT * FROM AdministracionInsumos;
SELECT * FROM InsumoProveedor;
SELECT * FROM Recetas;
SELECT * FROM IngredientesReceta;
SELECT * FROM InformeProduccion;
SELECT * FROM EstadoPedido;
SELECT * FROM PedidoGalletas;
SELECT * FROM InformeVentas;
SELECT * FROM DetalleVenta;
SELECT * FROM PedidosInsumos;
SELECT * FROM MermaInsumos;