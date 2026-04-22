from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Copy this file to db.py and fill in your credentials
DB_URL = "mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost:3306/wera_db"

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session()