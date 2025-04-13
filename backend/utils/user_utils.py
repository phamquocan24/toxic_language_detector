"""
Utility functions cho User objects
"""

def prepare_user_response(user):
    """
    Chuẩn bị đối tượng User cho response, chuyển đổi role thành string
    
    Args:
        user: Đối tượng User từ database
        
    Returns:
        dict: Dictionary chứa thông tin user với role dạng string
    """
    # Đảm bảo role là string
    if user.role and hasattr(user.role, 'name'):
        user_dict = user.__dict__.copy()
        user_dict['role'] = user.role.name
        return user_dict
    return user 