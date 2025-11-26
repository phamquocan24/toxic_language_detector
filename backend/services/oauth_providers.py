"""
OAuth2 Providers Support

Provides base classes and implementations for OAuth2 authentication.
Ready for integration with Google, Facebook, GitHub, etc.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


class OAuth2Provider(ABC):
    """
    Base class for OAuth2 providers
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    @abstractmethod
    def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL"""
        pass
    
    @abstractmethod
    async def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from provider"""
        pass
    
    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """Refresh access token (if supported)"""
        return None


class GoogleOAuth2Provider(OAuth2Provider):
    """
    Google OAuth2 Provider
    
    Setup:
        1. Go to https://console.cloud.google.com/
        2. Create OAuth2 credentials
        3. Set redirect URI
        4. Get client_id and client_secret
    """
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get Google authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query}"
    
    async def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "grant_type": "authorization_code"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Token exchange error: {e}")
                return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user info from Google"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "id": data.get("id"),
                        "email": data.get("email"),
                        "name": data.get("name"),
                        "picture": data.get("picture"),
                        "verified_email": data.get("verified_email")
                    }
                else:
                    logger.error(f"User info fetch failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"User info fetch error: {e}")
                return None


class GitHubOAuth2Provider(OAuth2Provider):
    """
    GitHub OAuth2 Provider
    
    Setup:
        1. Go to https://github.com/settings/developers
        2. Create OAuth App
        3. Set callback URL
        4. Get client_id and client_secret
    """
    
    AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USERINFO_URL = "https://api.github.com/user"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get GitHub authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
            "allow_signup": "true"
        }
        
        if state:
            params["state"] = state
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query}"
    
    async def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Token exchange error: {e}")
                return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user info from GitHub"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "id": str(data.get("id")),
                        "email": data.get("email"),
                        "name": data.get("name") or data.get("login"),
                        "avatar": data.get("avatar_url"),
                        "username": data.get("login")
                    }
                else:
                    logger.error(f"User info fetch failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"User info fetch error: {e}")
                return None


class FacebookOAuth2Provider(OAuth2Provider):
    """
    Facebook OAuth2 Provider
    
    Setup:
        1. Go to https://developers.facebook.com/
        2. Create App
        3. Setup Facebook Login
        4. Get app_id and app_secret
    """
    
    AUTHORIZATION_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    USERINFO_URL = "https://graph.facebook.com/v18.0/me"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get Facebook authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email public_profile",
            "response_type": "code"
        }
        
        if state:
            params["state"] = state
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query}"
    
    async def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.TOKEN_URL,
                    params={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Token exchange error: {e}")
                return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user info from Facebook"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USERINFO_URL,
                    params={
                        "fields": "id,name,email,picture",
                        "access_token": access_token
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "id": data.get("id"),
                        "email": data.get("email"),
                        "name": data.get("name"),
                        "picture": data.get("picture", {}).get("data", {}).get("url")
                    }
                else:
                    logger.error(f"User info fetch failed: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"User info fetch error: {e}")
                return None


class OAuth2Manager:
    """
    Manager for multiple OAuth2 providers
    """
    
    def __init__(self):
        self.providers: Dict[str, OAuth2Provider] = {}
    
    def register_provider(self, name: str, provider: OAuth2Provider):
        """Register an OAuth2 provider"""
        self.providers[name] = provider
        logger.info(f"Registered OAuth2 provider: {name}")
    
    def get_provider(self, name: str) -> Optional[OAuth2Provider]:
        """Get OAuth2 provider by name"""
        return self.providers.get(name)
    
    def get_authorization_url(
        self,
        provider_name: str,
        state: str = None
    ) -> Optional[str]:
        """Get authorization URL for provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_authorization_url(state)
        return None
    
    async def authenticate(
        self,
        provider_name: str,
        code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user via OAuth2 provider
        
        Returns:
            User info dict or None
        """
        provider = self.get_provider(provider_name)
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return None
        
        # Exchange code for token
        token_data = await provider.get_access_token(code)
        if not token_data:
            return None
        
        access_token = token_data.get("access_token")
        if not access_token:
            return None
        
        # Get user info
        user_info = await provider.get_user_info(access_token)
        if user_info:
            user_info["provider"] = provider_name
            user_info["access_token"] = access_token
            user_info["refresh_token"] = token_data.get("refresh_token")
        
        return user_info


# Global OAuth manager
_oauth_manager: Optional[OAuth2Manager] = None


def get_oauth_manager() -> OAuth2Manager:
    """Get OAuth2 manager singleton"""
    global _oauth_manager
    
    if _oauth_manager is None:
        from backend.config.settings import settings
        
        _oauth_manager = OAuth2Manager()
        
        # Register Google provider if configured
        if hasattr(settings, 'GOOGLE_CLIENT_ID') and settings.GOOGLE_CLIENT_ID:
            google = GoogleOAuth2Provider(
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=f"{settings.BACKEND_URL}/api/auth/oauth/google/callback"
            )
            _oauth_manager.register_provider("google", google)
        
        # Register GitHub provider if configured
        if hasattr(settings, 'GITHUB_CLIENT_ID') and settings.GITHUB_CLIENT_ID:
            github = GitHubOAuth2Provider(
                client_id=settings.GITHUB_CLIENT_ID,
                client_secret=settings.GITHUB_CLIENT_SECRET,
                redirect_uri=f"{settings.BACKEND_URL}/api/auth/oauth/github/callback"
            )
            _oauth_manager.register_provider("github", github)
        
        # Register Facebook provider if configured
        if hasattr(settings, 'FACEBOOK_CLIENT_ID') and settings.FACEBOOK_CLIENT_ID:
            facebook = FacebookOAuth2Provider(
                client_id=settings.FACEBOOK_CLIENT_ID,
                client_secret=settings.FACEBOOK_CLIENT_SECRET,
                redirect_uri=f"{settings.BACKEND_URL}/api/auth/oauth/facebook/callback"
            )
            _oauth_manager.register_provider("facebook", facebook)
    
    return _oauth_manager

