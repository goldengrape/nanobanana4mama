import json
import os
from typing import Dict, Any

class UserNotFoundError(Exception):
    """用户不存在异常"""
    pass

class InvalidCredentialsError(Exception):
    """无效凭据异常"""
    pass

def authenticate_user(username: str, password: str) -> bool:
    """
    验证用户凭据
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        bool: 认证成功返回True
    
    Raises:
        ValueError: 用户名或密码为空
        UserNotFoundError: 用户不存在
        InvalidCredentialsError: 密码错误
    """
    if not username or not password:
        raise ValueError("用户名和密码不能为空")
    
    user_data = load_user_data()
    
    if username not in user_data:
        raise UserNotFoundError(f"用户 '{username}' 不存在")
    
    stored_password = user_data[username].get("password", "")
    
    # 简单验证（实际应用中应使用哈希比较）
    if password != stored_password:
        raise InvalidCredentialsError("密码错误")
    
    return True

def load_user_data() -> Dict[str, Any]:
    """
    从JSON文件加载用户数据
    
    Returns:
        Dict[str, Any]: 用户数据字典
    """
    user_data_file = os.path.join("data", "users.json")
    
    if not os.path.exists(user_data_file):
        return {}
    
    try:
        with open(user_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_user_data(user_data: Dict[str, Any]) -> None:
    """
    保存用户数据到JSON文件
    
    Args:
        user_data: 用户数据字典
    
    Raises:
        IOError: 保存失败时抛出
    """
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    user_data_file = os.path.join("data", "users.json")
    
    try:
        with open(user_data_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        raise IOError(f"无法保存用户数据: {str(e)}")