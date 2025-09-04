import base64
import re
from io import BytesIO
from typing import List, Dict

import google.generativeai as genai
from PIL import Image

class APIError(Exception):
    pass

class NetworkError(Exception):
    pass

def generate_image_from_conversation(
    conversation_history: List[Dict[str, str]],
    api_key: str,
    context_window: int = 6,
    model_name: str = "gemini-1.5-flash"
) -> Image.Image:
    if not conversation_history:
        raise ValueError("Conversation history cannot be empty")
    
    if not isinstance(context_window, int) or context_window <= 0:
        raise ValueError("Context window must be a positive integer")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        recent_history = conversation_history[-context_window:] if len(conversation_history) > context_window else conversation_history
        
        prompt_parts = []
        for message in recent_history:
            role = message.get("role", "user")
            content = message.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        
        full_prompt = "\n".join(prompt_parts)
        full_prompt += "\n\n根据以上对话内容，生成一张相关的图片。请返回base64编码的图片数据。"
        
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise APIError("Empty response from API")
        
        image_data = _extract_base64_image(response.text)
        if not image_data:
            raise APIError("No image found in response")
        
        image_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(image_bytes))
    
    except ConnectionError as e:
        raise NetworkError(f"Network error: {str(e)}")
    except Exception as e:
        if "Network" in str(e) or "Connection" in str(e):
            raise NetworkError(f"Network error: {str(e)}")
        else:
            raise APIError(f"API error: {str(e)}")

def _extract_base64_image(response_text: str) -> str:
    pattern = r'data:image/(?:png|jpeg|jpg);base64,([^)"\s]+)'
    match = re.search(pattern, response_text)
    return match.group(1) if match else None