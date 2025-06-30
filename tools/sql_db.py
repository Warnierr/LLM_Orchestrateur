from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Fact(Base):
    __tablename__ = 'facts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False, unique=True)
    source = Column(String(100)) # Ex: 'conversation', 'web_search', 'document'
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_input = Column(Text, nullable=False)
    nina_response = Column(Text, nullable=False)
    meta = Column(Text)
    summary = Column(Text, nullable=True)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    key = Column(String, primary_key=True)
    value = Column(Text)

class SQLDatabase:
    def __init__(self, db_url=None):
        db_url = db_url or os.getenv('DATABASE_URL', 'sqlite:///data/nina_memory.db')
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_fact(self, content: str, source: str):
        """Sauvegarde un nouveau fait dans la base de données, en évitant les doublons."""
        session = self.Session()
        try:
            # Vérifier si le fait existe déjà
            existing_fact = session.query(Fact).filter_by(content=content).first()
            if not existing_fact:
                new_fact = Fact(content=content, source=source)
                session.add(new_fact)
                session.commit()
                return new_fact
            return existing_fact
        finally:
            session.close()

    def get_all_facts(self):
        """Récupère tous les faits stockés dans la base de données."""
        session = self.Session()
        try:
            return session.query(Fact).order_by(Fact.timestamp.desc()).all()
        finally:
            session.close()

    def load_conversations(self):
        session = self.Session()
        try:
            convs = session.query(Conversation).order_by(Conversation.timestamp).all()
            results = []
            for c in convs:
                meta_data = {}
                # Récupération sécurisée du champ meta
                meta_raw = getattr(c, 'meta', None)
                if meta_raw:
                    try:
                        meta_data = json.loads(meta_raw)
                    except Exception:
                        meta_data = {}
                results.append({
                    'timestamp': c.timestamp.isoformat(),
                    'user': c.user_input,
                    'nina': c.nina_response,
                    'meta': meta_data
                })
            return results
        finally:
            session.close()

    def load_user_profile(self):
        session = self.Session()
        try:
            profiles = session.query(UserProfile).all()
            return {p.key: p.value for p in profiles}
        finally:
            session.close()

    def save_interaction(self, user_query: str, nina_response: str, summary: Optional[str] = None):
        """Sauvegarde une interaction et son résumé dans la base de données."""
        with self.Session() as session:
            interaction = Conversation(
                user_input=user_query,
                nina_response=nina_response,
                summary=summary
            )
            session.add(interaction)
            session.commit()

    def save_user_profile(self, key, value):
        session = self.Session()
        try:
            p = session.get(UserProfile, key)
            if p:
                p.value = value
            else:
                p = UserProfile(key=key, value=value)
                session.add(p)
            session.commit()
        finally:
            session.close() 