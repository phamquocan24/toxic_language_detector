# Tạo file backend/utils/user_utils.py

from typing import Dict, Any, Union, List
from backend.db.models import User

def prepare_user_response(user: User) -> Dict[str, Any]:
    """
    Chuẩn bị đối tượng User cho response, chuyển đổi role thành string
    
    Args:
        user: Đối tượng User
        
    Returns:
        Dict[str, Any]: Dictionary biểu diễn user với role là string
    """
    if user is None:
        return None
        
    # Tạo dict từ object user
    if hasattr(user, "__dict__"):
        user_dict = user.__dict__.copy()
    else:
        # Nếu không có __dict__, thử chuyển đổi theo cách khác
        user_dict = {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "email": getattr(user, "email", None),
            "name": getattr(user, "name", None),
            "is_active": getattr(user, "is_active", True),
            "last_login": getattr(user, "last_login", None),
            "created_at": getattr(user, "created_at", None),
            "updated_at": getattr(user, "updated_at", None),
        }
    
    # Xử lý role
    role = getattr(user, "role", None)
    if role and hasattr(role, "name"):
        user_dict["role"] = role.name
    elif "role" in user_dict and hasattr(user_dict["role"], "name"):
        user_dict["role"] = user_dict["role"].name
    
    # Loại bỏ các thuộc tính không mong muốn trong response
    keys_to_remove = ["_sa_instance_state", "hashed_password", "reset_token", 
                      "reset_token_expires", "verification_token", 
                      "verification_token_expires"]
    for key in keys_to_remove:
        if key in user_dict:
            del user_dict[key]
    
    return user_dict

def prepare_users_response(users: List[User]) -> List[Dict[str, Any]]:
    """
    Chuẩn bị danh sách User cho response
    
    Args:
        users: Danh sách đối tượng User
        
    Returns:
        List[Dict[str, Any]]: Danh sách dictionary biểu diễn user với role là string
    """
    return [prepare_user_response(user) for user in users]