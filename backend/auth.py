import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
import sqlite3

class AuthManager:
    def __init__(self, db_path='ecommerce.db'):
        self.db_path = db_path
        self.secret_key = 'your-secret-key-change-in-production'
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def check_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def generate_token(self, user_id, username):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, username, email, password):
        """Register new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return None, "User already exists"
            
            # Hash password and create user
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Generate token
            token = self.generate_token(user_id, username)
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'token': token
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return None, "User not found"
            
            user_id, username, email, password_hash = user
            
            if not self.check_password(password, password_hash):
                return None, "Invalid password"
            
            # Generate token
            token = self.generate_token(user_id, username)
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'token': token
            }, None
            
        except Exception as e:
            return None, str(e)

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, jsonify
        
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            auth_manager = AuthManager()
            payload = auth_manager.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user info to request context
            request.current_user = payload
            
        except Exception as e:
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated