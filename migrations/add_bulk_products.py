import sqlite3
import random
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")

def generate_products():
    categories = {
        "Electronics": ["💻", "📱", "🎧", "⌚", "📷", "🔋", "🔌", "🔌", "🔊", "🖨️"],
        "Health & Beauty": ["✨", "🧴", "💄", "💆", "🛁", "🧴", "💅", "⚕️", "💊"],
        "Home & Garden": ["🏡", "🛋️", "🪴", "🚿", "🍳", "☕", "🍽️", "🧹", "🔪"],
        "Sports & Fitness": ["🏋️", "🧘", "🏃", "⚽", "🎾", "🚴", "🥊", "🏸"],
        "Toys & Games": ["🎮", "🎲", "🧸", "🤖", "🧩", "🎯", "🚁", "🚗"],
        "Automotive": ["🚗", "🏎️", "🧽", "🔧", "🔋", "🛞", "🧼", "⛽"],
        "Fashion": ["👗", "👕", "👖", "🧦", "🧥", "👒", "👓", "🥾", "👟"]
    }

    adjectives = ["Wireless", "Smart", "Portable", "Premium", "Ergonomic", "Compact", "Advanced", "Heavy-Duty", "Foldable", "Interactive", "Digital", "Electric", "Magnetic", "Ultra-Slim", "Rechargeable"]
    
    nouns = {
        "Electronics": ["Headphones", "Speaker", "Charger", "Tablet", "Monitor", "Keyboard", "Mouse", "Webcam", "Microphone", "Router"],
        "Health & Beauty": ["Massager", "Trimmer", "Serum", "Cleanser", "Moisturizer", "Diffuser", "Therapy Light", "Shaver", "Toothbrush"],
        "Home & Garden": ["Blender", "Vacuum", "Purifier", "Heater", "Fan", "Lamp", "Cooker", "Toaster", "Kettle", "Scale"],
        "Sports & Fitness": ["Treadmill", "Dumbbells", "Mat", "Resistance Bands", "Tracker", "Bottle", "Roller", "Grip", "Gloves"],
        "Toys & Games": ["Drone", "Action Figure", "Board Game", "Puzzle", "RC Car", "Building Blocks", "Plushie", "Console"],
        "Automotive": ["Dash Cam", "Jump Starter", "Vacuum", "Mount", "Tire Inflator", "Polisher", "Scanner", "Organizer"],
        "Fashion": ["Jacket", "Sneakers", "Watch", "Sunglasses", "Backpack", "Belt", "Wallet", "Scarf", "Gloves"]
    }

    brands = ["EcoLife", "TechPro", "HomeEssentials", "FlexFit", "SoundMax", "GlowTech", "DriveCharge", "NetSphere", "BuildBrain", "ChillKeep"]
    
    tags_pool = ["hot", "trending", "new", "deal", "bestseller"]

    products = []
    
    for category, category_emojis in categories.items():
        for _ in range(50): # 50 products per category
            adj = random.choice(adjectives)
            noun = random.choice(nouns[category])
            name = f"{adj} {noun} {random.randint(10, 9000)}"
            emoji = random.choice(category_emojis)
            price = round(random.uniform(10.0, 300.0), 2)
            original_price = round(price * random.uniform(1.1, 1.8), 2)
            rating = round(random.uniform(3.5, 5.0), 1)
            reviews = random.randint(10, 50000)
            score = random.randint(40, 99)
            
            num_tags = random.randint(1, 3)
            tags = json.dumps(random.sample(tags_pool, num_tags))
            
            sales = random.randint(100, 100000)
            margin = random.randint(20, 80)
            demand = random.choice(["Low", "Medium", "High", "Very High"])
            description = f"High quality {name.lower()} perfect for your needs. Excellent value and highly rated by customers."
            brand = random.choice(brands)
            
            products.append((name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand))
            
    return products

def add_products():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # ensure categories exist
    categories = ["Electronics", "Health & Beauty", "Home & Garden", "Sports & Fitness", "Toys & Games", "Automotive", "Fashion"]
    for cat in categories:
        cur.execute("SELECT COUNT(*) FROM categories WHERE name=?", (cat,))
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO categories (name, icon, count, pct) VALUES (?, '📦', 100, 50)", (cat,))
            
    products = generate_products()
    
    cur.executemany(
        """INSERT INTO products (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products
    )
    
    conn.commit()
    conn.close()
    print(f"Successfully added {len(products)} products across all categories.")

if __name__ == "__main__":
    add_products()
