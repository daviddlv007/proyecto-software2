-- Script de inicializacion del supermercado
-- Se ejecuta automaticamente al iniciar el contenedor de PostgreSQL

-- Insertar categorias del supermercado
INSERT INTO categorias (nombre, descripcion) VALUES 
('Electronica', 'Dispositivos y accesorios electronicos'),
('Ropa', 'Ropa y accesorios de vestir'),
('Alimentos', 'Productos alimenticios y bebidas'),
('Hogar', 'Articulos para el hogar y decoracion'),
('Deportes', 'Equipamiento deportivo y fitness'),
('Libros', 'Libros y material de lectura'),
('Juguetes', 'Juguetes y juegos'),
('Belleza', 'Productos de belleza y cuidado personal')
ON CONFLICT DO NOTHING;

-- Insertar productos del supermercado
INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id) VALUES
('Laptop HP', 'Laptop HP con procesador Intel Core i5', 599.99, 10000, 1),
('Mouse Logitech', 'Mouse inalambrico', 19.99, 10000, 1),
('Teclado Mecanico', 'Teclado gaming RGB', 89.99, 10000, 1),
('Monitor 24 pulgadas', 'Monitor Full HD IPS', 199.99, 10000, 1),
('Camiseta Nike', 'Camiseta deportiva de algodon', 29.99, 10000, 2),
('Pantalon Levis', 'Pantalon jean clasico', 49.99, 10000, 2),
('Zapatillas Adidas', 'Zapatillas running', 79.99, 10000, 2),
('Chaqueta North Face', 'Chaqueta impermeable', 129.99, 10000, 2),
('Arroz Premium 1kg', 'Arroz de grano largo', 2.99, 10000, 3),
('Aceite de Oliva 500ml', 'Aceite de oliva virgen extra', 8.99, 10000, 3),
('Leche Entera 1L', 'Leche fresca pasteurizada', 1.49, 10000, 3),
('Pan Integral', 'Pan de trigo integral', 2.49, 10000, 3),
('Manzanas 1kg', 'Manzanas frescas', 3.99, 10000, 3),
('Platanos 1kg', 'Platanos maduros', 2.99, 10000, 3),
('Tomates 1kg', 'Tomates frescos', 3.49, 10000, 3),
('Cebolla 1kg', 'Cebollas blancas', 1.99, 10000, 3),
('Papas 2kg', 'Papas blancas', 2.49, 10000, 3),
('Pollo Entero', 'Pollo fresco', 5.99, 10000, 3),
('Huevos x12', 'Huevos frescos', 3.49, 10000, 3),
('Yogurt Natural', 'Yogurt sin azucar', 2.99, 10000, 3),
('Sabanas Queen', 'Juego de sabanas 100% algodon', 39.99, 10000, 4),
('Almohada', 'Almohada de memory foam', 24.99, 10000, 4),
('Toallas', 'Set de 3 toallas', 19.99, 10000, 4),
('Lampara LED', 'Lampara de escritorio', 29.99, 10000, 4),
('Espejo de Pared', 'Espejo decorativo', 34.99, 10000, 4),
('Balon de Futbol', 'Balon profesional', 34.99, 10000, 5),
('Pesas 5kg', 'Par de mancuernas', 29.99, 10000, 5),
('Esterilla Yoga', 'Mat antideslizante', 24.99, 10000, 5),
('Bicicleta Estatica', 'Bicicleta de ejercicio', 299.99, 10000, 5),
('Cuerda de Saltar', 'Cuerda ajustable', 9.99, 10000, 5),
('Novela Bestseller', 'Ultima novela bestseller', 14.99, 10000, 6),
('Enciclopedia', 'Enciclopedia completa', 89.99, 10000, 6),
('Diccionario Ingles', 'Diccionario bilingue', 24.99, 10000, 6),
('Atlas Mundial', 'Atlas geografico actualizado', 34.99, 10000, 6),
('Lego Classic', 'Set de construccion', 44.99, 10000, 7),
('Muneca Barbie', 'Muneca clasica', 19.99, 10000, 7),
('Puzzle 1000 piezas', 'Puzzle de paisajes', 16.99, 10000, 7),
('Auto RC', 'Auto a control remoto', 49.99, 10000, 7),
('Pelota de Playa', 'Pelota inflable', 6.99, 10000, 7),
('Shampoo', 'Shampoo hidratante 400ml', 7.99, 10000, 8),
('Crema Facial', 'Crema anti-edad', 24.99, 10000, 8),
('Desodorante', 'Desodorante 48h', 4.99, 10000, 8),
('Perfume', 'Fragancia premium 50ml', 59.99, 10000, 8),
('Jabon Liquido', 'Jabon de manos 300ml', 3.99, 10000, 8),
('Cepillo de Dientes', 'Cepillo electrico', 29.99, 10000, 8),
('Pasta Dental', 'Pasta blanqueadora', 4.99, 10000, 8),
('Protector Solar', 'Protector FPS 50', 14.99, 10000, 8),
('Mascarilla Facial', 'Mascarilla hidratante', 8.99, 10000, 8),
('Esmalte de Unas', 'Esmalte de larga duracion', 6.99, 10000, 8)
ON CONFLICT DO NOTHING;

-- Insertar clientes demo
INSERT INTO clientes (nombre, correo, telefono) VALUES 
('Cliente Demo', 'demo@supermercado.com', '555-0000'),
('Juan Perez', 'juan.perez@email.com', '555-1234'),
('Maria Garcia', 'maria.garcia@email.com', '555-5678'),
('Carlos Rodriguez', 'carlos.rodriguez@email.com', '555-9012'),
('Ana Martinez', 'ana.martinez@email.com', '555-3456')
ON CONFLICT DO NOTHING;
