# # services/social_media.py
# import requests
# from typing import Dict, Any, List
# import os

# class FacebookAPI:
#     def __init__(self):
#         self.api_version = "v18.0"
#         self.api_url = f"https://graph.facebook.com/{self.api_version}"
#         self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    
#     def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
#         """
#         Get comments for a Facebook post
        
#         Args:
#             post_id (str): The Facebook post ID
#             limit (int): Maximum number of comments to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of comments
#         """
#         endpoint = f"{self.api_url}/{post_id}/comments"
#         params = {
#             "access_token": self.access_token,
#             "limit": limit,
#             "fields": "id,message,created_time,from"
#         }
        
#         response = requests.get(endpoint, params=params)
#         data = response.json()
        
#         if "data" in data:
#             return data["data"]
        
#         return []
    
#     def get_page_posts(self, page_id: str, limit: int = 25) -> List[Dict[str, Any]]:
#         """
#         Get posts from a Facebook page
        
#         Args:
#             page_id (str): The Facebook page ID
#             limit (int): Maximum number of posts to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of posts
#         """
#         endpoint = f"{self.api_url}/{page_id}/posts"
#         params = {
#             "access_token": self.access_token,
#             "limit": limit,
#             "fields": "id,message,created_time,comments.limit(0).summary(true)"
#         }
        
#         response = requests.get(endpoint, params=params)
#         data = response.json()
        
#         if "data" in data:
#             return data["data"]
        
#         return []


# class TwitterAPI:
#     def __init__(self):
#         self.api_url = "https://api.twitter.com/2"
#         self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
#         self.headers = {
#             "Authorization": f"Bearer {self.bearer_token}",
#             "Content-Type": "application/json"
#         }
    
#     def get_tweet_replies(self, tweet_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
#         """
#         Get replies to a tweet
        
#         Args:
#             tweet_id (str): The Tweet ID
#             max_results (int): Maximum number of results to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of replies
#         """
#         # Get conversation ID for the tweet
#         tweet_endpoint = f"{self.api_url}/tweets/{tweet_id}"
#         params = {
#             "tweet.fields": "conversation_id"
#         }
        
#         response = requests.get(tweet_endpoint, headers=self.headers, params=params)
#         tweet_data = response.json()
        
#         if "data" not in tweet_data:
#             return []
        
#         conversation_id = tweet_data["data"].get("conversation_id", tweet_id)
        
#         # Get replies in the conversation
#         search_endpoint = f"{self.api_url}/tweets/search/recent"
#         params = {
#             "query": f"conversation_id:{conversation_id}",
#             "max_results": max_results,
#             "tweet.fields": "created_at,author_id,in_reply_to_user_id"
#         }
        
#         response = requests.get(search_endpoint, headers=self.headers, params=params)
#         data = response.json()
        
#         if "data" in data:
#             return data["data"]
        
#         return []
    
#     def get_user_timeline(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
#         """
#         Get tweets from a user's timeline
        
#         Args:
#             user_id (str): The Twitter user ID
#             max_results (int): Maximum number of tweets to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of tweets
#         """
#         endpoint = f"{self.api_url}/users/{user_id}/tweets"
#         params = {
#             "max_results": max_results,
#             "tweet.fields": "created_at,public_metrics"
#         }
        
#         response = requests.get(endpoint, headers=self.headers, params=params)
#         data = response.json()
        
#         if "data" in data:
#             return data["data"]
        
#         return []


# class YouTubeAPI:
#     def __init__(self):
#         self.api_key = os.getenv("YOUTUBE_API_KEY", "")
#         self.api_url = "https://www.googleapis.com/youtube/v3"
    
#     def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
#         """
#         Get comments for a YouTube video
        
#         Args:
#             video_id (str): The YouTube video ID
#             max_results (int): Maximum number of comments to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of comments
#         """
#         endpoint = f"{self.api_url}/commentThreads"
#         params = {
#             "key": self.api_key,
#             "part": "snippet",
#             "videoId": video_id,
#             "maxResults": min(max_results, 100)  # YouTube API limit is 100 per request
#         }
        
#         comments = []
#         next_page_token = None
        
#         while len(comments) < max_results:
#             if next_page_token:
#                 params["pageToken"] = next_page_token
            
#             response = requests.get(endpoint, params=params)
#             data = response.json()
            
#             if "items" not in data:
#                 break
            
