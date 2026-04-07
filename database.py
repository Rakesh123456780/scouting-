"""
ScoutIQ — Database Setup & Seed Data (SQLite)
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")


def get_connection():
    """Return a new connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------- SCHEMA ----------
def create_tables(conn):
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        category    TEXT    NOT NULL,
        price       REAL    NOT NULL,
        original_price REAL,
        emoji       TEXT,
        rating      REAL    DEFAULT 0,
        reviews     INTEGER DEFAULT 0,
        score       INTEGER DEFAULT 0,
        tags        TEXT    DEFAULT '[]',   -- JSON array
        sales       INTEGER DEFAULT 0,
        margin      INTEGER DEFAULT 0,
        demand      TEXT    DEFAULT 'Medium',
        description TEXT,
        brand       TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL UNIQUE,
        icon  TEXT,
        count INTEGER DEFAULT 0,
        pct   INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS watchlist (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL UNIQUE,
        added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        product    TEXT    NOT NULL,
        type       TEXT    NOT NULL,
        type_name  TEXT,
        description TEXT,
        status     TEXT    DEFAULT 'active',
        icon       TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS geo_demand (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        flag   TEXT,
        name   TEXT NOT NULL,
        demand TEXT,
        pct    INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS brands (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        logo     TEXT,
        name     TEXT NOT NULL UNIQUE,
        products INTEGER DEFAULT 0,
        score    TEXT
    );

    CREATE TABLE IF NOT EXISTS insights (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        icon TEXT,
        text TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        email       TEXT    UNIQUE NOT NULL,
        password    TEXT    NOT NULL,
        phone_number TEXT,
        otp_code    TEXT,
        is_verified INTEGER DEFAULT 0,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS activity_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email  TEXT    NOT NULL,
        action      TEXT    NOT NULL,
        details     TEXT,
        timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()


# ---------- SEED DATA ----------
SEED_PRODUCTS = [
    (1, "Wireless Noise-Cancelling Headphones Pro", "Electronics", 10400.00, 15200.00, "🎧", 4.8, 2340, 94, '["hot","trending"]', 12400, 42, "Very High", "Premium ANC headphones with 40-hour battery life, adaptive EQ, and spatial audio. Market leader in the ₹8000-₹12000 segment with consistent 5-star reviews and low return rate.", "SoundMax"),
    (2, "LED Ring Light 18-inch Studio Kit", "Electronics", 3600.00, 6400.00, "💡", 4.6, 5678, 91, '["hot"]', 34500, 58, "Very High", "Professional ring light for content creators with 3 color modes, app control, and collapsible tripod stand. Trending with the creator economy boom.", "LitePro"),
    (3, "Bamboo Cutting Board Set (3-Pack)", "Home", 2800.00, 4000.00, "🍽️", 4.7, 1890, 87, '["new"]', 8900, 65, "High", "Eco-friendly bamboo cutting boards in 3 sizes with juice grooves and handles. Consistent seller in kitchen & dining, excellent margins for a low-cost product.", "EcoKitch"),
    (4, "Smart Posture Corrector Wearable", "Health", 3200.00, 4800.00, "🦴", 4.3, 876, 82, '["trending"]', 15600, 70, "High", "Bluetooth-enabled posture corrector that vibrates when you slouch. Integrates with a mobile app to track your progress over time.", "PostureTech"),
    (5, "Foldable Yoga Mat with Carry Strap", "Sports", 2300.00, 3600.00, "🧘", 4.5, 3210, 88, '["hot"]', 21000, 55, "Very High", "Non-slip foldable yoga mat made from eco-friendly materials. Perfect for travel and home workouts, trending due to the home fitness boom.", "FlexFit"),
    (6, "Portable Blender for Smoothies", "Home", 2900.00, 4400.00, "🥤", 4.4, 4567, 85, '["hot"]', 19800, 60, "High", "USB-C chargeable portable blender with 6 stainless steel blades. Excellent for commuters and fitness enthusiasts. Strong cross-sell potential.", "BlendGo"),
    (7, "Kids STEM Robot Building Kit", "Toys", 4000.00, 5600.00, "🤖", 4.9, 1234, 90, '["new","trending"]', 7800, 52, "High", "Educational robot kit for ages 8+ that teaches programming basics. Won multiple awards and has extremely positive reviews from parents and educators.", "BuildBrain"),
    (8, "Car Phone Mount Magnetic Wireless", "Automotive", 1800.00, 2800.00, "🚗", 4.6, 9876, 89, '["hot"]', 42000, 74, "Very High", "Magnetic wireless charging car mount compatible with all Qi-enabled phones. Extremely high volume seller with excellent review velocity.", "DriveCharge"),
    (9, "Mesh WiFi System (3-Pack)", "Electronics", 12800.00, 19200.00, "📡", 4.7, 3456, 86, '["trending"]', 5600, 38, "High", "Tri-band mesh WiFi covering up to 6,000 sq ft with parental controls and guest network. Growing market as WFH becomes permanent for many.", "NetSphere"),
    (10, "Resistance Band Set (11-Piece)", "Sports", 2000.00, 3200.00, "💪", 4.8, 7890, 92, '["hot"]', 38000, 72, "Very High", "Complete resistance band set with multiple tension levels, handles, ankle straps, and door anchor. Consistently one of the top-selling fitness products.", "IronEdge"),
    (11, "Electric Facial Gua Sha Massager", "Health", 4400.00, 7200.00, "✨", 4.5, 2340, 83, '["new","trending"]', 11200, 66, "High", "7-in-1 electric facial massager with LED light therapy and microcurrent technology. Viral on social media with a fast-growing niche audience.", "GlowTech"),
    (12, "Insulated Tumbler 40oz Stanley-Style", "Home", 2600.00, 4000.00, "☕", 4.9, 15670, 96, '["hot","trending"]', 67000, 62, "Very High", "Triple-insulated tumbler keeps drinks cold 24h/hot 12h. Exploding in popularity driven by social media trends. Multiple color variations available.", "ChillKeep"),
    (13, "Laptop Stand Adjustable Aluminum", "Electronics", 3600.00, 5200.00, "💻", 4.7, 8901, 88, '["trending"]', 23000, 55, "High", "Portable aluminum laptop stand with 6 height adjustments and foldable design. Evergreen product with steady sales across all seasons.", "DeskPro"),
    (14, "Seed Germination Kit (72 pods)", "Home", 2400.00, 3600.00, "🌱", 4.6, 3456, 81, '["new"]', 9400, 68, "Medium", "Complete seed starter kit for indoor gardening. Trending with the urban gardening movement and highly seasonal (spring peaks).", "GroWell"),
    (15, "Wireless Earbuds TWS Pro", "Electronics", 4800.00, 8000.00, "🎵", 4.6, 12340, 89, '["hot"]', 45000, 58, "Very High", "True wireless earbuds with ANC, 30hr total battery, IPX5 water resistance. Competitive category but strong price-to-value positioning.", "SoundMax"),
    (16, "Foam Roller Deep Tissue Massage", "Sports", 1600.00, 2800.00, "🏋️", 4.7, 5678, 85, '["deal"]', 28000, 70, "High", "High-density EVA foam roller for post-workout recovery. Great margins and consistent demand year-round with easy bundling potential.", "FlexFit"),
    (17, "Silk Pillowcase Set (2-Pack)", "Health", 3200.00, 4800.00, "🛏️", 4.8, 4567, 87, '["trending"]', 17600, 64, "High", "100% mulberry silk pillowcases in queen and king size. Beauty-adjacent product with strong social proof and repeat purchase potential.", "LuxSilk"),
    (18, "Digital Food Scale Kitchen Smart", "Home", 1400.00, 2400.00, "⚖️", 4.9, 23456, 93, '["hot","deal"]', 78000, 66, "Very High", "Ultra-precise 0.1g food scale with tare function and built-in timer. Massive volume seller in the kitchen category, dominated by repeat buyers.", "MeasurePro"),
    (19, "Camping Headlamp Rechargeable 1200LM", "Sports", 2800.00, 4400.00, "🔦", 4.8, 6789, 86, '["new"]', 14300, 58, "High", "USB-C rechargeable headlamp with motion sensor, red light mode, and 20h runtime. Growing demand from both outdoor and emergency preparedness markets.", "LitePath"),
    (20, "Macro Photography Lens Kit (5-in-1)", "Electronics", 2400.00, 4000.00, "📷", 4.4, 2345, 79, '["new"]', 6700, 72, "Medium", "Universal clip-on lens kit for smartphones. Photography hobby boom driving increased interest, especially among Gen Z creators.", "LensMaster"),
    (21, "Aromatherapy Diffuser Oil Set", "Health", 3400.00, 5200.00, "🕯️", 4.7, 3456, 84, '["trending"]', 20100, 75, "High", "Bundle of 6 essential oils with a BPA-free ultrasonic diffuser. Wellness trend driving strong conversions. Perfect gifting product.", "ZenAroma"),
    (22, "Toddler Art Supplies Mega Kit", "Toys", 3100.00, 4800.00, "🎨", 4.9, 8901, 91, '["hot"]', 24500, 60, "High", "100-piece washable art kit for toddlers including crayons, markers, stamps, and watercolors. Top gifting product year-round with spike in holiday season.", "TinkerKids"),
    (23, "Pet Hair Remover Roller Pro", "Home", 1200.00, 2000.00, "🐾", 4.8, 34567, 95, '["hot","trending"]', 89000, 80, "Very High", "Self-cleaning pet hair remover with upgradeable base. Evergreen product for pet owners with exceptional margins and near-zero returns.", "PetPro"),
    (24, "Stainless Steel Water Bottle 32oz", "Sports", 2100.00, 3200.00, "🍶", 4.7, 19876, 90, '["hot"]', 56000, 62, "Very High", "Triple-wall insulated bottle with leak-proof lid. Powerhouse seller and gateway product with strong brand loyalty and bundling potential.", "HydroForce"),
    (25, "Smart LED Strip Lights 32ft RGB", "Electronics", 2000.00, 3200.00, "🌈", 4.5, 18900, 91, '["hot","trending"]', 52000, 68, "Very High", "WiFi-enabled LED strip lights with 16M colors, music sync, and voice control via Alexa/Google. Massive TikTok-driven demand among Gen Z room decor enthusiasts.", "LitePro"),
    (26, "Ergonomic Vertical Mouse Wireless", "Electronics", 2800.00, 4400.00, "🖱️", 4.6, 6780, 84, '["trending"]', 18500, 60, "High", "Ergonomic vertical design reduces wrist strain. 6 programmable buttons, 3 DPI levels, USB-C rechargeable. Growing with the WFH and RSI-awareness trends.", "DeskPro"),
    (27, "Air Fryer 5.8 Quart Digital", "Home", 5600.00, 8800.00, "🍟", 4.8, 24500, 93, '["hot","deal"]', 61000, 45, "Very High", "Digital touchscreen air fryer with 8 presets, rapid air circulation, and dishwasher-safe basket. Kitchen must-have with exceptional review velocity.", "HomeChef"),
    (28, "Massage Gun Deep Tissue Percussive", "Health", 7200.00, 12000.00, "💆", 4.7, 8900, 88, '["hot"]', 27000, 52, "Very High", "30-speed percussion massager with 6 interchangeable heads and ultra-quiet brushless motor. Recovery tool of choice for athletes and desk workers alike.", "FlexFit"),
    (29, "Wireless Charging Pad 3-in-1", "Electronics", 3100.00, 4800.00, "🔋", 4.5, 11200, 86, '["trending"]', 31000, 62, "High", "Charges phone, watch, and earbuds simultaneously. Qi-certified 15W fast charging with LED indicator and anti-slip pad. Universal compatibility.", "DriveCharge"),
    (30, "Smart Plug WiFi Mini (4-Pack)", "Home", 2400.00, 3600.00, "🔌", 4.7, 31200, 92, '["hot"]', 74000, 70, "Very High", "Voice-controlled smart plugs compatible with Alexa, Google Home, and IFTTT. Timer scheduling and energy monitoring included. Highly bundleable.", "NetSphere"),
    (31, "Jump Rope Speed Weighted Digital", "Sports", 1600.00, 2600.00, "⏱️", 4.6, 5400, 83, '["new","trending"]', 16800, 72, "High", "Digital counter jump rope with adjustable weighted handles and ball bearing system. Trending in home fitness and boxing workout communities.", "IronEdge"),
    (32, "Vitamin C Serum with Hyaluronic Acid", "Health", 1500.00, 2800.00, "🧴", 4.8, 42300, 95, '["hot","trending"]', 112000, 82, "Very High", "Clinical-grade 20% vitamin C serum with hyaluronic acid and vitamin E. Skincare staple with massive repeat purchase rate and social media presence.", "GlowTech"),
    (33, "Dash Cam 4K Front and Rear", "Automotive", 6400.00, 10400.00, "📹", 4.6, 7800, 87, '["trending"]', 19500, 48, "High", "Dual-channel 4K dash cam with night vision, GPS, parking mode, and 170-degree wide angle. Insurance demand and safety awareness driving steady growth.", "DriveCharge"),
    (34, "Electric Milk Frother Handheld", "Home", 1200.00, 2000.00, "☕", 4.7, 28900, 90, '["hot","deal"]', 93000, 78, "Very High", "USB rechargeable milk frother with 3 speed settings and stainless steel whisk. Impulse buy with massive volume — top performer in kitchen gadgets.", "HomeChef"),
    (35, "Kids Walkie Talkies Long Range (2-Pack)", "Toys", 2200.00, 3400.00, "📻", 4.5, 6700, 84, '["new"]', 14200, 64, "High", "3-mile range walkie talkies for kids with flashlight, VOX function, and 22 channels. Outdoor play trending post-pandemic with strong gifting appeal.", "TinkerKids"),
    (36, "Heated Car Seat Cushion Universal", "Automotive", 2800.00, 4400.00, "🪑", 4.4, 4300, 80, '["trending"]', 11800, 58, "Medium", "12V heated seat cushion with 3 temperature settings and auto shut-off. Seasonal but highly profitable — strong Q4 and winter demand in northern markets.", "DriveCharge"),
    (37, "Mechanical Keyboard RGB Wireless", "Electronics", 4400.00, 7200.00, "⌨️", 4.7, 9800, 89, '["hot","trending"]', 26000, 50, "Very High", "Hot-swappable mechanical keyboard with Bluetooth 5.0, 2.4GHz, and USB-C. Custom RGB backlighting per key. Enthusiast and gaming communities driving demand.", "DeskPro"),
    (38, "Collagen Peptides Powder Unflavored", "Health", 2400.00, 3600.00, "💊", 4.8, 19800, 91, '["hot"]', 48000, 60, "Very High", "Grass-fed hydrolyzed collagen peptides with 20g protein per serving. Wellness supplement category leader with strong subscription and repeat purchase metrics.", "ZenAroma"),
    (39, "Solar Powered Garden Lights (12-Pack)", "Home", 2600.00, 4000.00, "🌞", 4.5, 14500, 86, '["new","deal"]', 37000, 68, "High", "Color-changing solar path lights with stainless steel stakes. Zero operating cost product with strong curb appeal — seasonal spike in spring and summer.", "EcoKitch"),
    (40, "Baby Monitor WiFi 2K Pan-Tilt", "Electronics", 4000.00, 6400.00, "👶", 4.6, 8900, 87, '["trending"]', 22000, 52, "High", "2K HD baby monitor with two-way audio, night vision, motion detection, and lullaby player. App-controlled with encrypted cloud and SD card storage.", "NetSphere"),
    (41, "Pull-Up Bar Doorway No-Screw", "Sports", 2600.00, 4000.00, "🏋️", 4.7, 11200, 88, '["hot"]', 29000, 64, "Very High", "Heavy-duty doorway pull-up bar supporting up to 440 lbs with foam grips and no drilling required. Calisthenics trend fueling consistent sales growth.", "IronEdge"),
    (42, "Board Game Strategy Family Night", "Toys", 2800.00, 4000.00, "🎲", 4.9, 5600, 85, '["new","trending"]', 13500, 55, "High", "Award-winning strategy board game for ages 10+ with 2-6 player modes. Board game renaissance driven by family time trends and content creator reviews.", "BuildBrain"),
    (43, "Car Vacuum Cleaner Handheld 12V", "Automotive", 2400.00, 3600.00, "🧹", 4.5, 15600, 86, '["hot"]', 38000, 66, "Very High", "8000Pa suction handheld car vacuum with HEPA filter and LED light. Comes with 4 attachments for crevice, upholstery, and wet/dry cleaning.", "DriveCharge"),
    (44, "Portable Projector Mini 1080p WiFi", "Electronics", 7200.00, 12000.00, "🎬", 4.4, 4500, 82, '["trending"]', 9800, 46, "High", "Pocket-size 1080p projector with WiFi mirroring, built-in speakers, and 120-inch throw. Outdoor movie night trend among millennials and families.", "LitePro"),
]

SEED_CATEGORIES = [
    ("Electronics", "💻", 287, 85),
    ("Health & Beauty", "✨", 234, 78),
    ("Home & Garden", "🏡", 198, 70),
    ("Sports & Fitness", "🏋️", 176, 65),
    ("Toys & Games", "🎮", 143, 55),
    ("Automotive", "🚗", 112, 45),
]

SEED_GEO = [
    ("🇺🇸", "United States", "Very High", 90),
    ("🇬🇧", "United Kingdom", "High", 72),
    ("🇩🇪", "Germany", "High", 68),
    ("🇦🇺", "Australia", "Medium", 54),
    ("🇨🇦", "Canada", "High", 70),
    ("🇫🇷", "France", "Medium", 50),
    ("🇧🇷", "Brazil", "Growing", 43),
    ("🇮🇳", "India", "Growing", 87),
]

SEED_BRANDS = [
    ("🎧", "SoundMax", 24, "9.4"),
    ("💪", "FlexFit", 18, "9.1"),
    ("🏠", "HomeEssentials", 31, "8.8"),
    ("🌿", "EcoLife", 15, "8.6"),
    ("🔧", "TechPro", 22, "8.4"),
]

SEED_INSIGHTS = [
    ("📈", "<strong>Hydration products</strong> are up +34% this month driven by summer prep and fitness trends."),
    ("🎯", "<strong>Pet accessories</strong> show the highest margin potential in the Home category — averaging 76% gross margin."),
    ("⚡", "<strong>USB-C compatible</strong> products are consistently outperforming older connector types by 2.3x sales velocity."),
    ("🌟", "Products with <strong>4.8+ star ratings</strong> see 58% lower return rates and 31% higher repeat purchase rates."),
    ("🔍", "<strong>Wellness & self-care</strong> searches increased 127% YoY — consider expanding in aromatherapy and skincare."),
]

SEED_ALERTS = [
    ("Wireless Noise-Cancelling Headphones Pro", "price-drop", "Price Drop", "Alert when price drops below ₹8000.00", "active", "📉"),
    ("Insulated Tumbler 40oz", "trend", "Trend Alert", "Alert when trending score exceeds 95", "triggered", "🔥"),
    ("Pet Hair Remover Roller Pro", "stock", "Stock Alert", "Alert when stock drops below 500 units", "triggered", "📦"),
    ("Smart Posture Corrector", "price-rise", "Price Rise", "Alert when competition raises prices above ₹4500", "paused", "📈"),
    ("Kids STEM Robot Kit", "trend", "Trend Alert", "Alert when trending score exceeds 95", "active", "🔥"),
]


def seed_data(conn):
    """Insert seed data if tables are empty."""
    cur = conn.cursor()

    # Products
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        cur.executemany(
            """INSERT INTO products (id, name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            SEED_PRODUCTS
        )

    # Categories
    if cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO categories (name, icon, count, pct) VALUES (?, ?, ?, ?)",
            SEED_CATEGORIES
        )

    # Geo demand
    if cur.execute("SELECT COUNT(*) FROM geo_demand").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO geo_demand (flag, name, demand, pct) VALUES (?, ?, ?, ?)",
            SEED_GEO
        )

    # Brands
    if cur.execute("SELECT COUNT(*) FROM brands").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO brands (logo, name, products, score) VALUES (?, ?, ?, ?)",
            SEED_BRANDS
        )

    # Insights
    if cur.execute("SELECT COUNT(*) FROM insights").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO insights (icon, text) VALUES (?, ?)",
            SEED_INSIGHTS
        )

    # Alerts
    if cur.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO alerts (product, type, type_name, description, status, icon) VALUES (?, ?, ?, ?, ?, ?)",
            SEED_ALERTS
        )

    conn.commit()

    # Bulk Product Generation to reach ~2847 products
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] < 2000:
        import random
        # Base data for generation
        adjectives = ["Smart", "Portable", "Wireless", "Magnetic", "Ergonomic", "Advanced", "Compact", "Heavy-Duty", "Electric", "Digital", "Interactive", "Foldable", "Premium", "Ultra-Slim", "Rechargeable"]
        nouns = {
            "Electronics": [("Power Bank 10,000mAh", "🔋"), ("Noise-Cancelling Earbuds", "🎧"), ("Bluetooth Speaker", "🔊"), ("Tablet Stand", "📱"), ("VR Headset Tracker", "🥽"), ("Drone with Camera", "🚁"), ("USB-C Hub", "🔌")],
            "Health & Beauty": [("Posture Mat", "🧘"), ("Light Therapy Lamp", "💡"), ("Sleep Mask", "😴"), ("Foot Spa", "🦶"), ("Acupressure Mat", "🧘"), ("Facial Massager", "✨")],
            "Home & Garden": [("Coffee Maker", "☕"), ("Air Purifier", "🌬️"), ("Smart Lock", "🔒"), ("Ceramic Knife Set", "🔪"), ("Bed Sheets Set", "🛏️"), ("Plush Throw Blanket", "🛋️")],
            "Sports & Fitness": [("Dumbbell Set", "🏋️"), ("Treadmill Mat", "🏃"), ("Sleeping Bag", "🎒"), ("Resistance Bands", "💪"), ("Yoga Block", "🧘")],
            "Toys & Games": [("Action Figure", "🦸"), ("Building Blocks", "🧱"), ("Remote Control Car", "🏎️"), ("Dollhouse", "🏠"), ("Water Gun", "🔫"), ("Magic Kit", "🎩")],
            "Automotive": [("OBD2 Scanner", "💻"), ("Microfiber Towels", "🧽"), ("Jump Starter Power Bank", "⚡"), ("Car Cover", "🚗"), ("Scratch Repair Kit", "🛠️"), ("Steering Wheel Cover", "🏎️")]
        }
        brands = [b[1] for b in SEED_BRANDS] + ["TechPro", "HomeChef", "FlexFit", "LuxSilk", "ZenAroma", "DriveCharge", "NetSphere", "BuildBrain", "PetPro", "IronEdge", "GlowTech", "LitePro", "LensMaster", "TinkerKids", "HydroForce", "EcoKitch", "MeasurePro", "ChillKeep", "BlendGo", "LitePath", "PostureTech", "SoundMax"]
        tags = ['["hot"]', '["new"]', '["trending"]', '["deal"]', '["hot","trending"]', '["new","trending"]', '["hot","deal"]', '["trending","deal"]', '["hot","new"]', '[]']
        demands = ["Low", "Medium", "High", "Very High", "Growing"]

        bulk_products = []
        for i in range(2753):
            category = random.choice(list(nouns.keys()))
            noun_pair = random.choice(nouns[category])
            name = f"{random.choice(adjectives)} {noun_pair[0]}"
            emoji = noun_pair[1]
            price = float(random.randint(499, 12999))
            original_price = float(price * random.uniform(1.1, 1.8))
            rating = float(f"{random.uniform(3.5, 5.0):.1f}")
            reviews = random.randint(50, 20000)
            score = random.randint(30, 99)
            product_tags = random.choice(tags)
            sales = random.randint(100, 99000)
            margin = random.randint(20, 85)
            demand = random.choice(demands)
            brand = random.choice(brands)
            desc = f"High quality {name.lower()} perfect for your needs. Excellent value and highly rated by customers."
            
            bulk_products.append((name, category, price, original_price, emoji, rating, reviews, score, product_tags, sales, margin, demand, desc, brand))

        cur.executemany(
            """INSERT INTO products (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            bulk_products
        )
        conn.commit()


def init_db():
    """Create tables and seed initial data."""
    conn = get_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print(f"[OK] Database initialised at {DB_PATH}")


if __name__ == "__main__":
    init_db()
