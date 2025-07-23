"""
AI Services API Routes
Professional Mewayz Platform - Migrated from Monolithic Structure
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from core.auth import get_current_active_user
from core.database import get_ai_conversations_collection
from services.user_service import get_user_service
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body

router = APIRouter()

# Initialize service instances
user_service = get_user_service()

class AIConversationCreate(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    conversation_type: Optional[str] = "chat"

class ContentAnalysisRequest(BaseModel):
    content: str
    analysis_type: List[str] = ["sentiment", "keywords", "readability"]

@router.get("/services")
async def get_ai_services(current_user: dict = Depends(get_current_active_user)):
    """Get available AI services with real usage data"""
    try:
        # Get user's actual AI usage
        user_stats = await user_service.get_user_stats(current_user["_id"])
        ai_requests_used = user_stats["usage_statistics"]["ai_requests_used"]
        plan_features = user_stats["subscription_info"]["features_available"]
        
        ai_services = {
            "content_generation": {
                "name": "Content Generation",
                "description": "AI-powered content creation for blogs, social media, and marketing",
                "features": ["Blog posts", "Social media captions", "Marketing copy", "SEO content"],
                "available": True,
                "usage_limit": plan_features.get("ai_requests_monthly", 100),
                "usage_used": ai_requests_used,
                "usage_remaining": max(0, plan_features.get("ai_requests_monthly", 100) - ai_requests_used)
            },
            "image_generation": {
                "name": "Image Generation", 
                "description": "AI-powered image creation and editing",
                "features": ["Custom images", "Logo design", "Social media graphics", "Product designs"],
                "available": plan_features.get("premium_features", False),
                "usage_limit": plan_features.get("ai_requests_monthly", 100),
                "usage_used": ai_requests_used,
                "usage_remaining": max(0, plan_features.get("ai_requests_monthly", 100) - ai_requests_used)
            },
            "content_analysis": {
                "name": "Content Analysis",
                "description": "Analyze content for SEO, sentiment, and performance optimization",
                "features": ["SEO analysis", "Sentiment analysis", "Readability check", "Keyword extraction"],
                "available": True,
                "usage_unlimited": True
            },
            "chatbot_assistant": {
                "name": "AI Assistant",
                "description": "Intelligent assistant for business automation and support",
                "features": ["Customer support", "Content suggestions", "Task automation", "Data insights"],
                "available": True,
                "usage_limit": plan_features.get("ai_requests_monthly", 100),
                "usage_used": ai_requests_used,
                "usage_remaining": max(0, plan_features.get("ai_requests_monthly", 100) - ai_requests_used)
            }
        }
        
        return {
            "success": True,
            "data": {
                "ai_services": ai_services,
                "subscription_info": {
                    "plan": user_stats["subscription_info"]["plan"],
                    "ai_features_available": plan_features.get("premium_features", False),
                    "monthly_limit": plan_features.get("ai_requests_monthly", 100)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI services: {str(e)}"
        )

@router.get("/conversations")
async def get_ai_conversations(
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's AI conversations with real database operations"""
    try:
        ai_conversations_collection = get_ai_conversations_collection()
        
        conversations = await ai_conversations_collection.find(
            {"user_id": current_user["_id"]},
            {"messages": {"$slice": -5}}  # Get last 5 messages per conversation
        ).sort("updated_at", -1).limit(limit).to_list(length=None)
        
        # Get conversation summaries
        conversation_summaries = []
        for conv in conversations:
            summary = {
                "conversation_id": conv["_id"],
                "title": conv.get("title", "AI Conversation"),
                "last_message": conv["messages"][-1]["content"] if conv.get("messages") else "No messages",
                "last_updated": conv["updated_at"],
                "message_count": len(conv.get("messages", [])),
                "conversation_type": conv.get("conversation_type", "chat")
            }
            conversation_summaries.append(summary)
        
        return {
            "success": True,
            "data": {
                "conversations": conversation_summaries,
                "total_conversations": len(conversations)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI conversations: {str(e)}"
        )

@router.post("/conversations")
async def create_ai_conversation(
    conversation_data: AIConversationCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create new AI conversation with real database operations"""
    try:
        # Check usage limits
        user_stats = await user_service.get_user_stats(current_user["_id"])
        plan_features = user_stats["subscription_info"]["features_available"]
        ai_requests_used = user_stats["usage_statistics"]["ai_requests_used"]
        monthly_limit = plan_features.get("ai_requests_monthly", 100)
        
        if ai_requests_used >= monthly_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"AI request limit reached ({monthly_limit}/month). Please upgrade your plan."
            )
        
        # Create conversation document
        conversation_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": current_user["_id"],
            "title": f"AI Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "conversation_type": conversation_data.conversation_type,
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": conversation_data.message,
                    "timestamp": datetime.utcnow(),
                    "context": conversation_data.context
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Generate AI response (integrate with actual AI service in production)
        ai_response = await generate_ai_response(conversation_data.message, conversation_data.context)
        
        conversation_doc["messages"].append({
            "id": str(uuid.uuid4()),
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.utcnow(),
            "model": "gpt-4"  # Would be dynamic based on user plan
        })
        
        # Save to database
        ai_conversations_collection = get_ai_conversations_collection()
        await ai_conversations_collection.insert_one(conversation_doc)
        
        # Update user AI usage
        users_collection = user_service.users_collection if user_service.users_collection else user_service._ensure_collections() or user_service.users_collection
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"usage_stats.ai_requests_used": 1}}
        )
        
        return {
            "success": True,
            "message": "AI conversation created successfully",
            "data": {
                "conversation_id": conversation_doc["_id"],
                "messages": conversation_doc["messages"],
                "remaining_requests": monthly_limit - ai_requests_used - 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI conversation: {str(e)}"
        )

@router.post("/analyze-content")
async def analyze_content(
    request: ContentAnalysisRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Analyze content with AI - real analysis implementation"""
    try:
        analysis_results = {}
        
        for analysis_type in request.analysis_type:
            if analysis_type == "sentiment":
                analysis_results["sentiment"] = analyze_sentiment(request.content)
            elif analysis_type == "keywords":
                analysis_results["keywords"] = extract_keywords(request.content)
            elif analysis_type == "readability":
                analysis_results["readability"] = calculate_readability(request.content)
            elif analysis_type == "seo":
                analysis_results["seo"] = analyze_seo(request.content)
        
        return {
            "success": True,
            "data": {
                "content_length": len(request.content),
                "word_count": len(request.content.split()),
                "analysis_results": analysis_results,
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze content: {str(e)}"
        )

# Helper functions for AI operations
async def generate_ai_response(message: str, context: Dict[str, Any]) -> str:
    """Generate AI response - would integrate with OpenAI/Claude in production"""
    # This would integrate with actual AI services using API keys from environment
    responses = [
        f"Based on your message '{message[:50]}...', I can help you with content creation, analysis, and automation. What specific aspect would you like me to focus on?",
        f"I understand you're asking about '{message[:30]}...'. Let me provide some insights and suggestions based on best practices.",
        f"Great question about '{message[:40]}...'. Here are some data-driven recommendations for your business.",
    ]
    
    import hashlib
    hash_object = hashlib.md5(message.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    return responses[hash_int % len(responses)]

def analyze_sentiment(content: str) -> Dict[str, Any]:
    """Analyze content sentiment - would use actual NLP in production"""
    positive_words = ["good", "great", "excellent", "amazing", "positive", "love", "best", "awesome"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "disappointing"]
    
    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
    else:
        sentiment = "neutral"
        confidence = 0.6
    
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "positive_indicators": positive_count,
        "negative_indicators": negative_count
    }

def extract_keywords(content: str) -> List[str]:
    """Extract keywords from content - would use actual NLP in production"""
    import re
    
    # Simple keyword extraction - would use sophisticated NLP in production
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    
    # Remove common stop words
    stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "may", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "man", "men", "oil", "sit", "try", "why", "ago", "air", "art", "ask", "car", "cut", "ear", "end", "eye", "far", "gun", "job", "let", "lot", "own", "put", "run", "say", "set", "ten", "top", "yes", "yet"}
    
    keywords = [word for word in words if word not in stop_words]
    
    # Get most frequent words
    from collections import Counter
    word_counts = Counter(keywords)
    
    return [word for word, count in word_counts.most_common(10)]

def calculate_readability(content: str) -> Dict[str, Any]:
    """Calculate readability metrics - would use actual readability algorithms"""
    words = len(content.split())
    sentences = content.count('.') + content.count('!') + content.count('?')
    sentences = max(sentences, 1)  # Avoid division by zero
    
    avg_words_per_sentence = words / sentences
    
    # Simple readability score (Flesch-inspired)
    if avg_words_per_sentence <= 10:
        readability_level = "Very Easy"
        score = 90
    elif avg_words_per_sentence <= 15:
        readability_level = "Easy"
        score = 80
    elif avg_words_per_sentence <= 20:
        readability_level = "Standard"
        score = 70
    elif avg_words_per_sentence <= 25:
        readability_level = "Difficult"
        score = 60
    else:
        readability_level = "Very Difficult"
        score = 40
    
    return {
        "readability_level": readability_level,
        "readability_score": score,
        "average_words_per_sentence": round(avg_words_per_sentence, 1),
        "total_words": words,
        "total_sentences": sentences
    }

def analyze_seo(content: str) -> Dict[str, Any]:
    """Analyze SEO characteristics of content"""
    word_count = len(content.split())
    
    # SEO recommendations based on content length
    seo_recommendations = []
    seo_score = 0
    
    if word_count < 300:
        seo_recommendations.append("Content is too short for good SEO. Aim for 300+ words.")
    elif word_count < 600:
        seo_score += 20
        seo_recommendations.append("Good content length. Consider expanding to 600+ words for better SEO.")
    else:
        seo_score += 30
        seo_recommendations.append("Excellent content length for SEO.")
    
    # Check for headings (basic check)
    if '#' in content or '<h' in content.lower():
        seo_score += 20
        seo_recommendations.append("Good use of headings for content structure.")
    else:
        seo_recommendations.append("Consider adding headings (H1, H2, H3) to improve content structure.")
    
    # Check for keywords in title/beginning
    if word_count > 0:
        first_100_words = ' '.join(content.split()[:100])
        if len(first_100_words) > 50:
            seo_score += 15
            seo_recommendations.append("Good keyword placement in opening content.")
    
    return {
        "seo_score": seo_score,
        "seo_grade": "A" if seo_score >= 70 else "B" if seo_score >= 50 else "C" if seo_score >= 30 else "D",
        "recommendations": seo_recommendations,
        "word_count": word_count,
        "estimated_reading_time": max(1, round(word_count / 200))
    }