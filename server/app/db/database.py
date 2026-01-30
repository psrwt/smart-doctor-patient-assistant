import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# connection string
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("❌ No DATABASE_URL found in environment variables!")

# Optimized Engine Configuration
# We use NullPool for Vercel/Supabase to avoid "Too many connections" errors.
is_cloud = "pooler.supabase.com" in SQLALCHEMY_DATABASE_URL or "neon.tech" in SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Checks if the connection is still alive
    poolclass=NullPool if is_cloud else None  # Disables local pooling for cloud
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()