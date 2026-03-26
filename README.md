# ScoutIQ — E-Commerce Intelligence Dashboard

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

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Rakesh123456780/scouting-.git
cd scouting-
```

### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Environment
Create a `.env` file in the root directory. You can copy the template below:
```env
FLASK_SECRET_KEY=any_random_string_here
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=your_app_password
```
> [!NOTE]
> If you don't configure `SENDER_EMAIL`, the app will still work! It will simply print the **OTP verification codes to your terminal** so you can log in/register during local testing.

### 6. Run the Application
```bash
python app.py
```
The app will automatically open in your browser at `http://127.0.0.1:5000`.

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
