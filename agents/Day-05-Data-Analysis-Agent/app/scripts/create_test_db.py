"""
Create a test SQLite database for the Data Analysis Agent.

This script creates a SQLite database with sample tables and data for testing
the Data Analysis Agent application.
"""

import sqlite3
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Database file path
DB_FILE = "test_data.db"

def create_database():
    """Create a new SQLite database with sample tables."""
    
    # Remove existing database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database: {DB_FILE}")
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"Created new database: {DB_FILE}")
    
    # Create tables and populate with data
    create_employees_table(conn)
    create_sales_table(conn)
    create_products_table(conn)
    create_customers_table(conn)
    
    # Close the connection
    conn.close()
    print("Database creation completed.")

def create_employees_table(conn):
    """Create and populate the employees table."""
    
    # Create the table
    conn.execute('''
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        hire_date DATE,
        department TEXT,
        salary REAL,
        years_experience INTEGER
    )
    ''')
    
    # Sample data
    employees_data = [
        (1, 'John', 'Smith', 'john.smith@example.com', '2018-05-15', 'Engineering', 85000.00, 5),
        (2, 'Sarah', 'Johnson', 'sarah.j@example.com', '2019-03-20', 'Marketing', 72000.00, 3),
        (3, 'Michael', 'Williams', 'michael.w@example.com', '2017-11-10', 'Engineering', 92000.00, 7),
        (4, 'Emily', 'Brown', 'emily.b@example.com', '2020-01-05', 'HR', 65000.00, 2),
        (5, 'David', 'Jones', 'david.j@example.com', '2016-08-22', 'Finance', 98000.00, 8),
        (6, 'Lisa', 'Garcia', 'lisa.g@example.com', '2021-02-15', 'Marketing', 68000.00, 1),
        (7, 'Robert', 'Miller', 'robert.m@example.com', '2015-04-30', 'Engineering', 105000.00, 10),
        (8, 'Jennifer', 'Davis', 'jennifer.d@example.com', '2019-07-12', 'HR', 67000.00, 4),
        (9, 'James', 'Rodriguez', 'james.r@example.com', '2017-09-18', 'Finance', 88000.00, 6),
        (10, 'Mary', 'Martinez', 'mary.m@example.com', '2020-11-03', 'Engineering', 78000.00, 3),
        (11, 'Thomas', 'Anderson', 'thomas.a@example.com', '2018-12-01', 'Marketing', 75000.00, 4),
        (12, 'Patricia', 'Thomas', 'patricia.t@example.com', '2016-06-14', 'Engineering', 95000.00, 9),
        (13, 'Christopher', 'Jackson', 'chris.j@example.com', '2021-01-20', 'Finance', 70000.00, 2),
        (14, 'Elizabeth', 'White', 'elizabeth.w@example.com', '2019-05-08', 'HR', 69000.00, 3),
        (15, 'Daniel', 'Harris', 'daniel.h@example.com', '2017-03-25', 'Engineering', 90000.00, 6)
    ]
    
    # Insert data
    conn.executemany('''
    INSERT INTO employees (employee_id, first_name, last_name, email, hire_date, department, salary, years_experience)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    conn.commit()
    print("Created and populated employees table with 15 records")

def create_sales_table(conn):
    """Create and populate the sales table."""
    
    # Create the table
    conn.execute('''
    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        product_id INTEGER,
        customer_id INTEGER,
        employee_id INTEGER,
        sale_date DATE,
        quantity INTEGER,
        total_amount REAL,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
    )
    ''')
    
    # Generate random sales data
    np.random.seed(42)  # For reproducibility
    
    # Generate 100 sales records
    sales_data = []
    sale_id = 1
    
    # Generate sales for the past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for _ in range(100):
        product_id = np.random.randint(1, 11)  # 10 products
        customer_id = np.random.randint(1, 21)  # 20 customers
        employee_id = np.random.randint(1, 16)  # 15 employees
        
        # Random date within the past 90 days
        days_ago = np.random.randint(0, 90)
        sale_date = (end_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        quantity = np.random.randint(1, 10)
        # Total amount will be calculated based on product price * quantity
        # For now, we'll use a random value between 10 and 500
        total_amount = round(np.random.uniform(10, 500), 2)
        
        sales_data.append((sale_id, product_id, customer_id, employee_id, sale_date, quantity, total_amount))
        sale_id += 1
    
    # Insert data
    conn.executemany('''
    INSERT INTO sales (sale_id, product_id, customer_id, employee_id, sale_date, quantity, total_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sales_data)
    
    conn.commit()
    print("Created and populated sales table with 100 records")

