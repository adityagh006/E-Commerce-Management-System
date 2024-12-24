CREATE DATABASE IF NOT EXISTS ecommerce_db;

USE ecommerce_db;

-- Create Users table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Increased size to accommodate hashed passwords
    email VARCHAR(100) NOT NULL,
    role ENUM('customer', 'seller') NOT NULL  -- Add role field for user type
);

CREATE TABLE category (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100)
);

CREATE TABLE Products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    image LONGBLOB,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE CASCADE
);

-- Create Orders table
CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

-- Create Sellers table
CREATE TABLE Sellers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    gstin VARCHAR(15) NOT NULL, 
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);


DELIMITER //

CREATE FUNCTION CalculateOrderPrice(p_order_id INT) 
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE total_price DECIMAL(10, 2);
    
    SELECT SUM(p.price * o.quantity) INTO total_price
    FROM Orders o
    JOIN Products p ON o.product_id = p.id
    WHERE o.id = p_order_id;
    
    RETURN total_price;
END; //

DELIMITER ;


DELIMITER //

CREATE TRIGGER delete_products_after_category_delete
AFTER DELETE ON category
FOR EACH ROW
BEGIN
    DELETE FROM Products WHERE category_id = OLD.category_id;
END; //

DELIMITER ;



INSERT INTO category (category_id, category_name) VALUES
(1, 'Electronics'),
(2, 'Fashion'),
(3, 'Home & Garden'),
(4, 'Health & Beauty'),
(5, 'Sports & Outdoors'),
(6, 'Toys & Games'),
(7, 'Automotive'),
(8, 'Books'),
(9, 'Groceries'),
(10, 'Pet Supplies');
