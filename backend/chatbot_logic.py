import sqlite3
import re
import random

class ChatbotLogic:
    def __init__(self):
        self.category_keywords = {
            'laptops': ['laptop', 'notebook', 'computer', 'pc', 'macbook', 'thinkpad'],
            'smartphones': ['phone', 'smartphone', 'mobile', 'iphone', 'android', 'cell'],
            'tablets': ['tablet', 'ipad', 'tab'],
            'accessories': ['headphones', 'earbuds', 'speaker', 'charger', 'mouse', 'keyboard', 'case'],
            'smart_devices': ['watch', 'smartwatch', 'echo', 'nest', 'smart', 'alexa', 'google']
        }
        
        self.brand_keywords = {
            'apple': ['apple', 'iphone', 'ipad', 'macbook', 'airpods'],
            'samsung': ['samsung', 'galaxy'],
            'google': ['google', 'pixel', 'nest'],
            'sony': ['sony'],
            'dell': ['dell', 'xps'],
            'hp': ['hp', 'hewlett'],
            'lenovo': ['lenovo', 'thinkpad'],
            'microsoft': ['microsoft', 'surface'],
            'asus': ['asus', 'rog'],
            'acer': ['acer', 'predator']
        }
        
        self.price_patterns = [
            r'under\s*\$?(\d+)',
            r'below\s*\$?(\d+)',
            r'less\s*than\s*\$?(\d+)',
            r'cheaper\s*than\s*\$?(\d+)',
            r'\$?(\d+)\s*-\s*\$?(\d+)',
            r'between\s*\$?(\d+)\s*and\s*\$?(\d+)',
            r'around\s*\$?(\d+)',
            r'about\s*\$?(\d+)'
        ]
    
    def get_db_connection(self):
        conn = sqlite3.connect('ecommerce.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def extract_category(self, message):
        message_lower = message.lower()
        words = re.findall(r'\b\w+\b', message_lower)
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in words:
                    return category
        return None

    
    def extract_brand(self, message):
        message_lower = message.lower()
        for brand, keywords in self.brand_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return brand
        return None
    
    def extract_price_range(self, message):
        for pattern in self.price_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:  # Single price (under, below, etc.)
                    if 'under' in pattern or 'below' in pattern or 'less' in pattern or 'cheaper' in pattern:
                        return (0, int(match.group(1)))
                    else:  # around, about
                        price = int(match.group(1))
                        return (price - 200, price + 200)
                elif len(match.groups()) == 2:  # Price range
                    return (int(match.group(1)), int(match.group(2)))
        return None
    
    def extract_keywords(self, message):
        # Remove common words and extract meaningful keywords
        stop_words = {'i', 'need', 'want', 'looking', 'for', 'show', 'me', 'find', 'get', 'buy', 'a', 'an', 'the', 'is', 'are', 'with', 'good', 'best'}
        words = re.findall(r'\b\w+\b', message.lower())
        return [word for word in words if word not in stop_words and len(word) > 2]
        print("\n[DEBUG] Message:", message)
        print("Extracted:")
        print("  Category:", category)
        print("  Brand:", brand)
        print("  Price Range:", price_range)
        print("  Keywords:", keywords)

    
    def search_products(self, category=None, brand=None, price_range=None, keywords=None, limit=10):
        conn = self.get_db_connection()
        
        sql = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if brand:
            sql += " AND LOWER(brand) = ?"
            params.append(brand.lower())
        
        if price_range:
            min_price, max_price = price_range
            sql += " AND price BETWEEN ? AND ?"
            params.extend([min_price, max_price])
        
        # Filter out useless or redundant keywords
        # Only apply keyword filter if it's useful
        if keywords and not (len(keywords) == 1 and category):
            useful_keywords = [
                kw for kw in keywords
                if kw != (category or '')
                and not kw.isdigit()
                and kw not in ['under', 'below', 'than', 'between', 'around', 'less', 'cheaper']
            ]

            
            keyword_conditions = []
            for keyword in useful_keywords:
                keyword_conditions.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ?)")
                params.extend([f'%{keyword}%', f'%{keyword}%'])
            
            if keyword_conditions:
                sql += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        sql += " ORDER BY rating DESC, price ASC LIMIT ?"
        params.append(limit)
        
        print("\n[DEBUG] SQL Query:", sql)
        print("[DEBUG] Params:", params)
        
        products = conn.execute(sql, params).fetchall()
        conn.close()
        
        return [dict(product) for product in products]

    
    def generate_greeting(self):
        greetings = [
            "Hello! I'm your shopping assistant. How can I help you find the perfect electronics today?",
            "Hi there! Looking for some great electronics? I'm here to help!",
            "Welcome! I can help you find laptops, smartphones, tablets, and more. What are you looking for?",
            "Hey! Ready to find some amazing electronics? What can I help you with?"
        ]
        return random.choice(greetings)
    
    def generate_product_response(self, products, query_info):
        if not products:
            return {
                'type': 'text',
                'message': "I couldn't find any products matching your criteria. Try adjusting your search or ask me about laptops, smartphones, tablets, or accessories!",
                'products': []
            }
        
        category = query_info.get('category', '')
        brand = query_info.get('brand', '')
        price_range = query_info.get('price_range', None)
        
        # Generate contextual message
        if len(products) == 1:
            message = f"I found the perfect {category or 'product'} for you!"
        else:
            message = f"Great! I found {len(products)} {category or 'products'} that match your criteria."
        
        if brand:
            message += f" All from {brand.title()}."
        if price_range:
            min_p, max_p = price_range
            message += f" Within your budget of ${min_p}-${max_p}."
        
        return {
            'type': 'products',
            'message': message,
            'products': products[:10]  # Limit to 5 products for better UX
        }
    
    def handle_greeting(self, message):
        greetings = ['hello', 'hi', 'hey', 'start', 'help']
        if any(greeting in message.lower() for greeting in greetings):
            return True
        return False
    
    def handle_filter_request(self, message):
        filters = {}
        message_lower = message.lower()
        
        if 'filter' in message_lower or 'sort' in message_lower:
            if 'price' in message_lower:
                if 'low' in message_lower or 'cheap' in message_lower:
                    filters['sort'] = 'price_asc'
                elif 'high' in message_lower or 'expensive' in message_lower:
                    filters['sort'] = 'price_desc'
            elif 'rating' in message_lower or 'best' in message_lower:
                filters['sort'] = 'rating_desc'
            return filters
        return None
    
    def process_message(self, message):
        message = message.strip()
        
        # Handle greetings
        if self.handle_greeting(message):
            return {
                'type': 'text',
                'message': self.generate_greeting(),
                'products': []
            }
        
        # Extract search parameters
        category = self.extract_category(message)
        brand = self.extract_brand(message)
        price_range = self.extract_price_range(message)
        keywords = self.extract_keywords(message)
        
        # Handle filter requests
        filters = self.handle_filter_request(message)
        if filters:
            # This would be handled by frontend for existing results
            return {
                'type': 'filter',
                'message': "I can help you filter products by price or rating. What would you like to filter?",
                'filters': filters
            }
        
        # Search for products
        products = self.search_products(
            category=category,
            brand=brand,
            price_range=price_range,
            keywords=keywords
        )
        
        query_info = {
            'category': category,
            'brand': brand,
            'price_range': price_range,
            'keywords': keywords
        }
        
        # Generate response
        response = self.generate_product_response(products, query_info)
        
        # Add helpful suggestions if no products found
        if not products:
            suggestions = []
            if category:
                suggestions.append(f"Try searching for {category} without specific brand requirements")
            else:
                suggestions.append("Try searching for 'laptops', 'phones', or 'tablets'")
            
            response['suggestions'] = suggestions
        
        return response

    