import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")

def insert_products():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Make sure Fashion category exists
    cur.execute("SELECT COUNT(*) FROM categories WHERE name='Fashion'")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO categories (name, icon, count, pct) VALUES ('Fashion', '👗', 120, 60)")

    new_products = [
        # --- Fashion ---
        ("Men's Classic Wool Blend Peacoat", "Fashion", 89.99, 149.99, "🧥", 4.7, 342, 85, '["winter", "trending"]', 1500, 48, "High", "A timeless classic wool blend peacoat for men. Excellent for cold seasons. Highly durable and fashionable.", "UrbanWear"),
        ("Women's High-Waisted Yoga Leggings", "Fashion", 24.99, 39.99, "👖", 4.8, 15024, 95, '["hot", "trending"]', 45000, 65, "Very High", "Squat-proof, buttery soft high-waisted leggings with deep side pockets. A staple in activewear.", "FlexFit"),
        ("Unisex Polarized Sunglasses Classic", "Fashion", 15.99, 29.99, "🕶️", 4.5, 4530, 80, '["hot", "deal"]', 22000, 72, "High", "Retro classic polarized sunglasses with UV400 protection. Perfect impulse buy product.", "SunGuard"),
        ("Chunky Platform Sneakers", "Fashion", 55.99, 85.99, "👟", 4.6, 2150, 88, '["trending"]', 8500, 50, "Medium", "Streetwear inspired chunky sole platform sneakers. Popular with Gen Z demographic.", "StepPro"),
        ("Minimalist Stainless Steel Watch", "Fashion", 45.99, 75.99, "⌚", 4.7, 3400, 82, '["deal"]', 12000, 60, "High", "Ultra-thin minimalist watch with mesh band. Water resistant and highly elegant for everyday use.", "ChronoPrime"),

        # --- Automotive ---
        ("OBD2 Scanner OBDII Code Reader", "Automotive", 29.99, 45.99, "🚘", 4.8, 25000, 93, '["hot", "trending"]', 60000, 68, "Very High", "Universal car diagnostic scanner tool to easily find and clear error codes.", "AutoTool"),
        ("Microfiber Car Wash Towels (6-Pack)", "Automotive", 14.99, 22.99, "🧽", 4.9, 18450, 96, '["hot"]', 70000, 75, "Very High", "Ultra soft, highly absorbent microfiber towels for scratch-free detailing and washing.", "ShineMaster"),
        ("Tire Inflator Portable Air Compressor", "Automotive", 34.99, 59.99, "💨", 4.7, 8500, 88, '["trending"]', 32000, 52, "High", "12V portable tire inflator with digital pressure gauge and emergency LED light.", "DriveCharge"),
        ("Car Jump Starter 2000A Battery Pack", "Automotive", 69.99, 119.99, "🔋", 4.8, 6200, 90, '["trending"]', 15000, 45, "High", "Powerful portable lithium-ion jump starter, can jump up to 8.0L gas engines.", "PowerBoost"),
        ("Leather Car Seat Covers Full Set", "Automotive", 149.99, 249.99, "💺", 4.5, 3100, 84, '["deal"]', 5200, 40, "Medium", "Premium PU leather car seat covers, universal fit, waterproof and breathable.", "LuxuryDrive"),

        # --- Toys & Games ---
        ("Magnetic Tiles Building Blocks Set", "Toys & Games", 45.99, 69.99, "🧱", 4.9, 12800, 94, '["hot", "trending"]', 42000, 55, "Very High", "100-piece magnetic 3D building blocks, great STEM educational toy for toddlers and kids.", "BuildBrain"),
        ("Interactive Smart Robot Puppy", "Toys & Games", 39.99, 59.99, "🐶", 4.6, 5400, 85, '["trending"]', 18000, 62, "High", "RC robot dog toy that barks, dances, and follows commands. Huge hit for holidays.", "TechPets"),
        ("Giant Outdoor Jenga Timber Tower", "Toys & Games", 49.99, 79.99, "🪵", 4.8, 3800, 82, '["deal"]', 11000, 45, "Medium", "Premium giant wooden blocks for outdoor party games. Reaches over 5 feet tall during play.", "OutdoorFun"),
        ("Drones with Camera for Kids 1080P", "Toys & Games", 59.99, 89.99, "🚁", 4.5, 7600, 88, '["hot"]', 25000, 58, "High", "Foldable RC quadcopter with 1080p FPV camera, altitude hold, and one-key start.", "SkyFly"),
        ("LCD Writing Tablet 10-Inch Doodle Board", "Toys & Games", 12.99, 24.99, "📝", 4.7, 34000, 91, '["hot", "deal"]', 120000, 78, "Very High", "Colorful screen writing pad, perfect travel toy for toddlers to draw without mess.", "TinkerKids"),
    ]

    for prod in new_products:
        name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand = prod
        cur.execute(
            """INSERT INTO products (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
        )

    conn.commit()
    conn.close()
    print("Successfully added new products to Fashion, Automotive, and Toys & Games.")

if __name__ == "__main__":
    insert_products()
