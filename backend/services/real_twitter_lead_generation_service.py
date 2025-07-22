"""
Real Twitter/X Lead Generation Service - NO MOCK DATA
"""
import tweepy
import uuid
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp

class RealTwitterLeadGenerationService:
    def __init__(self, db):
        self.db = db
        self.twitter_leads = db["twitter_leads"]
        self.lead_searches = db["lead_searches"]
        self.contact_enrichment = db["contact_enrichment"]
        
        # Real Twitter API v2 credentials
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        
        # Initialize Twitter API client
        self.client = tweepy.Client(
            bearer_token=self.get_bearer_token(),
            consumer_key=self.api_key,
            consumer_secret=self.api_secret
        )
        
    def get_bearer_token(self):
        """Get Bearer token for Twitter API v2"""
        try:
            auth_url = "https://api.twitter.com/oauth2/token"
            auth_headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
            }
            auth_data = "grant_type=client_credentials"
            
            import base64
            credentials = f"{self.api_key}:{self.api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            auth_headers["Authorization"] = f"Basic {encoded_credentials}"
            
            response = requests.post(auth_url, headers=auth_headers, data=auth_data)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                self.log(f"Failed to get bearer token: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"Error getting bearer token: {str(e)}")
            return None
    
    async def search_twitter_leads(self, search_criteria: Dict) -> Dict:
        """Search for real Twitter leads using Twitter API v2"""
        try:
            search_id = str(uuid.uuid4())
            
            # Build search query from criteria
            query_parts = []
            
            if search_criteria.get("keywords"):
                for keyword in search_criteria["keywords"]:
                    query_parts.append(keyword)
            
            if search_criteria.get("hashtags"):
                for hashtag in search_criteria["hashtags"]:
                    query_parts.append(f"#{hashtag}")
                    
            if search_criteria.get("location"):
                query_parts.append(f'place:"{search_criteria["location"]}"')
                
            if search_criteria.get("verified_only"):
                query_parts.append("is:verified")
                
            search_query = " ".join(query_parts)
            if not search_query:
                search_query = "business owner entrepreneur"  # Default search
                
            # Search tweets using Twitter API
            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=min(search_criteria.get("max_results", 100), 100),
                tweet_fields=["author_id", "created_at", "public_metrics", "context_annotations"],
                user_fields=["id", "name", "username", "description", "public_metrics", "verified", "location", "url"],
                expansions=["author_id"]
            )
            
            leads_found = []
            
            if tweets.data:
                # Process users from tweets
                users = {user.id: user for user in tweets.includes.get("users", [])}
                
                for tweet in tweets.data:
                    user = users.get(tweet.author_id)
                    if user:
                        # Extract lead information
                        lead_data = {
                            "_id": str(uuid.uuid4()),
                            "platform": "twitter",
                            "user_id": str(user.id),
                            "username": user.username,
                            "display_name": user.name,
                            "bio": user.description or "",
                            "follower_count": user.public_metrics.get("followers_count", 0),
                            "following_count": user.public_metrics.get("following_count", 0),
                            "tweet_count": user.public_metrics.get("tweet_count", 0),
                            "verified": user.verified or False,
                            "location": user.location or "",
                            "website_url": user.url or "",
                            "profile_image": f"https://twitter.com/{user.username}/photo",
                            "latest_tweet": {
                                "text": tweet.text,
                                "created_at": tweet.created_at.isoformat(),
                                "retweets": tweet.public_metrics.get("retweet_count", 0),
                                "likes": tweet.public_metrics.get("like_count", 0)
                            },
                            "engagement_rate": self.calculate_engagement_rate(user.public_metrics),
                            "extracted_at": datetime.utcnow(),
                            "search_id": search_id
                        }
                        
                        # Attempt to extract contact information
                        contact_info = await self.extract_contact_information(user)
                        lead_data["contact_info"] = contact_info
                        
                        leads_found.append(lead_data)
                        
                        # Save to database
                        await self.twitter_leads.insert_one(lead_data)
            
            # Save search record
            search_record = {
                "_id": search_id,
                "search_criteria": search_criteria,
                "query_used": search_query,
                "results_count": len(leads_found),
                "executed_at": datetime.utcnow(),
                "status": "completed"
            }
            
            await self.lead_searches.insert_one(search_record)
            
            return {
                "search_id": search_id,
                "leads_found": len(leads_found),
                "leads": leads_found[:10],  # Return first 10 for preview
                "total_available": len(leads_found)
            }
            
        except Exception as e:
            self.log(f"Error searching Twitter leads: {str(e)}")
            return {"error": str(e)}
    
    def calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate from Twitter metrics"""
        followers = metrics.get("followers_count", 0)
        if followers == 0:
            return 0.0
            
        # Estimate engagement based on followers vs activity
        tweets = metrics.get("tweet_count", 0)
        if tweets == 0:
            return 0.0
            
        # Simple engagement rate calculation
        engagement_ratio = (tweets / max(followers, 1)) * 100
        return min(engagement_ratio, 100.0)  # Cap at 100%
    
    async def extract_contact_information(self, user) -> Dict:
        """Extract contact information from Twitter profile"""
        contact_info = {
            "email": None,
            "phone": None,
            "website": user.url or None,
            "other_social": []
        }
        
        # Check bio for email patterns
        if user.description:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, user.description)
            if emails:
                contact_info["email"] = emails[0]
        
        # Check for website and try to extract more info
        if user.url:
            try:
                # This would typically involve web scraping the linked website
                # For now, we'll just store the URL
                contact_info["website"] = user.url
            except Exception:
                pass
                
        return contact_info
    
    async def export_leads_to_csv(self, search_id: str, export_format: str = "csv") -> Dict:
        """Export leads to CSV with real data"""
        try:
            leads = await self.twitter_leads.find({"search_id": search_id}).to_list(length=None)
            
            if not leads:
                return {"error": "No leads found for this search"}
            
            import csv
            import io
            
            output = io.StringIO()
            
            # Define CSV headers
            headers = [
                "Username", "Display Name", "Bio", "Followers", "Following", 
                "Tweets", "Verified", "Location", "Website", "Email", 
                "Engagement Rate", "Latest Tweet", "Extracted Date"
            ]
            
            writer = csv.writer(output)
            writer.writerow(headers)
            
            for lead in leads:
                row = [
                    lead.get("username", ""),
                    lead.get("display_name", ""),
                    lead.get("bio", ""),
                    lead.get("follower_count", 0),
                    lead.get("following_count", 0),
                    lead.get("tweet_count", 0),
                    lead.get("verified", False),
                    lead.get("location", ""),
                    lead.get("website_url", ""),
                    lead.get("contact_info", {}).get("email", ""),
                    f"{lead.get('engagement_rate', 0):.2f}%",
                    lead.get("latest_tweet", {}).get("text", ""),
                    lead.get("extracted_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "export_id": str(uuid.uuid4()),
                "format": export_format,
                "leads_count": len(leads),
                "csv_content": csv_content,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def log(self, message: str):
        print(f"[TWITTER] {message}")
