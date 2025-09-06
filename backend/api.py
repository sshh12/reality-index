#!/usr/bin/env python3
"""
FastAPI backend for newsletter subscription management
"""

import re
from typing import List, Optional
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database.database import get_database, init_database
from backend.database.models import Subscription, NewsletterArchive
from market_analyzer.topic_config import TOPICS, get_topic_keys, get_topic_descriptions, get_topic_display_names

# Initialize FastAPI app
app = FastAPI(
    title="The Reality Index API",
    description="API for managing AI-generated prediction market newsletter subscriptions",
    version="1.0.0"
)

# Available topics
VALID_TOPICS = get_topic_keys()

# Pydantic models for request/response
class SubscriptionRequest(BaseModel):
    email: EmailStr
    topics: List[str] = Field(..., min_items=1, max_items=8)
    
    @validator('topics')
    def validate_topics(cls, v):
        for topic in v:
            if topic not in VALID_TOPICS:
                raise ValueError(f'Invalid topic: {topic}. Valid topics are: {VALID_TOPICS}')
        return v

class SubscriptionResponse(BaseModel):
    message: str
    email: str
    topics: List[str]
    success: bool = True

class UnsubscribeResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    message: str
    success: bool = False

class NewsletterArchiveResponse(BaseModel):
    id: int
    topics: List[str]
    title: str
    content_html: str
    sent_at: str  # ISO format datetime
    subscriber_count: int

class NewsletterPreviewResponse(BaseModel):
    topics: List[str]
    newsletters: List[NewsletterArchiveResponse]
    count: int

def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_database()
        print("✅ Database initialized successfully")
        
        # Mount static files if directory exists
        static_dir = "/app/static"
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            print("✅ Static files mounted")
        else:
            print("⚠️  Static directory not found, skipping static file mounting")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "newsletter-api"}

# Subscribe endpoint
@app.post("/api/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    subscription_data: SubscriptionRequest,
    db: Session = Depends(get_database)
):
    try:
        email = subscription_data.email.lower().strip()
        topics = sorted(subscription_data.topics)  # Sort for consistency
        
        # Check if this exact email/topics combination already exists
        existing = Subscription.get_by_email_and_topics(db, email, topics)
        
        if existing:
            if existing.active:
                return SubscriptionResponse(
                    message="You're already subscribed to this topic combination!",
                    email=email,
                    topics=topics
                )
            else:
                # Reactivate inactive subscription
                existing.active = True
                db.commit()
                return SubscriptionResponse(
                    message="Welcome back! Subscription reactivated.",
                    email=email,
                    topics=topics
                )
        else:
            # Create new subscription for this topic combination
            subscription = Subscription.create(db, email, topics)
            
            # Send confirmation email
            try:
                from market_analyzer.subscription_email_sender import SubscriptionEmailSender
                email_sender = SubscriptionEmailSender()
                email_sender.send_confirmation_email(email, topics, subscription.unsubscribe_token)
            except Exception as e:
                print(f"⚠️  Failed to send confirmation email: {e}")
                # Don't fail the subscription if confirmation email fails
            
            return SubscriptionResponse(
                message="Successfully subscribed to the newsletter!",
                email=email,
                topics=topics
            )
            
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already subscribed to this topic combination"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription failed: {str(e)}"
        )

# Unsubscribe endpoint
@app.delete("/api/unsubscribe/{token}", response_model=UnsubscribeResponse)
async def unsubscribe(
    token: str,
    db: Session = Depends(get_database)
):
    try:
        subscription = Subscription.get_by_token(db, token)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid unsubscribe link"
            )
        
        if not subscription.active:
            return UnsubscribeResponse(
                message="You are already unsubscribed."
            )
        
        subscription.unsubscribe(db)
        
        return UnsubscribeResponse(
            message="Successfully unsubscribed from all newsletters."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unsubscribe failed: {str(e)}"
        )

# Get subscription info (for unsubscribe page)
@app.get("/api/subscription/{token}")
async def get_subscription_info(
    token: str,
    db: Session = Depends(get_database)
):
    try:
        subscription = Subscription.get_by_token(db, token)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid link"
            )
        
        return {
            "email": subscription.email,
            "topics": subscription.topics,
            "active": subscription.active,
            "created_at": subscription.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription info: {str(e)}"
        )

# List available topics
@app.get("/api/topics")
async def get_topics():
    return {
        "topics": VALID_TOPICS,
        "display_names": get_topic_display_names(),
        "descriptions": get_topic_descriptions()
    }

# Get newsletter previews by topic combination
@app.get("/api/newsletters/preview", response_model=NewsletterPreviewResponse)
async def get_newsletter_preview(
    topics: str,  # Comma-separated topics like "ai,politics"
    limit: int = 5,
    db: Session = Depends(get_database)
):
    """Get recent newsletters for a specific topic combination"""
    try:
        # Parse and validate topics
        topic_list = [topic.strip().lower() for topic in topics.split(",")]
        
        # Validate topics
        for topic in topic_list:
            if topic not in VALID_TOPICS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid topic: {topic}. Valid topics are: {VALID_TOPICS}"
                )
        
        # Get newsletters for this topic combination
        newsletters = NewsletterArchive.get_by_topics(db, topic_list, limit)
        
        # Convert to response format
        newsletter_responses = []
        for newsletter in newsletters:
            newsletter_responses.append(NewsletterArchiveResponse(
                id=newsletter.id,
                topics=newsletter.topics,
                title=newsletter.title,
                content_html=newsletter.content_html,
                sent_at=newsletter.sent_at.isoformat(),
                subscriber_count=newsletter.subscriber_count
            ))
        
        return NewsletterPreviewResponse(
            topics=sorted(topic_list),
            newsletters=newsletter_responses,
            count=len(newsletter_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get newsletter previews: {str(e)}"
        )

# Get specific newsletter by ID for preview
@app.get("/api/newsletters/{newsletter_id}")
async def get_newsletter_by_id(
    newsletter_id: int,
    db: Session = Depends(get_database)
):
    """Get specific newsletter by ID for preview"""
    try:
        newsletter = db.query(NewsletterArchive).filter(NewsletterArchive.id == newsletter_id).first()
        
        if not newsletter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Newsletter not found"
            )
        
        return {
            "id": newsletter.id,
            "topics": newsletter.topics,
            "title": newsletter.title,
            "content_html": newsletter.content_html,
            "content_markdown": newsletter.content_markdown,
            "sent_at": newsletter.sent_at.isoformat(),
            "subscriber_count": newsletter.subscriber_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get newsletter: {str(e)}"
        )

# Admin endpoint to get subscription stats (basic)
@app.get("/api/admin/stats")
async def get_subscription_stats(db: Session = Depends(get_database)):
    """Basic subscription statistics - consider adding authentication in production"""
    try:
        total_subs = db.query(Subscription).count()
        active_subs = db.query(Subscription).filter(Subscription.active == True).count()
        
        # Count by topics
        topic_stats = {}
        for topic in VALID_TOPICS:
            count = db.query(Subscription).filter(
                Subscription.active == True,
                Subscription.topics.cast(str).contains(topic)
            ).count()
            topic_stats[topic] = count
        
        return {
            "total_subscriptions": total_subs,
            "active_subscriptions": active_subs,
            "topic_breakdown": topic_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

# SPA route - serve index.html for all non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React SPA for all non-API routes"""
    # If it's an API route that doesn't exist, return 404
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # For root or non-API paths, serve index.html
    index_path = "/app/static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # If no static files, return a basic message
    return {"message": "Frontend not built yet", "tip": "Run the Docker build to compile the React app"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)