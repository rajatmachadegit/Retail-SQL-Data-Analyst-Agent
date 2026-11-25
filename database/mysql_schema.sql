-- Create the retail database if it does not already exist
CREATE DATABASE IF NOT EXISTS retail_agent_assignment;
USE retail_agent_assignment;

-- 1. STORES TABLE
CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR(20) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    city VARCHAR(50),
    store_type VARCHAR(50) -- e.g., Supermarket, Convenience
);

-- 2. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    sub_category VARCHAR(50),
    base_price DECIMAL(10, 2) NOT NULL
);

-- 3. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_segment VARCHAR(50), -- e.g., Regular, Budget, Premium
    signup_date DATE,              -- Date format in CSV is DD-MM-YYYY; convert during ingestion
    preferred_channel VARCHAR(50), -- e.g., Mobile App, Online, Partner
    city VARCHAR(50)
);

-- 4. SALES TRANSACTIONS TABLE
CREATE TABLE IF NOT EXISTS sales_transactions (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,      -- Date format in CSV is DD-MM-YYYY; convert during ingestion
    store_id VARCHAR(20),
    product_id VARCHAR(20),
    customer_id VARCHAR(20),
    sales_channel VARCHAR(50),     -- e.g., Online, In-store, Mobile App
    units_sold INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_pct DECIMAL(5, 2) DEFAULT 0.00,
    payment_status VARCHAR(50),    -- e.g., Paid, Pending
    delivery_status VARCHAR(50),   -- e.g., Delivered, Processing
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE SET NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

-- 5. RETURNS TABLE
CREATE TABLE IF NOT EXISTS returns (
    return_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    return_date DATE NOT NULL,     -- Date format in CSV is DD-MM-YYYY; convert during ingestion
    return_reason VARCHAR(255),
    FOREIGN KEY (order_id) REFERENCES sales_transactions(order_id) ON DELETE CASCADE
);