# # services/ml_model.py
# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
# import re
# import os
# from .model_adapter import ModelAdapter

# class MLModel:
#     def __init__(self, model_path="model/best_model_LSTM.h5", max_length=100, max_words=20000):
#         self.model_path = model_path
#         self.max_length = max_length
#         self.max_words = max_words
#         self.tokenizer = None
#         self.model = None
#         self.load_model()
    
#     def load_model(self):
#         """Load the pretrained model trained on Vietnamese social media data"""
#         try:
#             if os.path.exists(self.model_path):
#                 # Sử dụng ModelAdapter để tải model từ bất kỳ định dạng nào
#                 self.model = ModelAdapter.load_model(self.model_path)
#                 print(f"Vietnamese toxicity model loaded from {self.model_path}")
#             else:
#                 print(f"Model not found at {self.model_path}. Using dummy model.")
#                 self.model = self._create_dummy_model()
#         except Exception as e:
#             print(f"Error loading model: {e}. Using dummy model.")
#             self.model = self._create_dummy_model()
        
#         # Tiếp tục với phần tokenizer như cũ
#         try:
#             tokenizer_path = "model/vietnamese_tokenizer.pkl"
#             # Thêm đoạn này để tìm tokenizer phù hợp với model.safetensors
#             if self.model_path.endswith('.safetensors'):
#                 safetensors_tokenizer = self.model_path.replace('.safetensors', '_tokenizer.pkl')
#                 if os.path.exists(safetensors_tokenizer):
#                     tokenizer_path = safetensors_tokenizer
                    
#             if os.path.exists(tokenizer_path):
#                 import pickle
#                 with open(tokenizer_path, 'rb') as handle:
#                     self.tokenizer = pickle.load(handle)
#                 print(f"Vietnamese tokenizer loaded from {tokenizer_path}")
#             else:
#                 print("Tokenizer not found, initializing new one (for development only)")
#                 self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
#         except Exception as e:
#             print(f"Error loading tokenizer: {e}")
#             self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
    
#     def _fix_input_layer(self, config):
#         """Fix compatibility issues with older InputLayer configurations"""
#         if 'batch_shape' in config:
#             batch_shape = config.pop('batch_shape')
#             config['batch_input_shape'] = batch_shape
#         return tf.keras.layers.InputLayer(**config)
    
#     def _create_dummy_model(self):
#         """Create a dummy model for testing purposes"""
#         inputs = tf.keras.Input(shape=(self.max_length,))
#         x = tf.keras.layers.Embedding(self.max_words, 128, input_length=self.max_length)(inputs)
#         x = tf.keras.layers.LSTM(128)(x)
#         outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
#         model = tf.keras.Model(inputs=inputs, outputs=outputs)
#         model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
#         return model
    
#     def preprocess_text(self, text):
#         """Preprocess Vietnamese text for prediction"""
#         # For Vietnamese, we need to maintain special characters and diacritical marks
#         # Only remove punctuation and normalize whitespace
#         text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text.lower())
#         text = re.sub(r'\s+', ' ', text).strip()
        
#         # Use underthesea for Vietnamese tokenization if available
#         try:
#             from underthesea import word_tokenize
#             tokenized_text = word_tokenize(text, format="text")
#             text = tokenized_text
#         except ImportError:
#             # Fallback if underthesea is not available
#             pass
        
#         # Tokenize and pad
#         sequences = self.tokenizer.texts_to_sequences([text])
#         padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        
#         return padded_sequences
    
#     def predict(self, text):
#         """Predict the class of the Vietnamese text with enhanced spam detection"""
#         # Preprocess text
#         preprocessed_text = self.preprocess_text(text)
        
#         # Get additional spam features
#         _, spam_features = preprocess_for_spam_detection(text)
        
#         # Make prediction with the model
#         prediction = self.model.predict(preprocessed_text)[0]
        
#         # Get class and confidence
#         predicted_class = np.argmax(prediction)
#         confidence = float(prediction[predicted_class])
        
