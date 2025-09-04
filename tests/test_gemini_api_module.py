import base64
from io import BytesIO
from unittest.mock import Mock, patch
import pytest
from PIL import Image
from src.gemini_api_module import generate_image_from_conversation, APIError, NetworkError

class TestGenerateImageFromConversation:
    def test_successful_image_generation(self, mocker):
        conversation_history = [{"role": "user", "content": "画一只可爱的小猫"}]
        mock_image = Image.new('RGB', (100, 100), color='red')
        buffered = BytesIO()
        mock_image.save(buffered, format="PNG")
        mock_image_data = base64.b64encode(buffered.getvalue()).decode()
        
        mock_response = Mock()
        mock_response.text = f"![generated_image](data:image/png;base64,{mock_image_data})"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        mock_client = Mock()
        mock_client.GenerativeModel.return_value = mock_model
        
        with patch('src.gemini_api_module.genai', mock_client):
            result = generate_image_from_conversation(conversation_history, api_key="test_key")
            assert isinstance(result, Image.Image)

    def test_api_error_handling(self, mocker):
        conversation_history = [{"role": "user", "content": "画一只狗"}]
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        
        mock_client = Mock()
        mock_client.GenerativeModel.return_value = mock_model
        
        with patch('src.gemini_api_module.genai', mock_client):
            with pytest.raises(APIError):
                generate_image_from_conversation(conversation_history, api_key="test_key")

    def test_network_error_handling(self, mocker):
        conversation_history = [{"role": "user", "content": "画一只鸟"}]
        mock_model = Mock()
        mock_model.generate_content.side_effect = ConnectionError("Network timeout")
        
        mock_client = Mock()
        mock_client.GenerativeModel.return_value = mock_model
        
        with patch('src.gemini_api_module.genai', mock_client):
            with pytest.raises(NetworkError):
                generate_image_from_conversation(conversation_history, api_key="test_key")

    def test_empty_conversation_history(self):
        with pytest.raises(ValueError):
            generate_image_from_conversation([], api_key="test_key")

    def test_invalid_context_window(self):
        conversation_history = [{"role": "user", "content": "测试"}]
        with pytest.raises(ValueError):
            generate_image_from_conversation(conversation_history, api_key="test_key", context_window=0)