#             for item in data["items"]:
#                 if "snippet" in item and "topLevelComment" in item["snippet"]:
#                     comment = {
#                         "id": item["id"],
#                         "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
#                         "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
#                         "published_at": item["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
#                         "like_count": item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
#                     }
#                     comments.append(comment)
                    
#                     if len(comments) >= max_results:
#                         break
            
#             next_page_token = data.get("nextPageToken")
#             if not next_page_token:
#                 break
        
#         return comments
    
#     def search_videos(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
#         """
#         Search for YouTube videos
        
#         Args:
#             query (str): The search query
#             max_results (int): Maximum number of videos to retrieve
            
#         Returns:
#             List[Dict[str, Any]]: List of videos
#         """
#         endpoint = f"{self.api_url}/search"
#         params = {
#             "key": self.api_key,
#             "part": "snippet",
#             "q": query,
#             "type": "video",
#             "maxResults": min(max_results, 50)  # YouTube API limit is 50 per request
#         }
        
#         response = requests.get(endpoint, params=params)
#         data = response.json()
        
#         if "items" in data:
#             videos = []
#             for item in data["items"]:
#                 video = {
#                     "id": item["id"]["videoId"],
#                     "title": item["snippet"]["title"],
#                     "description": item["snippet"]["description"],
#                     "published_at": item["snippet"]["publishedAt"],
#                     "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
#                 }
#                 videos.append(video)
#             return videos
        
#         return []
# services/social_media.py
import requests
import logging
import time
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from backend.config.settings import settings
from urllib.parse import urlparse

# Thiết lập logging
logger = logging.getLogger("services.social_media")

