import pytest
from unittest.mock import patch, mock_open
from src.auth_module import authenticate_user, load_user_data, save_user_data, UserNotFoundError, InvalidCredentialsError

class TestAuthModule:
    def test_successful_authentication(self):
        """测试成功认证用户"""
        mock_user_data = {
            "test_user": {
                "password": "hashed_password_123",
                "name": "测试用户"
            }
        }
        
        with patch('src.auth_module.load_user_data', return_value=mock_user_data):
            result = authenticate_user("test_user", "password_123")
            assert result is True

    def test_user_not_found(self):
        """测试用户不存在的情况"""
        mock_user_data = {"existing_user": {"password": "pass", "name": "用户"}}
        
        with patch('src.auth_module.load_user_data', return_value=mock_user_data):
            with pytest.raises(UserNotFoundError):
                authenticate_user("nonexistent_user", "password")

    def test_invalid_password(self):
        """测试密码错误的情况"""
        mock_user_data = {
            "test_user": {
                "password": "correct_hash",
                "name": "测试用户"
            }
        }
        
        with patch('src.auth_module.load_user_data', return_value=mock_user_data):
            with pytest.raises(InvalidCredentialsError):
                authenticate_user("test_user", "wrong_password")

    def test_empty_username_or_password(self):
        """测试空用户名或密码"""
        with pytest.raises(ValueError):
            authenticate_user("", "password")
        
        with pytest.raises(ValueError):
            authenticate_user("user", "")

    def test_load_user_data_success(self):
        """测试成功加载用户数据"""
        mock_json_data = '{"user1": {"password": "pass1", "name": "用户1"}}'
        
        with patch('builtins.open', mock_open(read_data=mock_json_data)):
            with patch('os.path.exists', return_value=True):
                result = load_user_data()
                assert "user1" in result
                assert result["user1"]["name"] == "用户1"

    def test_load_user_data_file_not_found(self):
        """测试用户数据文件不存在"""
        with patch('os.path.exists', return_value=False):
            result = load_user_data()
            assert result == {}

    def test_load_user_data_invalid_json(self):
        """测试无效的JSON格式"""
        invalid_json = '{invalid json}'
        
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with patch('os.path.exists', return_value=True):
                result = load_user_data()
                assert result == {}

    def test_save_user_data_success(self):
        """测试成功保存用户数据"""
        test_data = {"user1": {"password": "pass1", "name": "用户1"}}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json:
                save_user_data(test_data)
                mock_json.assert_called_once()

    def test_save_user_data_error(self):
        """测试保存用户数据时的错误处理"""
        test_data = {"user1": {"password": "pass1"}}
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                save_user_data(test_data)