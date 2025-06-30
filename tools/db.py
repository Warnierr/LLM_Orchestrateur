import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    key = Column(String, primary_key=True)
    value = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db(db_path: str = 'data/nina_metadata.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine) 