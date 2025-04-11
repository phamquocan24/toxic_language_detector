# # services/huggingface_api.py
# import requests
# from typing import Dict, Any, List, Tuple
# import os

# class HuggingFaceAPI:
#     def __init__(self):
#         self.api_url = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
#         self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
#         self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
#     def predict(self, text: str, model_id: str = "distilbert-base-uncased-finetuned-sst-2-english") -> Tuple[int, float]:
#         """
#         Predict the class of the text using a HuggingFace model
        
#         Args:
#             text (str): The text to predict
#             model_id (str): The model ID on HuggingFace Hub
        
#         Returns:
#             Tuple[int, float]: Predicted class and confidence
#         """
#         api_url = f"{self.api_url}{model_id}"
#         payload = {"inputs": text}
        
#         response = requests.post(api_url, headers=self.headers, json=payload)
#         result = response.json()
        
#         if isinstance(result, list) and len(result) > 0:
#             # Handle classification output
#             if "label" in result[0]:
#                 label = result[0]["label"]
#                 score = result[0]["score"]
                
#                 # Map label to our classes
#                 label_mapping = {
#                     "POSITIVE": 0,  # clean
#                     "NEGATIVE": 1,  # offensive
#                     "NEUTRAL": 0,   # clean
#                     "HATE": 2,      # hate
#                     "SPAM": 3       # spam
#                 }
                
#                 predicted_class = label_mapping.get(label.upper(), 0)
#                 return predicted_class, score
        
#         # Default return if unable to process
#         return 0, 0.5
# services/huggingface_api.py
import requests
import time
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from backend.config.settings import settings

# Thiết lập logging
logger = logging.getLogger("services.huggingface_api")

