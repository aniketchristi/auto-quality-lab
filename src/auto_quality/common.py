import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')

def connect():
    return psycopg.connect(os.getenv('DATABASE_URL', 'postgresql://127.0.0.1:55432/auto_quality'), connect_timeout=5)

def initialize():
    with connect() as conn:
        conn.execute((ROOT / 'sql/schema.sql').read_text())