def create_products_table(conn):
    """Create and populate the products table."""
    
    # Create the table
    conn.execute('''
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT,
        unit_price REAL,
        stock_quantity INTEGER,
        supplier TEXT
    )
    ''')
    
    # Sample data
    products_data = [
        (1, 'Laptop Pro', 'Electronics', 1299.99, 45, 'TechSuppliers Inc.'),
        (2, 'Smartphone X', 'Electronics', 899.99, 120, 'MobileTech Ltd.'),
        (3, 'Office Chair', 'Furniture', 199.99, 30, 'FurnitureCo'),
        (4, 'Desk Lamp', 'Home Goods', 49.99, 75, 'HomeEssentials'),
        (5, 'Coffee Maker', 'Appliances', 89.99, 25, 'KitchenWare Plus'),
        (6, 'Wireless Headphones', 'Electronics', 159.99, 60, 'AudioTech'),
        (7, 'Ergonomic Keyboard', 'Electronics', 129.99, 40, 'TechSuppliers Inc.'),
        (8, 'Bookshelf', 'Furniture', 149.99, 15, 'FurnitureCo'),
        (9, 'Blender', 'Appliances', 79.99, 35, 'KitchenWare Plus'),
        (10, 'Desk', 'Furniture', 249.99, 20, 'FurnitureCo')
    ]
    
    # Insert data
    conn.executemany('''
    INSERT INTO products (product_id, product_name, category, unit_price, stock_quantity, supplier)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', products_data)
    
    conn.commit()
    print("Created and populated products table with 10 records")

def create_customers_table(conn):
    """Create and populate the customers table."""
    
    # Create the table
    conn.execute('''
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        city TEXT,
        state TEXT,
        signup_date DATE,
        total_purchases INTEGER DEFAULT 0
    )
    ''')
    
    # Sample data
    customers_data = [
        (1, 'Alice', 'Johnson', 'alice.j@example.com', '555-123-4567', 'New York', 'NY', '2020-01-15', 12),
        (2, 'Bob', 'Smith', 'bob.smith@example.com', '555-234-5678', 'Los Angeles', 'CA', '2020-03-22', 8),
        (3, 'Carol', 'Williams', 'carol.w@example.com', '555-345-6789', 'Chicago', 'IL', '2020-05-10', 15),
        (4, 'Dave', 'Brown', 'dave.b@example.com', '555-456-7890', 'Houston', 'TX', '2020-07-05', 5),
        (5, 'Eve', 'Jones', 'eve.jones@example.com', '555-567-8901', 'Phoenix', 'AZ', '2020-09-18', 10),
        (6, 'Frank', 'Garcia', 'frank.g@example.com', '555-678-9012', 'Philadelphia', 'PA', '2020-11-30', 7),
        (7, 'Grace', 'Miller', 'grace.m@example.com', '555-789-0123', 'San Antonio', 'TX', '2021-01-12', 9),
        (8, 'Henry', 'Davis', 'henry.d@example.com', '555-890-1234', 'San Diego', 'CA', '2021-02-28', 6),
        (9, 'Ivy', 'Rodriguez', 'ivy.r@example.com', '555-901-2345', 'Dallas', 'TX', '2021-04-17', 11),
        (10, 'Jack', 'Martinez', 'jack.m@example.com', '555-012-3456', 'San Jose', 'CA', '2021-06-05', 4),
        (11, 'Karen', 'Anderson', 'karen.a@example.com', '555-123-7890', 'Austin', 'TX', '2021-07-22', 8),
        (12, 'Leo', 'Thomas', 'leo.t@example.com', '555-234-8901', 'Jacksonville', 'FL', '2021-09-10', 5),
        (13, 'Mia', 'Jackson', 'mia.j@example.com', '555-345-9012', 'Fort Worth', 'TX', '2021-10-28', 7),
        (14, 'Noah', 'White', 'noah.w@example.com', '555-456-0123', 'Columbus', 'OH', '2021-12-15', 3),
        (15, 'Olivia', 'Harris', 'olivia.h@example.com', '555-567-1234', 'Charlotte', 'NC', '2022-01-30', 9),
        (16, 'Paul', 'Clark', 'paul.c@example.com', '555-678-2345', 'Indianapolis', 'IN', '2022-03-18', 6),
        (17, 'Quinn', 'Lewis', 'quinn.l@example.com', '555-789-3456', 'Seattle', 'WA', '2022-05-05', 10),
        (18, 'Ryan', 'Lee', 'ryan.l@example.com', '555-890-4567', 'Denver', 'CO', '2022-06-22', 4),
        (19, 'Sara', 'Walker', 'sara.w@example.com', '555-901-5678', 'Boston', 'MA', '2022-08-10', 7),
        (20, 'Tom', 'Hall', 'tom.h@example.com', '555-012-6789', 'Nashville', 'TN', '2022-10-05', 5)
    ]
    
    # Insert data
    conn.executemany('''
    INSERT INTO customers (customer_id, first_name, last_name, email, phone, city, state, signup_date, total_purchases)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', customers_data)
    
    conn.commit()
    print("Created and populated customers table with 20 records")

if __name__ == "__main__":
    create_database()
    print(f"SQLite database created at: {os.path.abspath(DB_FILE)}")
