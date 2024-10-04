CREATE TABLE IF NOT EXISTS users (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    email VARCHAR(255) NOT NULL UNIQUE, 
    password VARCHAR(255) NOT NULL,      
    birth_date DATE NOT NULL             
);

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    date_of_birth DATE
);
