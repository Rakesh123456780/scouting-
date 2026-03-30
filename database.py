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

    """)
    conn.commit()


# ---------- SEED DATA ----------
SEED_PRODUCTS = [
    (1, "Wireless Noise-Cancelling Headphones Pro", "Electronics", 129.99, 189.99, "🎧", 4.8, 2340, 94, '["hot","trending"]', 12400, 42, "Very High", "Premium ANC headphones with 40-hour battery life, adaptive EQ, and spatial audio. Market leader in the $100-$150 segment with consistent 5-star reviews and low return rate.", "SoundMax"),
    (2, "LED Ring Light 18-inch Studio Kit", "Electronics", 45.99, 79.99, "💡", 4.6, 5678, 91, '["hot"]', 34500, 58, "Very High", "Professional ring light for content creators with 3 color modes, app control, and collapsible tripod stand. Trending with the creator economy boom.", "LitePro"),
    (3, "Bamboo Cutting Board Set (3-Pack)", "Home", 34.99, 49.99, "🍽️", 4.7, 1890, 87, '["new"]', 8900, 65, "High", "Eco-friendly bamboo cutting boards in 3 sizes with juice grooves and handles. Consistent seller in kitchen & dining, excellent margins for a low-cost product.", "EcoKitch"),
    (4, "Smart Posture Corrector Wearable", "Health", 39.99, 59.99, "🦴", 4.3, 876, 82, '["trending"]', 15600, 70, "High", "Bluetooth-enabled posture corrector that vibrates when you slouch. Integrates with a mobile app to track your progress over time.", "PostureTech"),
    (5, "Foldable Yoga Mat with Carry Strap", "Sports", 28.99, 44.99, "🧘", 4.5, 3210, 88, '["hot"]', 21000, 55, "Very High", "Non-slip foldable yoga mat made from eco-friendly materials. Perfect for travel and home workouts, trending due to the home fitness boom.", "FlexFit"),
    (6, "Portable Blender for Smoothies", "Home", 36.99, 55.99, "🥤", 4.4, 4567, 85, '["hot"]', 19800, 60, "High", "USB-C chargeable portable blender with 6 stainless steel blades. Excellent for commuters and fitness enthusiasts. Strong cross-sell potential.", "BlendGo"),
    (7, "Kids STEM Robot Building Kit", "Toys", 49.99, 69.99, "🤖", 4.9, 1234, 90, '["new","trending"]', 7800, 52, "High", "Educational robot kit for ages 8+ that teaches programming basics. Won multiple awards and has extremely positive reviews from parents and educators.", "BuildBrain"),
    (8, "Car Phone Mount Magnetic Wireless", "Automotive", 22.99, 34.99, "🚗", 4.6, 9876, 89, '["hot"]', 42000, 74, "Very High", "Magnetic wireless charging car mount compatible with all Qi-enabled phones. Extremely high volume seller with excellent review velocity.", "DriveCharge"),
    (9, "Mesh WiFi System (3-Pack)", "Electronics", 159.99, 239.99, "📡", 4.7, 3456, 86, '["trending"]', 5600, 38, "High", "Tri-band mesh WiFi covering up to 6,000 sq ft with parental controls and guest network. Growing market as WFH becomes permanent for many.", "NetSphere"),
    (10, "Resistance Band Set (11-Piece)", "Sports", 24.99, 39.99, "💪", 4.8, 7890, 92, '["hot"]', 38000, 72, "Very High", "Complete resistance band set with multiple tension levels, handles, ankle straps, and door anchor. Consistently one of the top-selling fitness products.", "IronEdge"),
    (11, "Electric Facial Gua Sha Massager", "Health", 55.99, 89.99, "✨", 4.5, 2340, 83, '["new","trending"]', 11200, 66, "High", "7-in-1 electric facial massager with LED light therapy and microcurrent technology. Viral on social media with a fast-growing niche audience.", "GlowTech"),
    (12, "Insulated Tumbler 40oz Stanley-Style", "Home", 32.99, 49.99, "☕", 4.9, 15670, 96, '["hot","trending"]', 67000, 62, "Very High", "Triple-insulated tumbler keeps drinks cold 24h/hot 12h. Exploding in popularity driven by social media trends. Multiple color variations available.", "ChillKeep"),
    (13, "Laptop Stand Adjustable Aluminum", "Electronics", 44.99, 64.99, "💻", 4.7, 8901, 88, '["trending"]', 23000, 55, "High", "Portable aluminum laptop stand with 6 height adjustments and foldable design. Evergreen product with steady sales across all seasons.", "DeskPro"),
    (14, "Seed Germination Kit (72 pods)", "Home", 29.99, 44.99, "🌱", 4.6, 3456, 81, '["new"]', 9400, 68, "Medium", "Complete seed starter kit for indoor gardening. Trending with the urban gardening movement and highly seasonal (spring peaks).", "GroWell"),
    (15, "Wireless Earbuds TWS Pro", "Electronics", 59.99, 99.99, "🎵", 4.6, 12340, 89, '["hot"]', 45000, 58, "Very High", "True wireless earbuds with ANC, 30hr total battery, IPX5 water resistance. Competitive category but strong price-to-value positioning.", "SoundMax"),
    (16, "Foam Roller Deep Tissue Massage", "Sports", 19.99, 34.99, "🏋️", 4.7, 5678, 85, '["deal"]', 28000, 70, "High", "High-density EVA foam roller for post-workout recovery. Great margins and consistent demand year-round with easy bundling potential.", "FlexFit"),
    (17, "Silk Pillowcase Set (2-Pack)", "Health", 39.99, 59.99, "🛏️", 4.8, 4567, 87, '["trending"]', 17600, 64, "High", "100% mulberry silk pillowcases in queen and king size. Beauty-adjacent product with strong social proof and repeat purchase potential.", "LuxSilk"),
    (18, "Digital Food Scale Kitchen Smart", "Home", 18.99, 29.99, "⚖️", 4.9, 23456, 93, '["hot","deal"]', 78000, 66, "Very High", "Ultra-precise 0.1g food scale with tare function and built-in timer. Massive volume seller in the kitchen category, dominated by repeat buyers.", "MeasurePro"),
    (19, "Camping Headlamp Rechargeable 1200LM", "Sports", 35.99, 54.99, "🔦", 4.8, 6789, 86, '["new"]', 14300, 58, "High", "USB-C rechargeable headlamp with motion sensor, red light mode, and 20h runtime. Growing demand from both outdoor and emergency preparedness markets.", "LitePath"),
    (20, "Macro Photography Lens Kit (5-in-1)", "Electronics", 29.99, 49.99, "📷", 4.4, 2345, 79, '["new"]', 6700, 72, "Medium", "Universal clip-on lens kit for smartphones. Photography hobby boom driving increased interest, especially among Gen Z creators.", "LensMaster"),
    (21, "Aromatherapy Diffuser Oil Set", "Health", 42.99, 64.99, "🕯️", 4.7, 3456, 84, '["trending"]', 20100, 75, "High", "Bundle of 6 essential oils with a BPA-free ultrasonic diffuser. Wellness trend driving strong conversions. Perfect gifting product.", "ZenAroma"),
    (22, "Toddler Art Supplies Mega Kit", "Toys", 38.99, 59.99, "🎨", 4.9, 8901, 91, '["hot"]', 24500, 60, "High", "100-piece washable art kit for toddlers including crayons, markers, stamps, and watercolors. Top gifting product year-round with spike in holiday season.", "TinkerKids"),
    (23, "Pet Hair Remover Roller Pro", "Home", 15.99, 24.99, "🐾", 4.8, 34567, 95, '["hot","trending"]', 89000, 80, "Very High", "Self-cleaning pet hair remover with upgradeable base. Evergreen product for pet owners with exceptional margins and near-zero returns.", "PetPro"),
    (24, "Stainless Steel Water Bottle 32oz", "Sports", 26.99, 39.99, "🍶", 4.7, 19876, 90, '["hot"]', 56000, 62, "Very High", "Triple-wall insulated bottle with leak-proof lid. Powerhouse seller and gateway product with strong brand loyalty and bundling potential.", "HydroForce"),
    (25, "Smart LED Strip Lights 32ft RGB", "Electronics", 24.99, 39.99, "🌈", 4.5, 18900, 91, '["hot","trending"]', 52000, 68, "Very High", "WiFi-enabled LED strip lights with 16M colors, music sync, and voice control via Alexa/Google. Massive TikTok-driven demand among Gen Z room decor enthusiasts.", "LitePro"),
    (26, "Ergonomic Vertical Mouse Wireless", "Electronics", 34.99, 54.99, "🖱️", 4.6, 6780, 84, '["trending"]', 18500, 60, "High", "Ergonomic vertical design reduces wrist strain. 6 programmable buttons, 3 DPI levels, USB-C rechargeable. Growing with the WFH and RSI-awareness trends.", "DeskPro"),
    (27, "Air Fryer 5.8 Quart Digital", "Home", 69.99, 109.99, "🍟", 4.8, 24500, 93, '["hot","deal"]', 61000, 45, "Very High", "Digital touchscreen air fryer with 8 presets, rapid air circulation, and dishwasher-safe basket. Kitchen must-have with exceptional review velocity.", "HomeChef"),
    (28, "Massage Gun Deep Tissue Percussive", "Health", 89.99, 149.99, "💆", 4.7, 8900, 88, '["hot"]', 27000, 52, "Very High", "30-speed percussion massager with 6 interchangeable heads and ultra-quiet brushless motor. Recovery tool of choice for athletes and desk workers alike.", "FlexFit"),
    (29, "Wireless Charging Pad 3-in-1", "Electronics", 38.99, 59.99, "🔋", 4.5, 11200, 86, '["trending"]', 31000, 62, "High", "Charges phone, watch, and earbuds simultaneously. Qi-certified 15W fast charging with LED indicator and anti-slip pad. Universal compatibility.", "DriveCharge"),
    (30, "Smart Plug WiFi Mini (4-Pack)", "Home", 29.99, 44.99, "🔌", 4.7, 31200, 92, '["hot"]', 74000, 70, "Very High", "Voice-controlled smart plugs compatible with Alexa, Google Home, and IFTTT. Timer scheduling and energy monitoring included. Highly bundleable.", "NetSphere"),
    (31, "Jump Rope Speed Weighted Digital", "Sports", 19.99, 32.99, "⏱️", 4.6, 5400, 83, '["new","trending"]', 16800, 72, "High", "Digital counter jump rope with adjustable weighted handles and ball bearing system. Trending in home fitness and boxing workout communities.", "IronEdge"),
    (32, "Vitamin C Serum with Hyaluronic Acid", "Health", 18.99, 34.99, "🧴", 4.8, 42300, 95, '["hot","trending"]', 112000, 82, "Very High", "Clinical-grade 20% vitamin C serum with hyaluronic acid and vitamin E. Skincare staple with massive repeat purchase rate and social media presence.", "GlowTech"),
    (33, "Dash Cam 4K Front and Rear", "Automotive", 79.99, 129.99, "📹", 4.6, 7800, 87, '["trending"]', 19500, 48, "High", "Dual-channel 4K dash cam with night vision, GPS, parking mode, and 170-degree wide angle. Insurance demand and safety awareness driving steady growth.", "DriveCharge"),
    (34, "Electric Milk Frother Handheld", "Home", 14.99, 24.99, "☕", 4.7, 28900, 90, '["hot","deal"]', 93000, 78, "Very High", "USB rechargeable milk frother with 3 speed settings and stainless steel whisk. Impulse buy with massive volume — top performer in kitchen gadgets.", "HomeChef"),
    (35, "Kids Walkie Talkies Long Range (2-Pack)", "Toys", 27.99, 42.99, "📻", 4.5, 6700, 84, '["new"]', 14200, 64, "High", "3-mile range walkie talkies for kids with flashlight, VOX function, and 22 channels. Outdoor play trending post-pandemic with strong gifting appeal.", "TinkerKids"),
    (36, "Heated Car Seat Cushion Universal", "Automotive", 35.99, 54.99, "🪑", 4.4, 4300, 80, '["trending"]', 11800, 58, "Medium", "12V heated seat cushion with 3 temperature settings and auto shut-off. Seasonal but highly profitable — strong Q4 and winter demand in northern markets.", "DriveCharge"),
    (37, "Mechanical Keyboard RGB Wireless", "Electronics", 54.99, 89.99, "⌨️", 4.7, 9800, 89, '["hot","trending"]', 26000, 50, "Very High", "Hot-swappable mechanical keyboard with Bluetooth 5.0, 2.4GHz, and USB-C. Custom RGB backlighting per key. Enthusiast and gaming communities driving demand.", "DeskPro"),
    (38, "Collagen Peptides Powder Unflavored", "Health", 29.99, 44.99, "💊", 4.8, 19800, 91, '["hot"]', 48000, 60, "Very High", "Grass-fed hydrolyzed collagen peptides with 20g protein per serving. Wellness supplement category leader with strong subscription and repeat purchase metrics.", "ZenAroma"),
    (39, "Solar Powered Garden Lights (12-Pack)", "Home", 32.99, 49.99, "🌞", 4.5, 14500, 86, '["new","deal"]', 37000, 68, "High", "Color-changing solar path lights with stainless steel stakes. Zero operating cost product with strong curb appeal — seasonal spike in spring and summer.", "EcoKitch"),
    (40, "Baby Monitor WiFi 2K Pan-Tilt", "Electronics", 49.99, 79.99, "👶", 4.6, 8900, 87, '["trending"]', 22000, 52, "High", "2K HD baby monitor with two-way audio, night vision, motion detection, and lullaby player. App-controlled with encrypted cloud and SD card storage.", "NetSphere"),
    (41, "Pull-Up Bar Doorway No-Screw", "Sports", 32.99, 49.99, "🏋️", 4.7, 11200, 88, '["hot"]', 29000, 64, "Very High", "Heavy-duty doorway pull-up bar supporting up to 440 lbs with foam grips and no drilling required. Calisthenics trend fueling consistent sales growth.", "IronEdge"),
    (42, "Board Game Strategy Family Night", "Toys", 34.99, 49.99, "🎲", 4.9, 5600, 85, '["new","trending"]', 13500, 55, "High", "Award-winning strategy board game for ages 10+ with 2-6 player modes. Board game renaissance driven by family time trends and content creator reviews.", "BuildBrain"),
    (43, "Car Vacuum Cleaner Handheld 12V", "Automotive", 29.99, 44.99, "🧹", 4.5, 15600, 86, '["hot"]', 38000, 66, "Very High", "8000Pa suction handheld car vacuum with HEPA filter and LED light. Comes with 4 attachments for crevice, upholstery, and wet/dry cleaning.", "DriveCharge"),
    (44, "Portable Projector Mini 1080p WiFi", "Electronics", 89.99, 149.99, "🎬", 4.4, 4500, 82, '["trending"]', 9800, 46, "High", "Pocket-size 1080p projector with WiFi mirroring, built-in speakers, and 120-inch throw. Outdoor movie night trend among millennials and families.", "LitePro"),
    (110, "Magnetic Plush Throw Blanket", "Home & Garden", 70.96, 100.32, "🛋️", 4.8, 8093, 86, '["new"]', 76587, 49, "Low", "High quality magnetic plush throw blanket perfect for your needs. Excellent value and highly rated by customers.", "FlexFit"),
    (111, "Rechargeable Jump Starter Power Bank", "Automotive", 69.49, 106.72, "⚡", 4.7, 14020, 87, '["hot","new"]', 90001, 36, "Medium", "High quality rechargeable jump starter power bank perfect for your needs. Excellent value and highly rated by customers.", "BlendGo"),
    (112, "Premium Dollhouse", "Toys & Games", 94.33, 135.71, "🏠", 4.4, 11093, 65, '["hot","trending"]', 15668, 68, "Low", "High quality premium dollhouse perfect for your needs. Excellent value and highly rated by customers.", "LensMaster"),
    (113, "Compact Plush Throw Blanket", "Home & Garden", 116.36, 137.6, "🛋️", 4.1, 1312, 94, '["hot","new"]', 41275, 67, "Low", "High quality compact plush throw blanket perfect for your needs. Excellent value and highly rated by customers.", "PostureTech"),
    (114, "Interactive Dumbbell Set", "Sports & Fitness", 10.84, 43.33, "🏋️", 4.4, 8784, 60, '["new"]', 16347, 32, "Low", "High quality interactive dumbbell set perfect for your needs. Excellent value and highly rated by customers.", "TinkerKids"),
    (115, "Foldable Sleep Mask", "Health & Beauty", 24.01, 38.86, "😴", 5.0, 16510, 79, '["hot","new"]', 28905, 41, "Medium", "High quality foldable sleep mask perfect for your needs. Excellent value and highly rated by customers.", "DriveCharge"),
    (116, "Portable Drone with Camera", "Electronics", 142.15, 169.51, "🚁", 4.1, 15463, 72, '["trending","deal"]', 13173, 81, "Medium", "High quality portable drone with camera perfect for your needs. Excellent value and highly rated by customers.", "SoundMax"),
    (117, "Ergonomic Car Cover", "Automotive", 86.24, 104.11, "🚗", 4.5, 9078, 97, '["trending"]', 51978, 59, "Very High", "High quality ergonomic car cover perfect for your needs. Excellent value and highly rated by customers.", "ZenAroma"),
    (118, "Electric Ceramic Knife Set", "Home & Garden", 69.92, 91.86, "🔪", 4.8, 8607, 64, '["hot","trending"]', 42759, 56, "Low", "High quality electric ceramic knife set perfect for your needs. Excellent value and highly rated by customers.", "LitePro"),
    (119, "Heavy-Duty USB-C Hub", "Electronics", 112.55, 150.45, "🔌", 4.6, 10150, 86, '["deal"]', 63286, 74, "Medium", "High quality heavy-duty usb-c hub perfect for your needs. Excellent value and highly rated by customers.", "PetPro"),
    (120, "Foldable USB-C Hub", "Electronics", 26.65, 49.25, "🔌", 5.0, 7536, 95, '["hot","new"]', 37115, 57, "High", "High quality foldable usb-c hub perfect for your needs. Excellent value and highly rated by customers.", "GroWell"),
    (121, "Heavy-Duty Building Blocks", "Toys & Games", 12.73, 50.02, "🧱", 4.4, 604, 64, '["hot","trending"]', 62675, 53, "High", "High quality heavy-duty building blocks perfect for your needs. Excellent value and highly rated by customers.", "GlowTech"),
    (122, "Advanced Acupressure Mat", "Health & Beauty", 147.93, 194.14, "🧘", 4.7, 14627, 98, '["hot"]', 21249, 59, "Very High", "High quality advanced acupressure mat perfect for your needs. Excellent value and highly rated by customers.", "IronEdge"),
    (123, "Electric Sleep Mask", "Health & Beauty", 127.29, 145.36, "😴", 5.0, 9995, 90, '["trending","deal"]', 8926, 58, "Medium", "High quality electric sleep mask perfect for your needs. Excellent value and highly rated by customers.", "DriveCharge"),
    (124, "Advanced OBD2 Scanner", "Automotive", 84.59, 113.11, "💻", 4.4, 8317, 94, '["new"]', 41673, 32, "Medium", "High quality advanced obd2 scanner perfect for your needs. Excellent value and highly rated by customers.", "LitePro"),
    (125, "Smart Dumbbell Set", "Sports & Fitness", 90.31, 111.67, "🏋️", 4.8, 7162, 68, '["trending"]', 79712, 59, "Very High", "High quality smart dumbbell set perfect for your needs. Excellent value and highly rated by customers.", "BuildBrain"),
    (126, "Compact Dollhouse", "Toys & Games", 98.97, 112.46, "🏠", 4.5, 13454, 91, '["hot","new"]', 41696, 58, "Low", "High quality compact dollhouse perfect for your needs. Excellent value and highly rated by customers.", "BuildBrain"),
    (127, "Wireless Power Bank 10000mAh", "Electronics", 88.37, 128.89, "🔋", 4.9, 14016, 60, '["trending"]', 60404, 62, "Very High", "High quality wireless power bank 10000mah perfect for your needs. Excellent value and highly rated by customers.", "DeskPro"),
    (128, "Advanced Microfiber Towels", "Automotive", 14.91, 45.07, "🧽", 4.8, 6160, 90, '["deal"]', 27981, 64, "Very High", "High quality advanced microfiber towels perfect for your needs. Excellent value and highly rated by customers.", "SoundMax"),
    (129, "Compact OBD2 Scanner", "Automotive", 56.1, 104.0, "💻", 5.0, 16834, 80, '["hot"]', 44575, 80, "Medium", "High quality compact obd2 scanner perfect for your needs. Excellent value and highly rated by customers.", "HomeChef"),
    (130, "Foldable Light Therapy Lamp", "Health & Beauty", 88.62, 117.21, "💡", 4.7, 376, 88, '["trending"]', 34640, 74, "High", "High quality foldable light therapy lamp perfect for your needs. Excellent value and highly rated by customers.", "SoundMax"),
    (131, "Portable Bluetooth Speaker", "Electronics", 28.92, 78.06, "🔊", 4.9, 2127, 94, '["hot","trending"]', 26463, 83, "High", "High quality portable bluetooth speaker perfect for your needs. Excellent value and highly rated by customers.", "NetSphere"),
    (132, "Rechargeable Dumbbell Set", "Sports & Fitness", 116.07, 123.64, "🏋️", 4.9, 13322, 98, '["trending"]', 19844, 42, "Medium", "High quality rechargeable dumbbell set perfect for your needs. Excellent value and highly rated by customers.", "ZenAroma"),
    (133, "Wireless Smart Lock", "Home & Garden", 38.94, 69.25, "🔒", 4.6, 12749, 67, '["hot"]', 13051, 46, "Low", "High quality wireless smart lock perfect for your needs. Excellent value and highly rated by customers.", "BlendGo"),
    (134, "Magnetic Noise-Cancelling Earbuds", "Electronics", 83.36, 111.75, "🎧", 4.0, 7378, 94, '["new"]', 98147, 32, "Very High", "High quality magnetic noise-cancelling earbuds perfect for your needs. Excellent value and highly rated by customers.", "GroWell"),
    (135, "Portable Tablet Stand", "Electronics", 141.05, 189.25, "📱", 4.8, 6877, 97, '["new"]', 88271, 44, "High", "High quality portable tablet stand perfect for your needs. Excellent value and highly rated by customers.", "LitePath"),
    (136, "Smart Treadmill Mat", "Sports & Fitness", 22.83, 62.62, "🏃", 4.2, 19347, 74, '["new"]', 76707, 45, "Medium", "High quality smart treadmill mat perfect for your needs. Excellent value and highly rated by customers.", "PostureTech"),
    (137, "Rechargeable VR Headset Tracker", "Electronics", 149.0, 180.45, "🥽", 4.5, 11006, 68, '["trending"]', 37412, 37, "Low", "High quality rechargeable vr headset tracker perfect for your needs. Excellent value and highly rated by customers.", "ChillKeep"),
    (138, "Electric Steering Wheel Cover", "Automotive", 51.82, 95.22, "🏎️", 4.7, 10177, 72, '["new"]', 37870, 51, "Medium", "High quality electric steering wheel cover perfect for your needs. Excellent value and highly rated by customers.", "PetPro"),
    (139, "Wireless Foot Spa", "Health & Beauty", 95.86, 136.27, "🦶", 4.1, 13527, 76, '["deal"]', 2935, 80, "High", "High quality wireless foot spa perfect for your needs. Excellent value and highly rated by customers.", "BuildBrain"),
    (140, "Advanced Microfiber Towels", "Automotive", 61.06, 94.39, "🧽", 4.5, 4310, 85, '["hot","trending"]', 28825, 84, "Medium", "High quality advanced microfiber towels perfect for your needs. Excellent value and highly rated by customers.", "BlendGo"),
    (141, "Digital Treadmill Mat", "Sports & Fitness", 122.05, 171.06, "🏃", 4.2, 14436, 61, '["trending","deal"]', 69503, 59, "High", "High quality digital treadmill mat perfect for your needs. Excellent value and highly rated by customers.", "NetSphere"),
    (142, "Foldable Action Figure", "Toys & Games", 140.69, 153.44, "🦸", 4.3, 9192, 89, '["hot"]', 38630, 42, "Medium", "High quality foldable action figure perfect for your needs. Excellent value and highly rated by customers.", "HomeChef"),
    (143, "Advanced Acupressure Mat", "Health & Beauty", 22.19, 27.23, "🧘", 4.4, 333, 99, '["hot","trending"]', 25793, 44, "High", "High quality advanced acupressure mat perfect for your needs. Excellent value and highly rated by customers.", "PostureTech"),
    (144, "Premium Bed Sheets Set", "Home & Garden", 142.65, 167.62, "🛏️", 4.3, 9435, 90, '["trending"]', 73680, 30, "Medium", "High quality premium bed sheets set perfect for your needs. Excellent value and highly rated by customers.", "HydroForce"),
    (145, "Magnetic Water Gun", "Toys & Games", 40.53, 74.68, "🔫", 4.3, 12867, 83, '["new"]', 17170, 75, "Medium", "High quality magnetic water gun perfect for your needs. Excellent value and highly rated by customers.", "DeskPro"),
    (146, "Ergonomic Scratch Repair Kit", "Automotive", 27.81, 39.95, "🛠️", 4.5, 19160, 85, '["trending","deal"]', 1040, 55, "Medium", "High quality ergonomic scratch repair kit perfect for your needs. Excellent value and highly rated by customers.", "PetPro"),
    (147, "Advanced Sleeping Bag", "Sports & Fitness", 12.87, 31.15, "🎒", 4.0, 15777, 66, '["hot","trending"]', 47764, 47, "Medium", "High quality advanced sleeping bag perfect for your needs. Excellent value and highly rated by customers.", "PostureTech"),
    (148, "Compact Coffee Maker", "Home & Garden", 114.12, 127.19, "☕", 4.9, 10174, 88, '["new"]', 48030, 44, "Low", "High quality compact coffee maker perfect for your needs. Excellent value and highly rated by customers.", "LuxSilk"),
    (149, "Ultra-Slim Air Purifier", "Home & Garden", 27.37, 49.52, "🌬️", 5.0, 15501, 86, '["new"]', 20262, 48, "Very High", "High quality ultra-slim air purifier perfect for your needs. Excellent value and highly rated by customers.", "TinkerKids"),
    (150, "Electric Scratch Repair Kit", "Automotive", 84.25, 124.46, "🛠️", 4.8, 281, 64, '["trending","deal"]', 6484, 53, "Very High", "High quality electric scratch repair kit perfect for your needs. Excellent value and highly rated by customers.", "PostureTech"),
    (151, "Portable OBD2 Scanner", "Automotive", 141.62, 163.2, "💻", 4.3, 11269, 97, '["hot","trending"]', 29289, 77, "Very High", "High quality portable obd2 scanner perfect for your needs. Excellent value and highly rated by customers.", "LensMaster"),
    (152, "Foldable Coffee Maker", "Home & Garden", 115.73, 134.64, "☕", 4.8, 3254, 60, '["trending"]', 47865, 52, "Low", "High quality foldable coffee maker perfect for your needs. Excellent value and highly rated by customers.", "LitePro"),
    (153, "Ergonomic Remote Control Car", "Toys & Games", 119.59, 128.33, "🏎️", 4.6, 16070, 82, '["trending","deal"]', 37031, 73, "Medium", "High quality ergonomic remote control car perfect for your needs. Excellent value and highly rated by customers.", "EcoKitch"),
    (154, "Compact Power Bank 10000mAh", "Electronics", 112.48, 134.91, "🔋", 4.9, 16697, 89, '["trending"]', 20597, 63, "High", "High quality compact power bank 10000mah perfect for your needs. Excellent value and highly rated by customers.", "EcoKitch"),
    (155, "Interactive Remote Control Car", "Toys & Games", 95.93, 143.78, "🏎️", 5.0, 14640, 85, '["deal"]', 49087, 36, "Medium", "High quality interactive remote control car perfect for your needs. Excellent value and highly rated by customers.", "LitePro"),
    (156, "Digital Bluetooth Speaker", "Electronics", 87.05, 135.54, "🔊", 4.0, 18916, 61, '["hot"]', 87306, 65, "Medium", "High quality digital bluetooth speaker perfect for your needs. Excellent value and highly rated by customers.", "PetPro"),
    (157, "Advanced Magic Kit", "Toys & Games", 141.63, 164.0, "🎩", 4.8, 14848, 94, '["deal"]', 83054, 55, "Medium", "High quality advanced magic kit perfect for your needs. Excellent value and highly rated by customers.", "MeasurePro"),
    (158, "Interactive Microfiber Towels", "Automotive", 35.73, 73.6, "🧽", 5.0, 5638, 69, '["hot","trending"]', 12950, 36, "Low", "High quality interactive microfiber towels perfect for your needs. Excellent value and highly rated by customers.", "BlendGo"),
    (159, "Ergonomic Noise-Cancelling Earbuds", "Electronics", 60.77, 82.61, "🎧", 4.3, 10007, 96, '["trending","deal"]', 23357, 39, "Medium", "High quality ergonomic noise-cancelling earbuds perfect for your needs. Excellent value and highly rated by customers.", "BlendGo"),
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
    ("🇮🇳", "India", "Growing", 47),
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
    ("Wireless Noise-Cancelling Headphones Pro", "price-drop", "Price Drop", "Alert when price drops below $110.00", "active", "📉"),
    ("Insulated Tumbler 40oz", "trend", "Trend Alert", "Alert when trending score exceeds 95", "triggered", "🔥"),
    ("Pet Hair Remover Roller Pro", "stock", "Stock Alert", "Alert when stock drops below 500 units", "triggered", "📦"),
    ("Smart Posture Corrector", "price-rise", "Price Rise", "Alert when competition raises prices above $55", "paused", "📈"),
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
            "Electronics": [("Power Bank 10000mAh", "🔋"), ("Noise-Cancelling Earbuds", "🎧"), ("Bluetooth Speaker", "🔊"), ("Tablet Stand", "📱"), ("VR Headset Tracker", "🥽"), ("Drone with Camera", "🚁"), ("USB-C Hub", "🔌")],
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
            price = float(round(float(random.uniform(9.99, 149.99)), 2))
            original_price = float(round(float(price * random.uniform(1.1, 1.8)), 2))
            rating = float(round(float(random.uniform(3.5, 5.0)), 1))
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
