import httpx
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from backend.config.settings import settings

class FacebookAPI:
    """Service for interacting with Facebook Graph API"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v16.0"
        self.api_key = settings.FACEBOOK_API_KEY
    
    async def get_page_posts(self, page_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get posts from a Facebook page"""
        url = f"{self.base_url}/{page_id}/posts"
        params = {
            "access_token": self.api_key,
            "limit": limit,
            "fields": "id,message,created_time,comments.limit(25){id,message,created_time}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to fetch Facebook posts: {response.text}"}
            
            return response.json()
    
    async def get_post_comments(self, post_id: str, limit: int = 25) -> Dict[str, Any]:
        """Get comments from a Facebook post"""
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "access_token": self.api_key,
            "limit": limit,
            "fields": "id,message,created_time"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to fetch Facebook comments: {response.text}"}
            
            return response.json()

class TwitterAPI:
    """Service for interacting with Twitter API"""
    
    def __init__(self):
        self.base_url = "https://api.twitter.com/2"
        self.api_key = settings.TWITTER_API_KEY
    
    async def get_user_tweets(self, username: str, limit: int = 10) -> Dict[str, Any]:
        """Get tweets from a Twitter user"""
        # First get the user ID from username
        user_url = f"{self.base_url}/users/by/username/{username}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_url, headers=headers)
            if user_response.status_code != 200:
                return {"error": f"Failed to fetch Twitter user: {user_response.text}"}
            
            user_data = user_response.json()
            user_id = user_data.get("data", {}).get("id")
            
            if not user_id:
                return {"error": "User ID not found"}
            
            # Then get the user's tweets
            tweets_url = f"{self.base_url}/users/{user_id}/tweets"
            params = {
                "max_results": limit,
                "tweet.fields": "created_at,public_metrics",
                "expansions": "referenced_tweets.id"
            }
            
            tweets_response = await client.get(tweets_url, headers=headers, params=params)
            if tweets_response.status_code != 200:
                return {"error": f"Failed to fetch Twitter tweets: {tweets_response.text}"}
            
            return tweets_response.json()
    
    async def get_tweet_replies(self, tweet_id: str, limit: int = 25) -> Dict[str, Any]:
        """Get replies to a tweet"""
        url = f"{self.base_url}/tweets/search/recent"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "query": f"conversation_id:{tweet_id}",
            "max_results": limit,
            "tweet.fields": "created_at,in_reply_to_user_id,author_id"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to fetch tweet replies: {response.text}"}
            
            return response.json()

class YouTubeAPI:
    """Service for interacting with YouTube API"""
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = settings.YOUTUBE_API_KEY
    
    async def get_video_comments(self, video_id: str, limit: int = 25) -> Dict[str, Any]:
        """Get comments from a YouTube video"""
        url = f"{self.base_url}/commentThreads"
        params = {
            "key": self.api_key,
            "videoId": video_id,
            "part": "snippet",
            "maxResults": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to fetch YouTube comments: {response.text}"}
            
            return response.json()
    
    async def search_videos(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for YouTube videos"""
        url = f"{self.base_url}/search"
        params = {
            "key": self.api_key,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"Failed to search YouTube videos: {response.text}"}
            
            return response.json()

# Singleton instances
facebook_api = FacebookAPI()
twitter_api = TwitterAPI()
youtube_api = YouTubeAPI()