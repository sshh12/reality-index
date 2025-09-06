import uuid
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class Subscription(Base):
    """Database model for newsletter subscriptions - allows multiple topic combinations per email"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)  # Removed unique constraint
    topics = Column(JSON, nullable=False, default=list)  # List of topic strings: ["politics", "ai"]
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)
    unsubscribe_token = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Ensure unique combination of email and topics (sorted)
    __table_args__ = (UniqueConstraint('email', 'topics', name='unique_email_topics'),)

    def __repr__(self):
        return f"<Subscription(email='{self.email}', topics={self.topics}, active={self.active})>"

    @classmethod
    def create(cls, db: Session, email: str, topics: List[str]) -> "Subscription":
        """Create a new subscription for specific topic combination"""
        # Sort topics for consistent storage
        sorted_topics = sorted(topics)
        
        subscription = cls(
            email=email.lower().strip(),
            topics=sorted_topics,
            unsubscribe_token=str(uuid.uuid4())
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @classmethod
    def get_by_email_and_topics(cls, db: Session, email: str, topics: List[str]) -> Optional["Subscription"]:
        """Get subscription by email and specific topic combination"""
        sorted_topics = sorted(topics)
        topics_json = json.dumps(sorted_topics)
        return db.query(cls).filter(
            cls.email == email.lower().strip(),
            cls.topics.cast(Text) == topics_json
        ).first()

    @classmethod
    def get_by_email(cls, db: Session, email: str) -> List["Subscription"]:
        """Get all subscriptions for an email"""
        return db.query(cls).filter(cls.email == email.lower().strip()).all()

    @classmethod
    def get_by_token(cls, db: Session, token: str) -> Optional["Subscription"]:
        """Get subscription by unsubscribe token"""
        return db.query(cls).filter(cls.unsubscribe_token == token).first()

    @classmethod
    def get_active_subscriptions(cls, db: Session) -> List["Subscription"]:
        """Get all active subscriptions"""
        return db.query(cls).filter(cls.active == True).all()

    @classmethod
    def get_subscriptions_by_topics(cls, db: Session, topics: List[str]) -> List["Subscription"]:
        """Get active subscriptions for specific topic combination"""
        sorted_topics = sorted(topics)
        topics_json = json.dumps(sorted_topics)
        return db.query(cls).filter(
            cls.active == True,
            cls.topics.cast(Text) == topics_json
        ).all()

    def unsubscribe(self, db: Session):
        """Unsubscribe this specific topic combination"""
        self.active = False
        db.commit()

    @classmethod
    def unsubscribe_all_for_email(cls, db: Session, email: str) -> int:
        """Unsubscribe all topic combinations for an email"""
        updated = db.query(cls).filter(
            cls.email == email.lower().strip(),
            cls.active == True
        ).update({cls.active: False})
        db.commit()
        return updated


class NewsletterArchive(Base):
    """Database model for storing sent newsletters"""
    __tablename__ = "newsletter_archive"

    id = Column(Integer, primary_key=True, index=True)
    topics = Column(JSON, nullable=False)  # List of topic strings: ["politics", "ai"]
    title = Column(String, nullable=False)  # Newsletter title/subject
    content_html = Column(Text, nullable=False)  # Full HTML content
    content_markdown = Column(Text, nullable=False)  # Original markdown content
    sent_at = Column(DateTime, default=datetime.utcnow)
    subscriber_count = Column(Integer, default=0)  # Number of subscribers who received it
    
    def __repr__(self):
        return f"<NewsletterArchive(topics={self.topics}, title='{self.title}', sent_at='{self.sent_at}')>"

    @classmethod
    def create(cls, db: Session, topics: List[str], title: str, content_html: str, 
               content_markdown: str, subscriber_count: int = 0) -> "NewsletterArchive":
        """Create a new newsletter archive entry"""
        sorted_topics = sorted(topics)
        
        archive = cls(
            topics=sorted_topics,
            title=title,
            content_html=content_html,
            content_markdown=content_markdown,
            subscriber_count=subscriber_count
        )
        db.add(archive)
        db.commit()
        db.refresh(archive)
        return archive

    @classmethod
    def get_by_topics(cls, db: Session, topics: List[str], limit: int = 10) -> List["NewsletterArchive"]:
        """Get recent newsletters for specific topic combination"""
        sorted_topics = sorted(topics)
        topics_json = json.dumps(sorted_topics)
        return db.query(cls).filter(
            cls.topics.cast(Text) == topics_json
        ).order_by(cls.sent_at.desc()).limit(limit).all()

    @classmethod
    def get_all_recent(cls, db: Session, limit: int = 50) -> List["NewsletterArchive"]:
        """Get all recent newsletters across all topics"""
        return db.query(cls).order_by(cls.sent_at.desc()).limit(limit).all()

    @classmethod
    def get_unique_topic_combinations(cls, db: Session) -> List[List[str]]:
        """Get all unique topic combinations that have newsletters"""
        results = db.query(cls.topics).distinct().all()
        return [result[0] for result in results]