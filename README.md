# ScoutIQ (Anti) — E-Commerce Intelligence Dashboard

A high-performance, premium e-commerce product scouting and intelligence dashboard built with Flask and Vanilla JavaScript.

## 🚀 Features
- **Product Scouting**: Real-time product analysis with custom "Scout Score."
- **Comparison Engine**: Visual side-by-side comparison of up to 3 products.
- **Smart Alerts**: Track price drops, trends, and stock levels.
- **Visual Analytics**: Custom-drawn canvas charts for activity, categories, and price trends.
- **User Management**: Secure email-based OTP verification and activity logging.
- **Admin Dashboard**: Live feed of user activities and system growth.

## 🛠️ Technology Stack
- **Backend**: Python 3.10+ / Flask / SQLite
- **Frontend**: Vanilla JS (ES6) / CSS3 (CSS Variables + Grid/Flex)
- **Security**: Werkzeug password hashing, session-based auth, and environment variable management.

## 📦 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**:
   Create a `.env` file in the root with the following:
   ```env
   FLASK_SECRET_KEY=your_secret_key
   SENDER_EMAIL=your_gmail@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000`.

## 📂 Project Structure
- `app.py`: Main Flask API and route handlers.
- `database.py`: Database schema and initial seed data.
- `app.js`: Core frontend logic and API interactions.
- `style.css`: Design system and layout styles.
- `migrations/`: Historical database update scripts.
- `*.html`: Modular frontend views (Index, Login, Register, Profile, Admin).

## 🔒 Security
- All sensitive keys are moved out of source code into `.env`.
- Admin API endpoints are protected with login requirements.
- Passwords are salted and hashed using PBKDF2.

---
*Created with care by [Rakesh Doddigarla]*