#         # Apply heuristic rules for spam detection enhancement
#         # If the model isn't confident but we have strong spam indicators
#         if predicted_class != 3 and confidence < 0.8:  # If not predicted as spam with high confidence
#             spam_score = 0
            
#             # Add score based on spam features
#             if spam_features['has_url']:
#                 spam_score += 0.2
            
#             if spam_features['has_suspicious_url']:
#                 spam_score += 0.3
            
#             if spam_features['url_count'] > 1:
#                 spam_score += 0.1 * spam_features['url_count']
            
#             if spam_features['spam_keyword_count'] > 0:
#                 spam_score += 0.15 * spam_features['spam_keyword_count']
            
#             if spam_features['has_excessive_punctuation']:
#                 spam_score += 0.1
                
#             if spam_features['has_all_caps_words']:
#                 spam_score += 0.1
            
#             # Override prediction if spam score is high enough
#             if spam_score > 0.5:
#                 predicted_class = 3  # Spam
#                 confidence = max(confidence, spam_score)
        
#         return int(predicted_class), confidence
# services/ml_model.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import os
import json
import pickle
import logging
from typing import Tuple, Dict, Any, List, Optional
from backend.config.settings import settings
from backend.utils.text_processing import preprocess_text, preprocess_for_spam_detection, extract_keywords
from .model_adapter import ModelAdapter

# Thiết lập logging
logger = logging.getLogger("services.ml_model")