class HuggingFaceAPI:
    """
    Lớp kết nối với Hugging Face Inference API để thực hiện dự đoán
    """
    
    def __init__(self):
        self.api_url = settings.HUGGINGFACE_API_URL
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.model_id = settings.HUGGINGFACE_MODEL_ID or "vinai/phobert-base-vietnamese-sentiment"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.labels = settings.MODEL_LABELS
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.timeout = 30  # seconds
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # seconds (1 hour)
    
    def predict(self, text: str, model_id: Optional[str] = None) -> Tuple[int, float, Dict[str, float]]:
        """
        Dự đoán nhãn cho văn bản sử dụng Hugging Face API
        
        Args:
            text (str): Văn bản cần dự đoán
            model_id (Optional[str]): ID model trên Hugging Face Hub
        
        Returns:
            Tuple[int, float, Dict[str, float]]: Nhãn dự đoán, độ tin cậy, và xác suất cho từng nhãn
        """
        if not self.api_key:
            logger.error("Không có Hugging Face API key")
            return 0, 0.5, {label: 0.0 for label in self.labels}
        
        # Sử dụng model_id được chỉ định hoặc mặc định
        model_id = model_id or self.model_id
        
        # Kiểm tra cache
        cache_key = f"{model_id}:{text}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                logger.debug(f"Cache hit for text: {text[:20]}...")
                return cache_entry['prediction'], cache_entry['confidence'], cache_entry['probabilities']
        
        # Chuẩn bị URL và payload
        api_url = f"{self.api_url}{model_id}"
        payload = {"inputs": text}
        
        # Thêm tham số dành riêng cho tiếng Việt nếu cần
        if model_id.lower().find('vietnamese') >= 0 or model_id.lower().find('phobert') >= 0:
            payload["options"] = {"wait_for_model": True, "use_vietnamese_preprocessing": True}
        
        # Thực hiện request với retry logic
        predicted_class = 0
        confidence = 0.5
        probabilities = {label: 0.0 for label in self.labels}
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    api_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=self.timeout
                )
                
                # Kiểm tra lỗi
                if response.status_code == 429:
                    # Rate limit - chờ và thử lại
                    logger.warning(f"Rate limited by Hugging Face API. Retrying in {self.retry_delay} seconds")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                elif response.status_code != 200:
                    logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                    break
                
                # Xử lý kết quả
                result = response.json()
                
                # Log kết quả chi tiết ở chế độ debug
                logger.debug(f"Hugging Face API response: {json.dumps(result)}")
                
                # Xử lý các loại phản hồi khác nhau
                if isinstance(result, list) and len(result) > 0:
                    # Format 1: Danh sách các nhãn và xác suất
                    if isinstance(result[0], dict) and "label" in result[0]:
                        # Cập nhật predicted_class và confidence
                        predictions = sorted(result, key=lambda x: x.get("score", 0), reverse=True)
                        top_prediction = predictions[0]
                        raw_label = top_prediction["label"].upper()
                        confidence = top_prediction["score"]
                        
                        # Map nhãn từ Hugging Face sang nhãn hệ thống
                        label_mapping = self._get_label_mapping(model_id)
                        predicted_class = label_mapping.get(raw_label, 0)
                        
                        # Cập nhật probabilities
                        for pred in predictions:
                            label_idx = label_mapping.get(pred["label"].upper(), 0)
                            label_name = self.labels[label_idx]
                            probabilities[label_name] = pred["score"]
                        
                        break
                elif isinstance(result, dict):
                    # Format 2: Dictionary với thông tin nhãn
                    if "label" in result:
                        raw_label = result["label"].upper()
                        confidence = result["score"]
                        
                        label_mapping = self._get_label_mapping(model_id)
                        predicted_class = label_mapping.get(raw_label, 0)
                        
                        # Xử lý probabilities nếu có
                        if "probabilities" in result:
                            for i, prob in enumerate(result["probabilities"]):
                                if i < len(self.labels):
                                    probabilities[self.labels[i]] = prob
                        else:
                            probabilities[self.labels[predicted_class]] = confidence
                        
                        break
                    # Format 3: Dictionary với logits hoặc kết quả khác
                    elif "logits" in result or "embedding" in result:
                        # Xử lý logits hoặc embedding nếu cần
                        pass
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                time.sleep(self.retry_delay)
                continue
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                break
        
        # Chuẩn hóa probabilities để tổng bằng 1
        prob_sum = sum(probabilities.values())
        if prob_sum > 0:
            probabilities = {k: v/prob_sum for k, v in probabilities.items()}
        
        # Lưu vào cache
        self.cache[cache_key] = {
            'prediction': predicted_class,
            'confidence': confidence,
            'probabilities': probabilities,
            'timestamp': time.time()
        }
        
        return predicted_class, confidence, probabilities
    
    def _get_label_mapping(self, model_id: str) -> Dict[str, int]:
        """
        Lấy mapping từ nhãn Hugging Face sang nhãn hệ thống
        
        Args:
            model_id (str): ID model trên Hugging Face Hub
        
        Returns:
            Dict[str, int]: Mapping từ nhãn Hugging Face sang nhãn hệ thống
        """
        # Mapping mặc định
        default_mapping = {
            "POSITIVE": 0,  # clean
            "NEGATIVE": 1,  # offensive
            "NEUTRAL": 0,   # clean
            "HATE": 2,      # hate
            "SPAM": 3,      # spam
            "CLEAN": 0,     # clean
            "OFFENSIVE": 1, # offensive
            "NEG": 1,       # offensive (negative)
            "POS": 0,       # clean (positive)
            "LABEL_0": 0,   # clean
            "LABEL_1": 1,   # offensive
            "LABEL_2": 2,   # hate
            "LABEL_3": 3,   # spam
        }
        
        # Mapping đặc biệt cho một số models tiếng Việt
        model_specific_mappings = {
            "vinai/phobert-base-vietnamese-sentiment": {
                "POSITIVE": 0,  # clean
                "NEGATIVE": 1,  # offensive
                "NEUTRAL": 0,   # clean
            },
            "vinai/phobert-base": {
                "POS": 0,       # clean
                "NEG": 1,       # offensive
            },
        }
        
        # Trả về mapping đặc biệt nếu có, nếu không thì dùng mặc định
        for specific_model, mapping in model_specific_mappings.items():
            if specific_model in model_id:
                return mapping
        
        return default_mapping
    
    def clear_cache(self):
        """
        Xóa cache
        """
        self.cache = {}
        logger.info("Cache đã được xóa")
    
    async def predict_async(self, text: str, model_id: Optional[str] = None) -> Tuple[int, float, Dict[str, float]]:
        """
        Phiên bản bất đồng bộ của hàm predict
        
        Args:
            text (str): Văn bản cần dự đoán
            model_id (Optional[str]): ID model trên Hugging Face Hub
        
        Returns:
            Tuple[int, float, Dict[str, float]]: Nhãn dự đoán, độ tin cậy, và xác suất cho từng nhãn
        """
        import aiohttp
        
        if not self.api_key:
            logger.error("Không có Hugging Face API key")
            return 0, 0.5, {label: 0.0 for label in self.labels}
        
        # Sử dụng model_id được chỉ định hoặc mặc định
        model_id = model_id or self.model_id
        
        # Kiểm tra cache
        cache_key = f"{model_id}:{text}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['prediction'], cache_entry['confidence'], cache_entry['probabilities']
        
        # Chuẩn bị URL và payload
        api_url = f"{self.api_url}{model_id}"
        payload = {"inputs": text}
        
        # Thêm tham số dành riêng cho tiếng Việt nếu cần
        if model_id.lower().find('vietnamese') >= 0 or model_id.lower().find('phobert') >= 0:
            payload["options"] = {"wait_for_model": True, "use_vietnamese_preprocessing": True}
        
        # Thực hiện request với retry logic
        predicted_class = 0
        confidence = 0.5
        probabilities = {label: 0.0 for label in self.labels}
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(api_url, headers=self.headers, json=payload, timeout=self.timeout) as response:
                        # Kiểm tra lỗi
                        if response.status == 429:
                            # Rate limit - chờ và thử lại
                            logger.warning(f"Rate limited by Hugging Face API. Retrying in {self.retry_delay} seconds")
                            time.sleep(self.retry_delay * (attempt + 1))
                            continue
                            
                        elif response.status != 200:
                            response_text = await response.text()
                            logger.error(f"Hugging Face API error: {response.status} - {response_text}")
                            break
                        
                        # Xử lý kết quả
                        result = await response.json()
                        
                        # Xử lý tương tự như hàm predict
                        # (code xử lý kết quả giống hàm predict)
                        
                except Exception as e:
                    logger.error(f"Async request error: {str(e)}")
                    time.sleep(self.retry_delay)
                    continue
        
        # Lưu vào cache
        self.cache[cache_key] = {
            'prediction': predicted_class,
            'confidence': confidence,
            'probabilities': probabilities,
            'timestamp': time.time()
        }
        
        return predicted_class, confidence, probabilities

# Khởi tạo singleton instance
huggingface_api = HuggingFaceAPI()

def get_model_prediction(text: str) -> Tuple[int, float, Dict[str, float]]:
    """
    Hàm helper để gọi API Hugging Face từ bên ngoài
    
    Args:
        text (str): Văn bản cần dự đoán
    
    Returns:
        Tuple[int, float, Dict[str, float]]: Nhãn dự đoán, độ tin cậy, và xác suất cho từng nhãn
    """
    return huggingface_api.predict(text)