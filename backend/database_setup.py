import sqlite3
import random

def create_database():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
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
    
    # Create chat history table
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
    
    # Insert mock products
    products = [
        # Laptops
        ("Dell XPS 13", "laptops", "Dell", 999.99, "Ultra-portable laptop with 11th Gen Intel Core processor", "https://tse1.mm.bing.net/th?id=OIP.0jhL2o_M2IP5-M9DowQT5wHaFj&pid=Api&P=0&h=180", 4.5, 25),
        ("MacBook Air M2", "laptops", "Apple", 1199.99, "Apple's thinnest and lightest laptop with M2 chip", "https://m.media-amazon.com/images/I/41+0wuOoe0L._SY300_SX300_.jpg", 4.8, 15),
        ("HP Spectre x360", "laptops", "HP", 1299.99, "Premium 2-in-1 laptop with 360-degree hinge", "https://m.media-amazon.com/images/I/418-eHC9rpL._SX300_SY300_QL70_FMwebp_.jpg", 4.4, 20),
        ("Lenovo ThinkPad X1", "laptops", "Lenovo", 1399.99, "Business laptop with legendary keyboard", "https://m.media-amazon.com/images/I/41AW34vZZdL._SX300_SY300_QL70_FMwebp_.jpg", 4.6, 18),
        ("ASUS ROG Strix G15", "laptops", "ASUS", 1599.99, "Gaming laptop with RTX 3060 graphics", "https://m.media-amazon.com/images/I/41xCssXRQ9L._SX300_SY300_QL70_FMwebp_.jpg", 4.3, 12),
        ("Acer Predator Helios 300", "laptops", "Acer", 1199.99, "High-performance gaming laptop", "https://m.media-amazon.com/images/I/41JfJYBLAFL._SX300_SY300_QL70_FMwebp_.jpg", 4.2, 10),
        ("Microsoft Surface Laptop 4", "laptops", "Microsoft", 999.99, "Sleek laptop with touchscreen display", "https://m.media-amazon.com/images/I/414ilIo3tAL._SX300_SY300_QL70_FMwebp_.jpg", 4.4, 22),
        ("Razer Blade 15", "laptops", "Razer", 2299.99, "Premium gaming laptop with RGB keyboard", "https://m.media-amazon.com/images/I/71RXOnGBA5L._SL1500_.jpg", 4.7, 8),
        ("Dell Inspiron 15 3000", "laptops", "Dell", 599.99, "Budget-friendly laptop for everyday use", "https://m.media-amazon.com/images/I/41FHm3D6ziL._SX300_SY300_QL70_FMwebp_.jpg", 3.8, 35),
        ("HP Pavilion Gaming", "laptops", "HP", 899.99, "Entry-level gaming laptop with GTX 1650", "https://m.media-amazon.com/images/I/71hC42cKbsL._SX569_.jpg", 4.0, 28),
        
        # Smartphones
        ("iPhone 14 Pro", "smartphones", "Apple", 999.99, "Latest iPhone with Pro camera system", "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6487/6487403_sd.jpg", 4.7, 50),
        ("Samsung Galaxy S23", "smartphones", "Samsung", 799.99, "Flagship Android phone with amazing cameras", "https://m.media-amazon.com/images/I/31Zb0680uoL._SX300_SY300_QL70_FMwebp_.jpg", 4.5, 45),
        ("Google Pixel 7", "smartphones", "Google", 599.99, "Pure Android experience with computational photography", "https://m.media-amazon.com/images/I/518Ds5LHL5L._SX300_SY300_QL70_FMwebp_.jpg", 4.4, 30),
        ("OnePlus 11", "smartphones", "OnePlus", 699.99, "Fast charging flagship with clean software", "https://m.media-amazon.com/images/I/61amb0CfMGL._SL1500_.jpg", 4.3, 25),
        ("Xiaomi Mi 13", "smartphones", "Xiaomi", 549.99, "High-performance phone at great value", "https://m.media-amazon.com/images/I/41eB+jXzGsL._SY300_SX300_.jpg", 4.2, 40),
        ("iPhone 13", "smartphones", "Apple", 729.99, "Previous generation iPhone still going strong", "https://m.media-amazon.com/images/I/3150P3KQFlL._SX300_SY300_QL70_FMwebp_.jpg", 4.6, 60),
        ("Samsung Galaxy A54", "smartphones", "Samsung", 449.99, "Mid-range phone with premium features", "https://m.media-amazon.com/images/I/31imefykVML._SY300_SX300_QL70_FMwebp_.jpg", 4.1, 55),
        ("Google Pixel 6a", "smartphones", "Google", 349.99, "Budget Pixel with flagship camera", "https://m.media-amazon.com/images/I/71s6RRFzE4L._SY450_.jpg", 4.3, 35),
        ("Nothing Phone 2", "smartphones", "Nothing", 599.99, "Unique transparent design with glyph interface", "https://m.media-amazon.com/images/I/51vLph5k7UL._SX300_SY300_QL70_FMwebp_.jpg", 4.0, 20),
        ("Motorola Edge 30", "smartphones", "Motorola", 499.99, "Sleek design with near-stock Android", "https://m.media-amazon.com/images/I/41R+4ohZ77L._SY300_SX300_.jpg", 3.9, 25),
        
        # Tablets
        ("iPad Pro 12.9", "tablets", "Apple", 1099.99, "Professional tablet with M2 chip", "https://m.media-amazon.com/images/I/41XOG2QviwL._SY445_SX342_QL70_FMwebp_.jpg", 4.8, 20),
        ("iPad Air", "tablets", "Apple", 599.99, "Powerful and versatile iPad for everyone", "https://m.media-amazon.com/images/I/41ZKcMButQL._SX300_SY300_QL70_FMwebp_.jpg", 4.6, 30),
        ("Samsung Galaxy Tab S8", "tablets", "Samsung", 699.99, "Android tablet with S Pen included", "https://m.media-amazon.com/images/I/31JuXYPsUCL._SX300_SY300_QL70_FMwebp_.jpg", 4.4, 25),
        ("Microsoft Surface Pro 9", "tablets", "Microsoft", 999.99, "2-in-1 tablet that replaces your laptop", "https://m.media-amazon.com/images/I/41TqUcJzxjL._SY300_SX300_QL70_FMwebp_.jpg", 4.3, 15),
        ("Amazon Fire HD 10", "tablets", "Amazon", 149.99, "Budget tablet for entertainment", "https://m.media-amazon.com/images/I/71oGhSbkKuL._SX569_.jpg", 3.8, 50),
        ("Lenovo Tab P11", "tablets", "Lenovo", 249.99, "Affordable Android tablet with good performance", "https://m.media-amazon.com/images/I/41M5+7y0i0L._SY300_SX300_.jpg", 4.0, 35),
        
        # Accessories
        ("AirPods Pro 2", "accessories", "Apple", 249.99, "Premium wireless earbuds with ANC", "https://m.media-amazon.com/images/I/31GYay3meDL._SX300_SY300_QL70_FMwebp_.jpg", 4.7, 100),
        ("Sony WH-1000XM5", "accessories", "Sony", 399.99, "Industry-leading noise canceling headphones", "https://m.media-amazon.com/images/I/31vOBg8cPaL._SX300_SY300_QL70_FMwebp_.jpg", 4.8, 45),
        ("Bose QuietComfort 45", "accessories", "Bose", 329.99, "Comfortable wireless headphones", "https://m.media-amazon.com/images/I/31+fg95OcqL._SY300_SX300_.jpg", 4.5, 40),
        ("JBL Flip 6", "accessories", "JBL", 129.99, "Portable Bluetooth speaker", "https://m.media-amazon.com/images/I/41QBa9gm++L._SY300_SX300_.jpg", 4.3, 60),
        ("Anker PowerCore 10000", "accessories", "Anker", 29.99, "Compact portable charger", "https://assets2.cbsnewsstatic.com/hub/i/r/2025/06/13/d22ae165-51c8-4c25-ad25-c89264bfb7ab/thumbnail/620x461/6b0da41db4691edef0738e034f115b7d/screenshot-2025-06-13-at-11-42-00-am.png?v=64f55bb7ef9382fe7916b907da543f1f#", 4.4, 80),
        ("Logitech MX Master 3", "accessories", "Logitech", 99.99, "Advanced wireless mouse for productivity", "https://m.media-amazon.com/images/I/31kOPvuYXLL._SX300_SY300_QL70_FMwebp_.jpg", 4.6, 55),
        ("Keychron K2", "accessories", "Keychron", 79.99, "Wireless mechanical keyboard", "https://m.media-amazon.com/images/I/31UE4dNtc2L._SX300_SY300_QL70_FMwebp_.jpg", 4.2, 30),
        ("Samsung 980 PRO SSD", "accessories", "Samsung", 149.99, "High-speed NVMe SSD 1TB", "https://m.media-amazon.com/images/I/21HXE05iS4L._SY300_SX300_QL70_FMwebp_.jpg", 4.7, 25),
        ("Belkin 3-in-1 Wireless Charger", "accessories", "Belkin", 149.99, "Charge iPhone, AirPods, and Apple Watch", "https://m.media-amazon.com/images/I/316JxOJoIXL._SX300_SY300_QL70_FMwebp_.jpg", 4.1, 35),
        ("Apple Magic Keyboard", "accessories", "Apple", 179.99, "Wireless keyboard for iPad Pro", "https://m.media-amazon.com/images/I/71BkHuHTS-L._SX679_.jpg", 4.4, 20),
        
        # Smart Devices
        ("Apple Watch Series 8", "smart_devices", "Apple", 399.99, "Advanced health and fitness tracking", "https://m.media-amazon.com/images/I/41of44hRBqL._SX300_SY300_QL70_FMwebp_.jpg", 4.6, 40),
        ("Samsung Galaxy Watch 5", "smart_devices", "Samsung", 279.99, "Comprehensive smartwatch for Android", "https://m.media-amazon.com/images/I/21JgtoI8+4L._SX300_SY300_.jpg", 4.3, 35),
        ("Amazon Echo Dot", "smart_devices", "Amazon", 49.99, "Compact smart speaker with Alexa", "https://m.media-amazon.com/images/I/5108OEjU5+L._SY300_SX300_.jpg", 4.2, 100),
        ("Google Nest Hub", "smart_devices", "Google", 99.99, "Smart display with Google Assistant", "https://m.media-amazon.com/images/I/61AvI9FrkQL._SX425_.jpg", 4.1, 50),
        ("Ring Video Doorbell", "smart_devices", "Ring", 199.99, "Smart doorbell with HD video", "https://m.media-amazon.com/images/I/51dgQ0F4dnL._SY450_.jpg", 4.0, 30),
        ("Philips Hue Starter Kit", "smart_devices", "Philips", 179.99, "Smart lighting system", "https://m.media-amazon.com/images/I/31plcsCT0yL._SX300_SY300_QL70_FMwebp_.jpg", 4.4, 25),
        ("Nest Thermostat", "smart_devices", "Google", 129.99, "Smart thermostat for energy savings", "https://m.media-amazon.com/images/I/61A+x8c9VeL._SX569_.jpg", 4.3, 20),
        ("Fitbit Versa 3", "smart_devices", "Fitbit", 199.99, "Health and fitness smartwatch", "https://m.media-amazon.com/images/I/31no9Y6TZdL._SX300_SY300_QL70_FMwebp_.jpg", 4.2, 45),
    ]
    
    cursor.executemany(
        'INSERT INTO products (name, category, brand, price, description, image_url, rating, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        products
    )
    
    conn.commit()
    conn.close()
    print("Database created successfully with mock data!")

if __name__ == '__main__':
    create_database()