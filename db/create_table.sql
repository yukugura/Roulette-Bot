CREATE TABLE IF NOT EXISTS roulette_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(64) NOT NULL,
    item_role ENUM('survivor', 'hunter') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (item_name, item_role)
);