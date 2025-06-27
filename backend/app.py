from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime  # ✅ Correct import for timestamp
from functools import wraps
import bcrypt
import json
from chatbot_logic import ChatbotLogic

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Database helper
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

# Auth token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return 'Welcome to the E-commerce Chatbot API'

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username or email already exists'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user_id):
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/verify-token', methods=['GET'])
@token_required
def verify_token(current_user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, email FROM users WHERE id = ?', (current_user_id,)).fetchone()
    conn.close()

    if user:
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    return jsonify({'message': 'User not found'}), 404

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()

    return jsonify([dict(product) for product in products])

@app.route('/api/products/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand', '')

    conn = get_db_connection()
    sql = 'SELECT * FROM products WHERE 1=1'
    params = []

    if query:
        sql += ' AND (name LIKE ? OR description LIKE ?)'
        params.extend([f'%{query}%', f'%{query}%'])

    if category:
        sql += ' AND category = ?'
        params.append(category)

    if min_price is not None:
        sql += ' AND price >= ?'
        params.append(min_price)

    if max_price is not None:
        sql += ' AND price <= ?'
        params.append(max_price)

    if brand:
        sql += ' AND brand = ?'
        params.append(brand)

    sql += ' ORDER BY rating DESC, name'
    products = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify([dict(product) for product in products])

@app.route('/api/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    conn = get_db_connection()
    products = conn.execute(
        'SELECT * FROM products WHERE category = ? ORDER BY rating DESC',
        (category,)
    ).fetchall()
    conn.close()

    return jsonify([dict(product) for product in products])

@app.route('/api/chat', methods=['POST'])
@token_required
def process_chat(current_user_id):
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'message': 'Message is required'}), 400

    chatbot = ChatbotLogic()
    response = chatbot.process_message(message)

    # Save chat with correct timestamp
    timestamp = datetime.datetime.utcnow().isoformat()
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO chat_history (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)',
        (current_user_id, message, json.dumps(response), timestamp)
    )
    conn.commit()
    conn.close()

    return jsonify(response)

@app.route('/api/chat-history', methods=['GET'])
@token_required
def get_chat_history(current_user_id):
    conn = get_db_connection()
    history = conn.execute(
        'SELECT message, response, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50',
        (current_user_id,)
    ).fetchall()
    conn.close()

    chat_history = []
    for record in history:
        chat_history.append({
            'message': record['message'],
            'response': json.loads(record['response']),
            'timestamp': record['timestamp']
        })

    return jsonify(chat_history)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
