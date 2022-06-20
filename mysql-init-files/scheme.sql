DROP DATABASE IF EXISTS stocks;
CREATE DATABASE stocks;
USE stocks;

CREATE USER IF NOT EXISTS stocks@localhost IDENTIFIED BY 'stocks';
CREATE USER IF NOT EXISTS stocks@'%' IDENTIFIED BY 'stocks';
GRANT ALL PRIVILEGES ON stocks.* TO stocks@localhost;
GRANT ALL PRIVILEGES ON stocks.* TO stocks@'%';

CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    path VARCHAR(255) NOT NULL,
    status TINYINT(1) NOT NULL
);

CREATE TABLE prices (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    file_id INTEGER NOT NULL,
    date DATE NOT NULL,

    low FLOAT NOT NULL,
    high FLOAT NOT NULL,
    open FLOAT NOT NULL,
    close FLOAT NOT NULL,

    low_seasonality FLOAT NOT NULL,
    high_seasonality FLOAT NOT NULL,
    open_seasonality FLOAT NOT NULL,
    close_seasonality FLOAT NOT NULL,

    FOREIGN KEY (file_id) REFERENCES files(id)

);
