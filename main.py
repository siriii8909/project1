import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
try:
    connection = psycopg2.connect(DATABASE_URL)
    print("Successfully connected to Supabase!")
    connection.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
