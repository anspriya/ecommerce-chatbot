# 🛒 E-commerce AI Chatbot Assistant

A full-stack e-commerce chatbot that helps users search for products like laptops, smartphones, tablets, and accessories using natural language. Built with **React**, **Flask**, and **SQLite**.

---

## ✨ Features

- 🔐 User authentication (Register/Login with JWT)
- 💬 AI chatbot that understands:
  - Product categories (e.g., "laptops", "headphones")
  - Brands (e.g., Apple, Samsung, Dell)
  - Price filters (e.g., "under $1000", "between $500 and $1000")
- 🛍 Product display cards with rating, price, and stock status
- 🧠 Intelligent query handling using keyword + category extraction
- ⏱ Chat history saved per user
- 🎨 Responsive React UI with Tailwind CSS (or custom styles)

---

## 🛠 Tech Stack

| Layer         | Technology          |
|---------------|---------------------|
| Frontend      | React.js, Tailwind CSS |
| Backend       | Flask, Flask-CORS   |
| Database      | SQLite              |
| Auth          | JWT (PyJWT), bcrypt |
| Chat Logic    | Custom NLP in Python |

---


---

## 🚀 Getting Started

### 🔧 Prerequisites

- Python 3.x
- Node.js + npm or yarn

---

### 💻 Backend Setup (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Initialize DB
python database_setup.py

# Start Flask server
python app.py

### 🌐 Frontend Setup (React)

cd frontend
npm install
npm start

Frontend runs on http://localhost:3000
Backend runs on http://localhost:5000


💡 Example Prompts

"Show me laptops under 1000"
"I need a gaming laptop"
"Headphones from Sony"
"iPhone models"
"Wireless accessories"

