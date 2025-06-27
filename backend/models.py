import sqlite3
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_path='ecommerce.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

class User:
    def __init__(self, db_path='ecommerce.db'):
        self.db_manager = DatabaseManager(db_path)
    
    def get_by_id(self, user_id):
        """Get user by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_by_username(self, username):
        """Get user by username"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

class Product:
    def __init__(self, db_path='ecommerce.db'):
        self.db_manager = DatabaseManager(db_path)
    
    def get_all(self, limit=50, offset=0):
        """Get all products with pagination"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        products = cursor.fetchall()
        conn.close()
        return [dict(product) for product in products]
    
    def get_by_id(self, product_id):
        """Get product by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        return dict(product) if product else None
    
    def get_by_category(self, category):
        """Get products by category"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE LOWER(category) = LOWER(?) ORDER BY rating DESC",
            (category,)
        )
        products = cursor.fetchall()
        conn.close()
        return [dict(product) for product in products]
    
    def search(self, query, category=None, min_price=None, max_price=None, brand=None):
        """Search products with filters"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        sql = """
        SELECT * FROM products 
        WHERE (LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))
        """
        params = [f'%{query}%', f'%{query}%']
        
        if category:
            sql += " AND LOWER(category) = LOWER(?)"
            params.append(category)
        
        if brand:
            sql += " AND LOWER(brand) = LOWER(?)"
            params.append(brand)
        
        if min_price is not None:
            sql += " AND price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            sql += " AND price <= ?"
            params.append(max_price)
        
        sql += " ORDER BY rating DESC, price ASC"
        
        cursor.execute(sql, params)
        products = cursor.fetchall()
        conn.close()
        return [dict(product) for product in products]
    
    def get_by_price_range(self, min_price, max_price):
        """Get products within price range"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE price BETWEEN ? AND ? ORDER BY price ASC",
            (min_price, max_price)
        )
        products = cursor.fetchall()
        conn.close()
        return [dict(product) for product in products]
    
    def get_featured(self, limit=6):
        """Get featured products (highest rated)"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE rating >= 4.0 ORDER BY rating DESC, stock_quantity DESC LIMIT ?",
            (limit,)
        )
        products = cursor.fetchall()
        conn.close()
        return [dict(product) for product in products]

class ChatHistory:
    def __init__(self, db_path='ecommerce.db'):
        self.db_manager = DatabaseManager(db_path)
    
    def add_message(self, user_id, message, response):
        """Add chat message to history"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, message, response) VALUES (?, ?, ?)",
            (user_id, message, response)
        )
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def get_user_history(self, user_id, limit=50):
        """Get chat history for user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message, response, timestamp 
            FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, limit)
        )
        history = cursor.fetchall()
        conn.close()
        return [dict(item) for item in history]
    
    def clear_user_history(self, user_id):
        """Clear chat history for user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, user_id, days=7):
        """Get recent conversations within specified days"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message, response, timestamp 
            FROM chat_history 
            WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
            """.format(days),
            (user_id,)
        )
        history = cursor.fetchall()
        conn.close()
        return [dict(item) for item in history]

class DatabaseInitializer:
    def __init__(self, db_path='ecommerce.db'):
        self.db_path = db_path
    
    def create_tables(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(50) NOT NULL,
            brand VARCHAR(50) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            description TEXT,
            image_url VARCHAR(500),
            rating DECIMAL(2, 1),
            stock_quantity INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Chat history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sample_products = [
            # Laptops
            ("MacBook Pro 14-inch", "laptop", "Apple", 1999.00, "Apple M1 Pro chip, 16GB RAM, 512GB SSD", "https://example.com/macbook-pro.jpg", 4.8, 25),
            ("Dell XPS 13", "laptop", "Dell", 1299.00, "Intel Core i7, 16GB RAM, 512GB SSD, 13.3-inch display", "https://example.com/dell-xps.jpg", 4.6, 30),
            ("ThinkPad X1 Carbon", "laptop", "Lenovo", 1599.00, "Business laptop with Intel Core i7, 16GB RAM", "https://example.com/thinkpad.jpg", 4.7, 20),
            ("ASUS ROG Strix", "laptop", "ASUS", 1799.00, "Gaming laptop with RTX 3070, AMD Ryzen 7", "https://example.com/asus-rog.jpg", 4.5, 15),
            
            # Smartphones
            ("iPhone 14 Pro", "smartphone", "Apple", 1099.00, "6.1-inch display, A16 Bionic chip, 128GB", "https://example.com/iphone-14.jpg", 4.9, 50),
            ("Samsung Galaxy S23", "smartphone", "Samsung", 899.00, "6.1-inch display, Snapdragon 8 Gen 2, 256GB", "https://example.com/galaxy-s23.jpg", 4.7, 45),
            ("Google Pixel 7", "smartphone", "Google", 699.00, "6.3-inch display, Google Tensor G2, 128GB", "https://example.com/pixel-7.jpg", 4.6, 35),
            ("OnePlus 11", "smartphone", "OnePlus", 799.00, "6.7-inch display, Snapdragon 8 Gen 2, 256GB", "https://example.com/oneplus-11.jpg", 4.5, 25),
            
            # Accessories
            ("AirPods Pro", "accessory", "Apple", 249.00, "Active Noise Cancellation, Spatial Audio", "https://example.com/airpods-pro.jpg", 4.8, 100),
            ("Sony WH-1000XM4", "accessory", "Sony", 349.00, "Wireless noise-canceling headphones", "https://example.com/sony-headphones.jpg", 4.9, 75),
            ("Logitech MX Master 3", "accessory", "Logitech", 99.00, "Advanced wireless mouse for productivity", "https://example.com/mx-master.jpg", 4.7, 60),
            ("Blue Yeti Microphone", "accessory", "Blue", 129.00, "USB microphone for streaming and recording", "https://example.com/blue-yeti.jpg", 4.6, 40),
            
            # Tablets
            ("iPad Air", "tablet", "Apple", 699.00, "10.9-inch display, M1 chip, 64GB Wi-Fi", "https://example.com/ipad-air.jpg", 4.8, 30),
            ("Samsung Tab S8", "tablet", "Samsung", 729.00, "11-inch display, Snapdragon 8 Gen 1, 128GB", "https://example.com/tab-s8.jpg", 4.6, 25),
            ("Microsoft Surface Pro", "tablet", "Microsoft", 1099.00, "13-inch touchscreen, Intel Core i5, 256GB", "https://example.com/surface-pro.jpg", 4.5, 20),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO products (name, category, brand, price, description, image_url, rating, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sample_products
        )
        
        conn.commit()
        conn.close()