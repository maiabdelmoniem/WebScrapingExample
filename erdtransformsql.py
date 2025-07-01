import pandas as pd
import sqlite3

# --- Step 1: Load the Data ---
csv_file = 'books_data.csv'
json_file = 'books_data.json'

# Load CSV and JSON data
csv_df = pd.read_csv(csv_file)
json_df = pd.read_json(json_file)

df = json_df.copy()

# --- Step 2: Clean the Data ---
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

# --- Step 3: Save Cleaned Data ---
df.to_csv('cleaned_data.csv', index=False)
df.to_json('cleaned_data.json', orient='records', lines=True)

# --- Step 4: Save to SQLite and Create Star Schema ---
conn = sqlite3.connect('databasebooks.db')
cursor = conn.cursor()

# --- Step 5: Create Star Schema using SQL ---
schema_sql = """
DROP TABLE IF EXISTS fact_book_sales;
DROP TABLE IF EXISTS dim_book;
DROP TABLE IF EXISTS dim_product_type;
DROP TABLE IF EXISTS dim_availability;

CREATE TABLE fact_book_sales (
    book_id             INTEGER,
    product_type_id     INTEGER,
    availability_id     INTEGER,
    price_excl_tax      REAL,
    price_incl_tax      REAL,
    tax                 REAL,
    stock_quantity      INTEGER,
    number_of_reviews   INTEGER,
    star_rating         TEXT,
    FOREIGN KEY (book_id)         REFERENCES dim_book(book_id),
    FOREIGN KEY (product_type_id) REFERENCES dim_product_type(product_type_id),
    FOREIGN KEY (availability_id) REFERENCES dim_availability(availability_id)
);

CREATE TABLE dim_book (
    book_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT,
    description     TEXT,
    upc             TEXT UNIQUE,
    product_page    TEXT
);

CREATE TABLE dim_product_type (
    product_type_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    category         TEXT UNIQUE
);

CREATE TABLE dim_availability (
    availability_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    availability     INTEGER
);
"""

# Execute schema creation
cursor.executescript(schema_sql)

conn.commit()
conn.close()