class MLModel:
    """
    Lớp quản lý mô hình Machine Learning để phát hiện ngôn từ tiêu cực tiếng Việt
    """
    def __init__(self, model_path=None, max_length=100, max_words=20000):
        self.model_path = model_path or settings.MODEL_PATH
        self.vocab_path = settings.MODEL_VOCAB_PATH
        self.config_path = settings.MODEL_CONFIG_PATH
        self.max_length = max_length
        self.max_words = max_words
        self.tokenizer = None
        self.model = None
        self.device = settings.MODEL_DEVICE
        self.labels = settings.MODEL_LABELS
        self.loaded = False
        
        # Tải mô hình nếu cài đặt cho phép preload
        if settings.MODEL_PRELOAD:
            self.load_model()
    
    def load_model(self):
        """Tải mô hình đã được huấn luyện trên dữ liệu mạng xã hội tiếng Việt"""
        try:
            if os.path.exists(self.model_path):
                # Sử dụng ModelAdapter để tải model từ bất kỳ định dạng nào
                self.model = ModelAdapter.load_model(self.model_path, device=self.device)
                logger.info(f"Đã tải model tiếng Việt từ {self.model_path}")
                
                # Tải cấu hình model nếu có
                if os.path.exists(self.config_path):
                    try:
                        with open(self.config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            if 'max_length' in config:
                                self.max_length = config['max_length']
                            if 'max_words' in config:
                                self.max_words = config['max_words']
                        logger.info(f"Đã tải cấu hình model từ {self.config_path}")
                    except Exception as e:
                        logger.warning(f"Lỗi khi tải cấu hình model: {e}")
            else:
                logger.warning(f"Không tìm thấy model tại {self.model_path}. Sử dụng dummy model.")
                self.model = self._create_dummy_model()
        except Exception as e:
            logger.error(f"Lỗi khi tải model: {e}")
            self.model = self._create_dummy_model()
        
        # Tải tokenizer
        try:
            # Tìm tokenizer phù hợp với model
            tokenizer_path = self.vocab_path
            
            # Nếu không có đường dẫn cụ thể, thử các đường dẫn thông thường
            if not tokenizer_path or not os.path.exists(tokenizer_path):
                potential_paths = [
                    os.path.join(os.path.dirname(self.model_path), "tokenizer.pkl"),
                    os.path.join(os.path.dirname(self.model_path), "vietnamese_tokenizer.pkl"),
                    self.model_path.replace('.h5', '_tokenizer.pkl'),
                    self.model_path.replace('.safetensors', '_tokenizer.pkl'),
                    "model/vietnamese_tokenizer.pkl"
                ]
                
                for path in potential_paths:
                    if os.path.exists(path):
                        tokenizer_path = path
                        break
            
            # Tải tokenizer nếu tìm thấy
            if tokenizer_path and os.path.exists(tokenizer_path):
                with open(tokenizer_path, 'rb') as handle:
                    self.tokenizer = pickle.load(handle)
                logger.info(f"Đã tải Vietnamese tokenizer từ {tokenizer_path}")
            else:
                logger.warning("Không tìm thấy tokenizer, khởi tạo mới (chỉ dùng cho phát triển)")
                self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
        except Exception as e:
            logger.error(f"Lỗi khi tải tokenizer: {e}")
            self.tokenizer = Tokenizer(num_words=self.max_words, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
        
        self.loaded = True
    
    def _fix_input_layer(self, config):
        """Sửa các vấn đề tương thích với cấu hình InputLayer cũ"""
        if 'batch_shape' in config:
            batch_shape = config.pop('batch_shape')
            config['batch_input_shape'] = batch_shape
        return tf.keras.layers.InputLayer(**config)
    
    def _create_dummy_model(self):
        """Tạo dummy model cho mục đích kiểm thử"""
        inputs = tf.keras.Input(shape=(self.max_length,))
        x = tf.keras.layers.Embedding(self.max_words, 128, input_length=self.max_length)(inputs)
        x = tf.keras.layers.LSTM(128)(x)
        outputs = tf.keras.layers.Dense(len(self.labels), activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    def predict(self, text: str) -> Tuple[int, float]:
        if not self.loaded or not self.model:
            logger.error("Model chưa được tải.")
            return -1, 0.0
    
    def _preprocess_text(self, text):
        """Tiền xử lý văn bản tiếng Việt cho dự đoán"""
        # Tiền xử lý cơ bản
        text = preprocess_text(text)
        
        # Sử dụng underthesea cho tokenize tiếng Việt nếu có
        try:
            from underthesea import word_tokenize
            tokenized_text = word_tokenize(text, format="text")
            text = tokenized_text
        except ImportError:
            # Fallback nếu không có underthesea
            pass
        
        # Tokenize và pad
        sequences = self.tokenizer.texts_to_sequences([text])
        padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        
        return padded_sequences, text
    
    def predict(self, text) -> Tuple[int, float, Dict[str, float]]:
        """
        Dự đoán nhãn cho văn bản tiếng Việt với khả năng phát hiện spam nâng cao
        
        Args:
            text (str): Văn bản cần dự đoán
            
        Returns:
            Tuple[int, float, Dict[str, float]]: Nhãn dự đoán, độ tin cậy, và xác suất cho từng nhãn
        """
        # Đảm bảo model đã được tải
        if not self.loaded:
            self.load_model()
        
        # Tiền xử lý văn bản
        try:
            preprocessed_text, cleaned_text = self._preprocess_text(text)
        except Exception as e:
            logger.error(f"Lỗi khi tiền xử lý văn bản: {e}")
            # Fallback nếu tiền xử lý thất bại
            return 0, 0.5, {label: 0.25 for label in self.labels}
        
        # Lấy các đặc trưng spam bổ sung
        _, spam_features = preprocess_for_spam_detection(text)
        
        # Thực hiện dự đoán với model
        try:
            prediction = self.model.predict(preprocessed_text)[0]
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán: {e}")
            # Fallback nếu dự đoán thất bại
            return 0, 0.5, {label: 0.25 for label in self.labels}
        
        # Lấy nhãn và độ tin cậy
        predicted_class = np.argmax(prediction)
        confidence = float(prediction[predicted_class])
        
        # Tạo dictionary xác suất cho từng nhãn
        probabilities = {label: float(prob) for label, prob in zip(self.labels, prediction)}
        
        # Áp dụng các quy tắc heuristic cho việc phát hiện spam nâng cao
        # Nếu model không chắc chắn nhưng có các dấu hiệu spam mạnh
        if predicted_class != 3 and confidence < 0.8:  # Nếu không được dự đoán là spam với độ tin cậy cao
            spam_score = 0
            
            # Cộng điểm dựa trên các đặc trưng spam
            if spam_features['has_url']:
                spam_score += 0.2
            
            if spam_features['has_suspicious_url']:
                spam_score += 0.3
            
            if spam_features['url_count'] > 1:
                spam_score += 0.1 * min(spam_features['url_count'], 3)  # Giới hạn tối đa
            
            if spam_features['spam_keyword_count'] > 0:
                spam_score += 0.15 * min(spam_features['spam_keyword_count'], 5)  # Giới hạn tối đa
            
            if spam_features['has_excessive_punctuation']:
                spam_score += 0.1
                
            if spam_features['has_all_caps_words']:
                spam_score += 0.1
            
            # Ghi đè dự đoán nếu spam score đủ cao
            if spam_score > 0.5:
                predicted_class = 3  # Spam
                confidence = max(confidence, spam_score)
                # Cập nhật probabilities
                probabilities = {label: 0.1 for label in self.labels}
                probabilities[self.labels[3]] = confidence
        
        # Log kết quả ở chế độ debug
        logger.debug(f"Dự đoán cho '{text[:50]}...': {self.labels[predicted_class]} (tin cậy: {confidence:.2f})")
        
        return int(predicted_class), confidence, probabilities
    
    async def predict_async(self, text) -> Tuple[int, float, Dict[str, float]]:
        """
        Phiên bản bất đồng bộ của hàm predict
        """
        # Hiện tại, chỉ gọi phiên bản đồng bộ vì TensorFlow không có API bất đồng bộ
        # Trong tương lai, có thể thay đổi để sử dụng worker pool hoặc giải pháp khác
        return self.predict(text)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về model
        
        Returns:
            Dict[str, Any]: Thông tin model
        """
        total_params = 0
        if hasattr(self.model, 'count_params'):
            try:
                total_params = self.model.count_params()
            except:
                pass
        
        return {
            "model_path": self.model_path,
            "max_length": self.max_length,
            "max_words": self.max_words,
            "device": self.device,
            "labels": self.labels,
            "is_dummy": not os.path.exists(self.model_path),
            "total_params": total_params,
            "vocab_size": len(self.tokenizer.word_index) + 1 if self.tokenizer else 0
        }
    
    def extract_important_features(self, text) -> List[str]:
        """
        Trích xuất các đặc trưng quan trọng từ văn bản
        
        Args:
            text (str): Văn bản cần trích xuất
            
        Returns:
            List[str]: Danh sách các đặc trưng quan trọng
        """
        # Tiền xử lý văn bản
        _, cleaned_text = self._preprocess_text(text)
        
        # Trích xuất keywords
        keywords = extract_keywords(cleaned_text)
        
        return keywords

# Khởi tạo singleton instance
_model_instance = None

def get_ml_model() -> MLModel:
    """
    Lấy instance MLModel (Singleton pattern)
    
    Returns:
        MLModel: Instance ML model
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = MLModel()
    return _model_instance

def predict_text(text: str) -> Tuple[int, float, Dict[str, float]]:
    """
    Hàm helper để dự đoán nhãn cho văn bản
    
    Args:
        text (str): Văn bản cần dự đoán
        
    Returns:
        Tuple[int, float, Dict[str, float]]: Nhãn dự đoán, độ tin cậy, và xác suất cho từng nhãn
    """
    model = get_ml_model()
    return model.predict(text)

def get_model_stats() -> Dict[str, Any]:
    """
    Lấy thống kê về model
    
    Returns:
        Dict[str, Any]: Thống kê về model
    """
    model = get_ml_model()
    return model.get_model_info()

def get_labels(self) -> List[str]:
    return self.labels or ["clean", "offensive", "hate", "spam"]

def is_loaded(self) -> bool:
    return self.loaded