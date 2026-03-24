import sqlite3
import random
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")

categories = ["Electronics", "Home", "Health", "Sports", "Toys", "Automotive", "Fashion"]
brands = ["SoundMax", "LitePro", "EcoKitch", "PostureTech", "FlexFit", "BlendGo", "BuildBrain", "DriveCharge", "NetSphere", "IronEdge", "GlowTech", "ChillKeep", "DeskPro", "GroWell", "LuxSilk", "MeasurePro", "LitePath", "LensMaster", "ZenAroma", "TinkerKids", "PetPro", "HydroForce", "HomeChef", "UrbanWear", "SunGuard"]

adjectives = ["Smart", "Wireless", "Portable", "Electric", "Digital", "Ergonomic", "Advanced", "Premium", "Compact", "Heavy-Duty", "Eco-friendly", "Foldable", "Magnetic", "Ultra-Slim", "Rechargeable", "Interactive"]

nouns_by_cat = {
    "Electronics": [("Power Bank 10000mAh", "🔋"), ("Bluetooth Speaker", "🔊"), ("Webcam 1080p", "📷"), ("Gaming Mouse", "🖱️"), ("Tablet Stand", "📱"), ("USB-C Hub", "🔌"), ("Noise-Cancelling Earbuds", "🎧"), ("Smart Thermostat", "🌡️"), ("VR Headset Tracker", "🥽"), ("Drone with Camera", "🚁")],
    "Health": [("Water Flosser", "🦷"), ("Sleep Mask", "😴"), ("Neck Massager", "💆"), ("Electric Toothbrush", "🪥"), ("Posture Corrector", "🦴"), ("Acupressure Mat", "🧘"), ("Foot Spa", "🦶"), ("Light Therapy Lamp", "💡"), ("Gua Sha Set", "✨"), ("Fitness Tracker", "⌚")],
    "Home": [("Air Purifier", "🌬️"), ("Robot Vacuum", "🤖"), ("Coffee Maker", "☕"), ("Humidifier", "💧"), ("Security Camera", "📷"), ("Smart Lock", "🔒"), ("Bed Sheets Set", "🛏️"), ("Ceramic Knife Set", "🔪"), ("Sunrise Alarm Clock", "🌅"), ("Plush Throw Blanket", "🛋️")],
    "Sports": [("Dumbbell Set", "🏋️"), ("Treadmill Mat", "🏃"), ("Cycling Gloves", "🧤"), ("Protein Shaker Bottle", "🥤"), ("Knee Sleeves", "🦵"), ("Yoga Block", "🧱"), ("Jump Rope Digital", "⏱️"), ("Camping Tent", "⛺"), ("Sleeping Bag", "🎒"), ("Hiking Poles", "🦯")],
    "Toys": [("Puzzle 1000 Pieces", "🧩"), ("Remote Control Car", "🏎️"), ("Dollhouse", "🏠"), ("Building Blocks", "🧱"), ("Board Game", "🎲"), ("Plush Dinosaur", "🦕"), ("Action Figure", "🦸"), ("Magic Kit", "🎩"), ("Educational Tablet", "📱"), ("Water Gun", "🔫")],
    "Automotive": [("Microfiber Towels", "🧽"), ("Tire Inflator Portable", "💨"), ("Car Cover", "🚗"), ("Windshield Sun Shade", "☀️"), ("Seat Organizer", "💺"), ("Jump Starter Power Bank", "⚡"), ("OBD2 Scanner", "💻"), ("Steering Wheel Cover", "🏎️"), ("Car Air Freshener", "🌲"), ("Scratch Repair Kit", "🛠️")],
    "Fashion": [("Winter Scarf", "🧣"), ("Running Sneakers", "👟"), ("Leather Wallet", "👛"), ("Sunglasses", "🕶️"), ("Backpack", "🎒"), ("Denim Jacket", "🧥"), ("Yoga Pants", "👖"), ("Beanie Hat", "🧢"), ("Chronograph Watch", "⌚"), ("Canvas Tote Bag", "🛍️")]
}

tags_list = ['["hot"]', '["trending"]', '["new"]', '["deal"]', '["hot","new"]', '["trending","deal"]', '["hot","trending"]']
demand_levels = ["Low", "Medium", "High", "Very High"]

conn = sqlite3.connect(db_path)
cur = conn.cursor()

new_products_for_db = []
num_products = 50

for i in range(num_products):
    cat = random.choice(categories)
    noun, emoji = random.choice(nouns_by_cat[cat])
    adj = random.choice(adjectives)
    
    name = f"{adj} {noun}"
    price = round(random.uniform(10.0, 150.0), 2)
    original_price = round(price + random.uniform(5.0, 50.0), 2)
    rating = round(random.uniform(4.0, 5.0), 1)
    reviews = random.randint(100, 20000)
    score = random.randint(60, 99)
    tags = random.choice(tags_list)
    sales = random.randint(1000, 100000)
    margin = random.randint(30, 85)
    demand = random.choice(demand_levels)
    description = f"High quality {name.lower()} perfect for your needs. Excellent value and highly rated by customers."
    brand = random.choice(brands)
    
    new_products_for_db.append((name, cat, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand))

cur.executemany(
    """INSERT INTO products (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    new_products_for_db
)
conn.commit()
conn.close()

print("Successfully added 50 random products to the database.")
