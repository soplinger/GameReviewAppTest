import sqlite3

conn = sqlite3.connect('game_reviews.db')
cursor = conn.cursor()

# Get all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Existing tables:", [t[0] for t in tables])

# Check if reviews table exists
if 'reviews' in [t[0] for t in tables]:
    print("\n✓ Reviews table exists")
    
    # Get column info
    columns = cursor.execute("PRAGMA table_info(reviews)").fetchall()
    print("\nReviews table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\n✗ Reviews table does NOT exist - migration needed")

conn.close()