class SocialMediaBase:
    """Lớp cơ sở cho các API mạng xã hội"""
    
    def __init__(self):
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.last_request_time = 0
        self.min_request_interval = 1  # Tối thiểu 1 giây giữa các requests
    
    def _handle_rate_limit(self):
        """Xử lý rate limiting"""
        # Đảm bảo khoảng thời gian tối thiểu giữa các requests
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        # Kiểm tra rate limit còn lại
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 1:
            # Nếu gần hết rate limit, chờ đến khi reset
            if self.rate_limit_reset is not None:
                sleep_time = max(0, self.rate_limit_reset - current_time)
                if sleep_time > 0:
                    logger.info(f"Đang chờ {sleep_time:.2f} giây để reset rate limit")
                    time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Cập nhật thông tin rate limit từ headers"""
        # Triển khai trong các class con
        pass
    
    def _extract_user_from_url(self, url: str) -> Optional[str]:
        """Trích xuất ID người dùng từ URL"""
        # Triển khai trong các class con
        return None
    
    @staticmethod
    def detect_platform(url: str) -> Optional[str]:
        """
        Phát hiện nền tảng mạng xã hội từ URL
        
        Args:
            url: URL cần kiểm tra
            
        Returns:
            str: Tên nền tảng ('facebook', 'twitter', 'youtube', 'tiktok') hoặc None
        """
        if not url:
            return None
            
        domain = urlparse(url).netloc.lower()
        
        if 'facebook.com' in domain or 'fb.com' in domain or 'fb.watch' in domain:
            return 'facebook'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'tiktok.com' in domain:
            return 'tiktok'
        elif 'instagram.com' in domain:
            return 'instagram'
        
        return None


class FacebookAPI(SocialMediaBase):
    """API tương tác với Facebook Graph API"""
    
    def __init__(self):
        super().__init__()
        self.api_version = "v18.0"
        self.api_url = f"https://graph.facebook.com/{self.api_version}"
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        
        # Tự động lấy access token nếu chưa có
        if not self.access_token and self.app_id and self.app_secret:
            self._get_app_access_token()
    
    def _get_app_access_token(self):
        """Lấy app access token từ app ID và app secret"""
        endpoint = f"{self.api_url}/oauth/access_token"
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if "access_token" in data:
                self.access_token = data["access_token"]
                logger.info("Đã lấy Facebook App Access Token thành công")
            else:
                logger.error(f"Không thể lấy Facebook App Access Token: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Lỗi khi lấy Facebook App Access Token: {str(e)}")
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Cập nhật thông tin rate limit từ headers"""
        usage = headers.get('x-app-usage') or headers.get('x-business-use-case-usage')
        if usage:
            try:
                usage_data = json.loads(usage)
                # Facebook trả về % sử dụng, chuyển thành số lượng còn lại
                call_count = usage_data.get('call_count', 0)
                self.rate_limit_remaining = 100 - call_count
                # Facebook không trả về thời gian reset, ước tính 1 giờ
                self.rate_limit_reset = time.time() + 3600
            except:
                pass
    
    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy bình luận cho một bài đăng Facebook
        
        Args:
            post_id: ID của bài đăng Facebook
            limit: Số lượng bình luận tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách bình luận
        """
        if not self.access_token:
            logger.error("Thiếu Facebook Access Token")
            return []
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/{post_id}/comments"
        params = {
            "access_token": self.access_token,
            "limit": min(limit, 100),  # Facebook API giới hạn 100 item mỗi request
            "fields": "id,message,created_time,from"
        }
        
        comments = []
        next_page = None
        
        try:
            while len(comments) < limit:
                if next_page:
                    response = requests.get(next_page)
                else:
                    response = requests.get(endpoint, params=params)
                
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi Facebook API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                if "data" in data:
                    for comment in data["data"]:
                        comments.append({
                            "id": comment.get("id"),
                            "text": comment.get("message", ""),
                            "created_at": comment.get("created_time"),
                            "author": comment.get("from", {}).get("name") if "from" in comment else None,
                            "author_id": comment.get("from", {}).get("id") if "from" in comment else None,
                            "platform": "facebook",
                            "platform_id": comment.get("id"),
                            "post_id": post_id
                        })
                        
                        if len(comments) >= limit:
                            break
                
                # Kiểm tra trang tiếp theo
                next_page = data.get("paging", {}).get("next")
                if not next_page:
                    break
        except Exception as e:
            logger.error(f"Lỗi khi lấy bình luận Facebook: {str(e)}")
        
        return comments
    
    def get_page_posts(self, page_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Lấy bài đăng từ một trang Facebook
        
        Args:
            page_id: ID của trang Facebook
            limit: Số lượng bài đăng tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách bài đăng
        """
        if not self.access_token:
            logger.error("Thiếu Facebook Access Token")
            return []
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/{page_id}/posts"
        params = {
            "access_token": self.access_token,
            "limit": min(limit, 50),  # Facebook API giới hạn 50 item mỗi request
            "fields": "id,message,created_time,permalink_url,comments.limit(0).summary(true)"
        }
        
        posts = []
        next_page = None
        
        try:
            while len(posts) < limit:
                if next_page:
                    response = requests.get(next_page)
                else:
                    response = requests.get(endpoint, params=params)
                
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi Facebook API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                if "data" in data:
                    for post in data["data"]:
                        posts.append({
                            "id": post.get("id"),
                            "text": post.get("message", ""),
                            "created_at": post.get("created_time"),
                            "url": post.get("permalink_url"),
                            "comment_count": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                            "platform": "facebook",
                            "platform_id": post.get("id")
                        })
                        
                        if len(posts) >= limit:
                            break
                
                # Kiểm tra trang tiếp theo
                next_page = data.get("paging", {}).get("next")
                if not next_page:
                    break
        except Exception as e:
            logger.error(f"Lỗi khi lấy bài đăng Facebook: {str(e)}")
        
        return posts
    
    def get_comments_from_url(self, url: str, limit: int = 100) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Lấy bình luận từ URL Facebook
        
        Args:
            url: URL của bài đăng Facebook
            limit: Số lượng bình luận tối đa cần lấy
            
        Returns:
            Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: (Danh sách bình luận, thông tin bài đăng)
        """
        # Trích xuất ID bài đăng từ URL
        post_id = self._extract_post_id_from_url(url)
        if not post_id:
            logger.error(f"Không thể trích xuất ID bài đăng từ URL: {url}")
            return [], None
        
        # Lấy thông tin bài đăng
        post_info = self._get_post_info(post_id)
        
        # Lấy bình luận
        comments = self.get_post_comments(post_id, limit)
        
        return comments, post_info
    
    def _extract_post_id_from_url(self, url: str) -> Optional[str]:
        """
        Trích xuất ID bài đăng từ URL Facebook
        
        Args:
            url: URL của bài đăng Facebook
            
        Returns:
            Optional[str]: ID bài đăng hoặc None nếu không thể trích xuất
        """
        # Các pattern URL Facebook phổ biến
        patterns = [
            r'facebook\.com\/[^\/]+\/posts\/(\d+)',                # facebook.com/username/posts/123456
            r'facebook\.com\/[^\/]+\/photos\/[^\/]+\/(\d+)',       # facebook.com/username/photos/a.123/123456
            r'facebook\.com\/permalink\.php\?story_fbid=(\d+)',    # facebook.com/permalink.php?story_fbid=123456
            r'facebook\.com\/photo\.php\?fbid=(\d+)',              # facebook.com/photo.php?fbid=123456
            r'facebook\.com\/[^\/]+\/videos\/(\d+)',               # facebook.com/username/videos/123456
            r'facebook\.com\/watch\/\?v=(\d+)'                     # facebook.com/watch/?v=123456
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _get_post_info(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin bài đăng Facebook
        
        Args:
            post_id: ID của bài đăng Facebook
            
        Returns:
            Optional[Dict[str, Any]]: Thông tin bài đăng hoặc None nếu không thể lấy
        """
        if not self.access_token:
            logger.error("Thiếu Facebook Access Token")
            return None
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/{post_id}"
        params = {
            "access_token": self.access_token,
            "fields": "id,message,created_time,permalink_url,from"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            self._update_rate_limit(response.headers)
            
            if response.status_code != 200:
                logger.error(f"Lỗi Facebook API: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            return {
                "id": data.get("id"),
                "text": data.get("message", ""),
                "created_at": data.get("created_time"),
                "url": data.get("permalink_url"),
                "author": data.get("from", {}).get("name") if "from" in data else None,
                "author_id": data.get("from", {}).get("id") if "from" in data else None,
                "platform": "facebook",
                "platform_id": data.get("id")
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin bài đăng Facebook: {str(e)}")
        
        return None


class TwitterAPI(SocialMediaBase):
    """API tương tác với Twitter API v2"""
    
    def __init__(self):
        super().__init__()
        self.api_url = "https://api.twitter.com/2"
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        
        # Xác định loại token để sử dụng
        if self.bearer_token:
            self.headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
        elif self.api_key and self.api_secret:
            self._get_bearer_token()
    
    def _get_bearer_token(self):
        """Lấy bearer token từ API key và secret"""
        token_url = "https://api.twitter.com/oauth2/token"
        auth = (self.api_key, self.api_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        
        try:
            response = requests.post(token_url, auth=auth, data=data, headers=headers)
            token_data = response.json()
            
            if "access_token" in token_data:
                self.bearer_token = token_data["access_token"]
                self.headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "Content-Type": "application/json"
                }
                logger.info("Đã lấy Twitter Bearer Token thành công")
            else:
                logger.error(f"Không thể lấy Twitter Bearer Token: {token_data}")
        except Exception as e:
            logger.error(f"Lỗi khi lấy Twitter Bearer Token: {str(e)}")
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Cập nhật thông tin rate limit từ headers"""
        self.rate_limit_remaining = int(headers.get('x-rate-limit-remaining', 0))
        reset_time = int(headers.get('x-rate-limit-reset', 0))
        if reset_time:
            self.rate_limit_reset = reset_time
    
    def get_tweet_replies(self, tweet_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy các phản hồi cho một tweet
        
        Args:
            tweet_id: ID của tweet
            max_results: Số lượng phản hồi tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách phản hồi
        """
        if not self.bearer_token:
            logger.error("Thiếu Twitter Bearer Token")
            return []
            
        self._handle_rate_limit()
        
        # Lấy conversation ID cho tweet
        tweet_endpoint = f"{self.api_url}/tweets/{tweet_id}"
        params = {
            "tweet.fields": "conversation_id,author_id,created_at"
        }
        
        try:
            response = requests.get(tweet_endpoint, headers=self.headers, params=params)
            self._update_rate_limit(response.headers)
            
            if response.status_code != 200:
                logger.error(f"Lỗi Twitter API: {response.status_code} - {response.text}")
                return []
                
            tweet_data = response.json()
            
            if "data" not in tweet_data:
                logger.error(f"Không tìm thấy tweet: {tweet_id}")
                return []
            
            original_tweet = tweet_data["data"]
            conversation_id = original_tweet.get("conversation_id", tweet_id)
            
            # Lấy các phản hồi trong conversation
            search_endpoint = f"{self.api_url}/tweets/search/recent"
            params = {
                "query": f"conversation_id:{conversation_id}",
                "max_results": min(max_results, 100),  # Twitter API giới hạn 100 item mỗi request
                "tweet.fields": "created_at,author_id,in_reply_to_user_id,text",
                "expansions": "author_id"
            }
            
            replies = []
            next_token = None
            
            while len(replies) < max_results:
                if next_token:
                    params["next_token"] = next_token
                
                response = requests.get(search_endpoint, headers=self.headers, params=params)
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi Twitter API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                # Lấy thông tin user
                users = {}
                if "includes" in data and "users" in data["includes"]:
                    for user in data["includes"]["users"]:
                        users[user["id"]] = user["username"]
                
                if "data" in data:
                    for tweet in data["data"]:
                        # Bỏ qua tweet gốc
                        if tweet["id"] == tweet_id:
                            continue
                            
                        # Lấy username từ author_id
                        username = users.get(tweet.get("author_id"), None)
                        
                        replies.append({
                            "id": tweet.get("id"),
                            "text": tweet.get("text", ""),
                            "created_at": tweet.get("created_at"),
                            "author_id": tweet.get("author_id"),
                            "author": username,
                            "platform": "twitter",
                            "platform_id": tweet.get("id"),
                            "in_reply_to": tweet.get("in_reply_to_user_id"),
                            "conversation_id": conversation_id
                        })
                        
                        if len(replies) >= max_results:
                            break
                
                # Kiểm tra trang tiếp theo
                next_token = data.get("meta", {}).get("next_token")
                if not next_token:
                    break
                    
                # Thêm thời gian chờ để tránh rate limit
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy phản hồi Twitter: {str(e)}")
        
        return replies
    
    def get_user_timeline(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy tweets từ timeline của một người dùng
        
        Args:
            user_id: ID của người dùng Twitter
            max_results: Số lượng tweet tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách tweet
        """
        if not self.bearer_token:
            logger.error("Thiếu Twitter Bearer Token")
            return []
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/admin/users/{user_id}/tweets"
        params = {
            "max_results": min(max_results, 100),  # Twitter API giới hạn 100 item mỗi request
            "tweet.fields": "created_at,public_metrics,conversation_id",
            "exclude": "retweets,replies"
        }
        
        tweets = []
        next_token = None
        
        try:
            while len(tweets) < max_results:
                if next_token:
                    params["pagination_token"] = next_token
                
                response = requests.get(endpoint, headers=self.headers, params=params)
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi Twitter API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                if "data" in data:
                    for tweet in data["data"]:
                        metrics = tweet.get("public_metrics", {})
                        
                        tweets.append({
                            "id": tweet.get("id"),
                            "text": tweet.get("text", ""),
                            "created_at": tweet.get("created_at"),
                            "like_count": metrics.get("like_count", 0),
                            "retweet_count": metrics.get("retweet_count", 0),
                            "reply_count": metrics.get("reply_count", 0),
                            "quote_count": metrics.get("quote_count", 0),
                            "conversation_id": tweet.get("conversation_id"),
                            "platform": "twitter",
                            "platform_id": tweet.get("id"),
                            "author_id": user_id
                        })
                        
                        if len(tweets) >= max_results:
                            break
                
                # Kiểm tra trang tiếp theo
                next_token = data.get("meta", {}).get("next_token")
                if not next_token:
                    break
                    
                # Thêm thời gian chờ để tránh rate limit
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy timeline Twitter: {str(e)}")
        
        return tweets
    
    def get_tweets_from_url(self, url: str, include_replies: bool = True, max_results: int = 100) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Lấy tweet và phản hồi từ URL
        
        Args:
            url: URL của tweet
            include_replies: Có bao gồm phản hồi hay không
            max_results: Số lượng phản hồi tối đa cần lấy
            
        Returns:
            Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: (Danh sách phản hồi, thông tin tweet)
        """
        # Trích xuất ID tweet từ URL
        tweet_id = self._extract_tweet_id_from_url(url)
        if not tweet_id:
            logger.error(f"Không thể trích xuất ID tweet từ URL: {url}")
            return [], None
        
        # Lấy thông tin tweet
        tweet_endpoint = f"{self.api_url}/tweets/{tweet_id}"
        params = {
            "tweet.fields": "created_at,author_id,conversation_id,public_metrics",
            "expansions": "author_id"
        }
        
        tweet_info = None
        replies = []
        
        try:
            self._handle_rate_limit()
            response = requests.get(tweet_endpoint, headers=self.headers, params=params)
            self._update_rate_limit(response.headers)
            
            if response.status_code != 200:
                logger.error(f"Lỗi Twitter API: {response.status_code} - {response.text}")
                return replies, tweet_info
                
            data = response.json()
            
            if "data" in data:
                tweet = data["data"]
                metrics = tweet.get("public_metrics", {})
                
                # Lấy username từ author_id
                username = None
                if "includes" in data and "users" in data["includes"]:
                    for user in data["includes"]["users"]:
                        if user["id"] == tweet.get("author_id"):
                            username = user["username"]
                            break
                
                tweet_info = {
                    "id": tweet.get("id"),
                    "text": tweet.get("text", ""),
                    "created_at": tweet.get("created_at"),
                    "author_id": tweet.get("author_id"),
                    "author": username,
                    "like_count": metrics.get("like_count", 0),
                    "retweet_count": metrics.get("retweet_count", 0),
                    "reply_count": metrics.get("reply_count", 0),
                    "platform": "twitter",
                    "platform_id": tweet.get("id"),
                    "url": url
                }
            
            # Lấy phản hồi nếu yêu cầu
            if include_replies:
                replies = self.get_tweet_replies(tweet_id, max_results)
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy tweet từ URL: {str(e)}")
        
        return replies, tweet_info
    
    def _extract_tweet_id_from_url(self, url: str) -> Optional[str]:
        """
        Trích xuất ID tweet từ URL Twitter
        
        Args:
            url: URL của tweet
            
        Returns:
            Optional[str]: ID tweet hoặc None nếu không thể trích xuất
        """
        # Các pattern URL Twitter phổ biến
        patterns = [
            r'twitter\.com\/[^\/]+\/status\/(\d+)',  # twitter.com/username/status/123456
            r'x\.com\/[^\/]+\/status\/(\d+)'         # x.com/username/status/123456
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


class YouTubeAPI(SocialMediaBase):
    """API tương tác với YouTube Data API v3"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.YOUTUBE_API_KEY
        self.api_url = "https://www.googleapis.com/youtube/v3"
        self.min_request_interval = 0.5  # YouTube API có thể xử lý nhiều request hơn
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Cập nhật thông tin rate limit từ headers"""
        # YouTube sử dụng quota thay vì rate limit thông thường
        # Chúng ta không thể biết được quota còn lại từ headers
        pass
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy bình luận cho một video YouTube
        
        Args:
            video_id: ID của video YouTube
            max_results: Số lượng bình luận tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách bình luận
        """
        if not self.api_key:
            logger.error("Thiếu YouTube API Key")
            return []
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/commentThreads"
        params = {
            "key": self.api_key,
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": min(max_results, 100)  # YouTube API giới hạn 100 item mỗi request
        }
        
        comments = []
        next_page_token = None
        
        try:
            while len(comments) < max_results:
                if next_page_token:
                    params["pageToken"] = next_page_token
                
                response = requests.get(endpoint, params=params)
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi YouTube API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                if "items" not in data:
                    break
                
                for item in data["items"]:
                    if "snippet" in item and "topLevelComment" in item["snippet"]:
                        comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                        
                        comment = {
                            "id": item["id"],
                            "text": comment_snippet.get("textDisplay", ""),
                            "textOriginal": comment_snippet.get("textOriginal", ""),
                            "author": comment_snippet.get("authorDisplayName"),
                            "author_id": comment_snippet.get("authorChannelId", {}).get("value") if "authorChannelId" in comment_snippet else None,
                            "author_profile": comment_snippet.get("authorProfileImageUrl"),
                            "published_at": comment_snippet.get("publishedAt"),
                            "updated_at": comment_snippet.get("updatedAt"),
                            "like_count": comment_snippet.get("likeCount", 0),
                            "platform": "youtube",
                            "platform_id": item["id"],
                            "video_id": video_id
                        }
                        comments.append(comment)
                        
                        # Lấy cả replies nếu có
                        if "replies" in item and "comments" in item["replies"]:
                            for reply in item["replies"]["comments"]:
                                if "snippet" in reply:
                                    reply_snippet = reply["snippet"]
                                    
                                    reply_comment = {
                                        "id": reply["id"],
                                        "text": reply_snippet.get("textDisplay", ""),
                                        "textOriginal": reply_snippet.get("textOriginal", ""),
                                        "author": reply_snippet.get("authorDisplayName"),
                                        "author_id": reply_snippet.get("authorChannelId", {}).get("value") if "authorChannelId" in reply_snippet else None,
                                        "author_profile": reply_snippet.get("authorProfileImageUrl"),
                                        "published_at": reply_snippet.get("publishedAt"),
                                        "updated_at": reply_snippet.get("updatedAt"),
                                        "like_count": reply_snippet.get("likeCount", 0),
                                        "platform": "youtube",
                                        "platform_id": reply["id"],
                                        "video_id": video_id,
                                        "parent_id": item["id"]
                                    }
                                    comments.append(reply_comment)
                        
                        if len(comments) >= max_results:
                            break
                
                # Kiểm tra trang tiếp theo
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
                    
                # Thêm thời gian chờ để tránh quota limit
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Lỗi khi lấy bình luận YouTube: {str(e)}")
        
        return comments
    
    def search_videos(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Tìm kiếm video YouTube
        
        Args:
            query: Từ khóa tìm kiếm
            max_results: Số lượng video tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách video
        """
        if not self.api_key:
            logger.error("Thiếu YouTube API Key")
            return []
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/search"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),  # YouTube API giới hạn 50 item mỗi request
            "relevanceLanguage": "vi"  # Ưu tiên kết quả tiếng Việt
        }
        
        videos = []
        next_page_token = None
        
        try:
            while len(videos) < max_results:
                if next_page_token:
                    params["pageToken"] = next_page_token
                
                response = requests.get(endpoint, params=params)
                self._update_rate_limit(response.headers)
                
                if response.status_code != 200:
                    logger.error(f"Lỗi YouTube API: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                if "items" in data:
                    for item in data["items"]:
                        video = {
                            "id": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"],
                            "published_at": item["snippet"]["publishedAt"],
                            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                            "channel_title": item["snippet"]["channelTitle"],
                            "channel_id": item["snippet"]["channelId"],
                            "platform": "youtube",
                            "platform_id": item["id"]["videoId"],
                            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                        }
                        videos.append(video)
                        
                        if len(videos) >= max_results:
                            break
                
                # Kiểm tra trang tiếp theo
                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
                    
                # Thêm thời gian chờ để tránh quota limit
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm video YouTube: {str(e)}")
        
        return videos
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin của một video YouTube
        
        Args:
            video_id: ID của video YouTube
            
        Returns:
            Optional[Dict[str, Any]]: Thông tin video hoặc None nếu không thể lấy
        """
        if not self.api_key:
            logger.error("Thiếu YouTube API Key")
            return None
            
        self._handle_rate_limit()
        
        endpoint = f"{self.api_url}/videos"
        params = {
            "key": self.api_key,
            "part": "snippet,statistics,contentDetails",
            "id": video_id
        }
        
        try:
            response = requests.get(endpoint, params=params)
            self._update_rate_limit(response.headers)
            
            if response.status_code != 200:
                logger.error(f"Lỗi YouTube API: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                item = data["items"][0]
                snippet = item["snippet"]
                statistics = item["statistics"]
                content_details = item["contentDetails"]
                
                # Chuyển đổi định dạng thời lượng ISO 8601 thành số giây
                duration = content_details.get("duration", "PT0S")  # Mặc định là 0 giây
                duration_seconds = self._parse_duration(duration)
                
                return {
                    "id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt"),
                    "channel_title": snippet.get("channelTitle"),
                    "channel_id": snippet.get("channelId"),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "tags": snippet.get("tags", []),
                    "category_id": snippet.get("categoryId"),
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "duration": duration_seconds,
                    "duration_formatted": duration,
                    "platform": "youtube",
                    "platform_id": item["id"],
                    "url": f"https://www.youtube.com/watch?v={item['id']}"
                }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video YouTube: {str(e)}")
        
        return None
    
    def get_comments_from_url(self, url: str, max_results: int = 100) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Lấy bình luận từ URL YouTube
        
        Args:
            url: URL của video YouTube
            max_results: Số lượng bình luận tối đa cần lấy
            
        Returns:
            Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: (Danh sách bình luận, thông tin video)
        """
        # Trích xuất ID video từ URL
        video_id = self._extract_video_id_from_url(url)
        if not video_id:
            logger.error(f"Không thể trích xuất ID video từ URL: {url}")
            return [], None
        
        # Lấy thông tin video
        video_info = self.get_video_info(video_id)
        
        # Lấy bình luận
        comments = self.get_video_comments(video_id, max_results)
        
        return comments, video_info
    
    def _extract_video_id_from_url(self, url: str) -> Optional[str]:
        """
        Trích xuất ID video từ URL YouTube
        
        Args:
            url: URL của video YouTube
            
        Returns:
            Optional[str]: ID video hoặc None nếu không thể trích xuất
        """
        # Các pattern URL YouTube phổ biến
        patterns = [
            r'youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',  # youtube.com/watch?v=abc123
            r'youtu\.be\/([a-zA-Z0-9_-]+)',              # youtu.be/abc123
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)',    # youtube.com/embed/abc123
            r'youtube\.com\/v\/([a-zA-Z0-9_-]+)'         # youtube.com/v/abc123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Chuyển đổi định dạng thời lượng ISO 8601 thành số giây
        
        Args:
            duration_str: Chuỗi thời lượng theo định dạng ISO 8601
            
        Returns:
            int: Thời lượng theo giây
        """
        # Ví dụ: PT1H30M15S -> 1 giờ 30 phút 15 giây
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)
        
        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0
        
        return hours * 3600 + minutes * 60 + seconds


class TikTokAPI(SocialMediaBase):
    """API tương tác với TikTok không chính thức (do TikTok không có API chính thức)"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.TIKTOK_API_KEY
        # Vì TikTok không có API chính thức, chúng ta có thể sử dụng một API thứ ba
        self.api_url = "https://tiktok-scraper-api.example.com"  # API ví dụ
        self.min_request_interval = 2  # Thời gian giữa các request dài hơn để tránh bị chặn
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy bình luận cho một video TikTok
        
        Args:
            video_id: ID của video TikTok
            max_results: Số lượng bình luận tối đa cần lấy
            
        Returns:
            List[Dict[str, Any]]: Danh sách bình luận
        """
        # Phương thức này sẽ phụ thuộc vào API thứ ba hoặc phương pháp scraping
        # Do TikTok không có API chính thức
        logger.warning("TikTok API không được triển khai chính thức")
        return []
    
    def get_comments_from_url(self, url: str, max_results: int = 100) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Lấy bình luận từ URL TikTok
        
        Args:
            url: URL của video TikTok
            max_results: Số lượng bình luận tối đa cần lấy
            
        Returns:
            Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: (Danh sách bình luận, thông tin video)
        """
        # Trích xuất ID video từ URL
        video_id = self._extract_video_id_from_url(url)
        if not video_id:
            logger.error(f"Không thể trích xuất ID video từ URL: {url}")
            return [], None
        
        # Lấy bình luận
        comments = self.get_video_comments(video_id, max_results)
        
        return comments, None
    
    def _extract_video_id_from_url(self, url: str) -> Optional[str]:
        """
        Trích xuất ID video từ URL TikTok
        
        Args:
            url: URL của video TikTok
            
        Returns:
            Optional[str]: ID video hoặc None nếu không thể trích xuất
        """
        # Các pattern URL TikTok phổ biến
        patterns = [
            r'tiktok\.com\/@[^\/]+\/video\/(\d+)',  # tiktok.com/@username/video/1234567890
            r'vm\.tiktok\.com\/([a-zA-Z0-9]+)'      # vm.tiktok.com/abc123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


# Factory cho social media APIs
def get_social_media_api(platform: str) -> SocialMediaBase:
    """
    Factory method để lấy instance API tương ứng với nền tảng
    
    Args:
        platform: Tên nền tảng ('facebook', 'twitter', 'youtube', 'tiktok')
        
    Returns:
        SocialMediaBase: API instance cho nền tảng tương ứng
    """
    platform = platform.lower()
    
    if platform == 'facebook':
        return FacebookAPI()
    elif platform == 'twitter':
        return TwitterAPI()
    elif platform == 'youtube':
        return YouTubeAPI()
    elif platform == 'tiktok':
        return TikTokAPI()
    else:
        logger.warning(f"Không hỗ trợ nền tảng: {platform}")
        raise ValueError(f"Không hỗ trợ nền tảng: {platform}")

def get_comments_from_url(url: str, max_results: int = 100) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Hàm tiện ích để lấy bình luận từ URL bất kỳ
    
    Args:
        url: URL của bài đăng/video từ bất kỳ nền tảng nào
        max_results: Số lượng bình luận tối đa cần lấy
        
    Returns:
        Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: (Danh sách bình luận, thông tin bài đăng)
    """
    # Phát hiện nền tảng từ URL
    platform = SocialMediaBase.detect_platform(url)
    if not platform:
        logger.error(f"Không thể phát hiện nền tảng từ URL: {url}")
        return [], None
    
    try:
        # Lấy API tương ứng
        api = get_social_media_api(platform)
        
        # Lấy bình luận
        return api.get_comments_from_url(url, max_results)
    except Exception as e:
        logger.error(f"Lỗi khi lấy bình luận từ {url}: {str(e)}")
        return [], None