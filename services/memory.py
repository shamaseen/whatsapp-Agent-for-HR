from typing import List, Dict
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

Base = declarative_base()

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)
    role = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class ConversationMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db_session = Session()

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        msg = ConversationHistory(session_id=self.session_id, role=role, content=content)
        self.db_session.add(msg)
        self.db_session.commit()
        self._cleanup_old_messages()

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        messages = self.db_session.query(ConversationHistory).filter_by(
            session_id=self.session_id
        ).order_by(ConversationHistory.timestamp.desc()).limit(limit).all()
        return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]

    def _cleanup_old_messages(self):
        """Keep only the most recent MAX_MESSAGES_PER_SESSION messages"""
        count = self.db_session.query(ConversationHistory).filter_by(session_id=self.session_id).count()
        if count > settings.MAX_MESSAGES_PER_SESSION:
            messages_to_delete = count - settings.MAX_MESSAGES_PER_SESSION
            old_messages = self.db_session.query(ConversationHistory).filter_by(
                session_id=self.session_id
            ).order_by(ConversationHistory.timestamp).limit(messages_to_delete).all()
            for msg in old_messages:
                self.db_session.delete(msg)
            self.db_session.commit()
