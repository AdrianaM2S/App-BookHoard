DROP DATABASE IF EXISTS bookhoard_database;
CREATE DATABASE bookhoard_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookhoard_database;

CREATE TABLE role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(256),
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES role(id)
);

CREATE TABLE book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150),
    author VARCHAR(100),
    synopsys VARCHAR(500),
    cover BLOB,
    type_book VARCHAR(30),
    category VARCHAR(50),
    isbn VARCHAR(20), 
    publish_date DATE,
    languege VARCHAR(30),
);

INSERT INTO role (name) VALUES ('Admin'), ('User');