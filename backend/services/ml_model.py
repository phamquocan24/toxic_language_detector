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
        self.model_type = "lstm"  # Mặc định là LSTM
        
        # Tải cấu hình model nếu có
        self._load_config()
        
        # Tải mô hình nếu cài đặt cho phép preload
        if settings.MODEL_PRELOAD:
            self.load_model()
    
    def _load_config(self):
        """Tải cấu hình model từ file config.json"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Cập nhật thông số từ config file
                if 'max_length' in config:
                    self.max_length = config['max_length']
                if 'vocab_size' in config:
                    self.max_words = config['vocab_size']
                if 'model_type' in config:
                    self.model_type = config['model_type']
                if 'labels' in config:
                    self.labels = config['labels']
                
                logger.info(f"Đã tải cấu hình model từ {self.config_path}. Model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Lỗi khi tải cấu hình model: {str(e)}")
    
    def load_model(self):
        """Tải model từ đường dẫn cấu hình"""
        # Nếu đã tải model rồi thì skip
        if self.loaded and self.model is not None:
            return

        try:
            logger.info(f"Đang tải model từ {self.model_path}...")

            # Kiểm tra các model mới trong thư mục model
            model_files = {
                "lstm": "model/best_model_LSTM.h5",
                "cnn": "model/cnn/model.safetensors",
                "grn": "model/grn/model.safetensors",
                "bert": "model/bert/model.safetensors",
                "phobert": "model/phobert/model.safetensors",
                "bert4news": "model/bert4news/model.safetensors"
            }
            
            # Thử tìm và tải model phù hợp với loại đã cấu hình
            if self.model_type in model_files and os.path.exists(model_files[self.model_type]):
                model_path = model_files[self.model_type]
                logger.info(f"Tìm thấy model '{self.model_type}' tại {model_path}")
            else:
                # Fallback về LSTM nếu không tìm thấy model cấu hình
                model_path = model_files.get("lstm", self.model_path)
                if os.path.exists(model_path):
                    logger.info(f"Fallback về model LSTM tại {model_path}")
                else:
                    model_path = self.model_path
                    logger.info(f"Sử dụng model mặc định tại {model_path}")
            
            # Sử dụng ModelAdapter để tải model bất kể định dạng nào
            self.model = ModelAdapter.load_model(model_path, self.device)
            logger.info(f"Đã tải model thành công: {model_path}")
            
            # Tải tokenizer phù hợp
            self._load_tokenizer(model_path)
            
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model: {str(e)}")
            # Tạo model dummy
            self._create_dummy_model()
    
    def _load_tokenizer(self, model_path):
        """Tải tokenizer phù hợp với model"""
        try:
            # Thử tìm tokenizer theo mẫu "<model_path>_tokenizer.pkl" hoặc thư mục chứa tokenizer
            tokenizer_path = model_path.replace('.h5', '_tokenizer.pkl').replace('.safetensors', '_tokenizer.pkl')
            if not os.path.exists(tokenizer_path):
                # Thử tìm trong thư mục model/
                tokenizer_path = os.path.join("model", "tokenizer.pkl")
            
            if os.path.exists(tokenizer_path):
                with open(tokenizer_path, 'rb') as f:
                    self.tokenizer = pickle.load(f)
                logger.info(f"Đã tải tokenizer từ {tokenizer_path}")
            else:
                # Tạo tokenizer mới
                logger.warning("Không tìm thấy tokenizer, tạo mới")
                self.tokenizer = Tokenizer(num_words=self.max_words)
                
                # Nếu có tập từ vựng, fit tokenizer với tập đó
                if os.path.exists(self.vocab_path):
                    with open(self.vocab_path, 'r', encoding='utf-8') as f:
                        vocab = [line.strip() for line in f.readlines()]
                    self.tokenizer.fit_on_texts(vocab)
                    logger.info(f"Đã fit tokenizer với từ vựng từ {self.vocab_path}")
        except Exception as e:
            logger.error(f"Lỗi khi tải tokenizer: {str(e)}")
            self.tokenizer = Tokenizer(num_words=self.max_words)
    
    def _create_dummy_model(self):
        """Tạo model giả để demo"""
        logger.warning("Tạo model dummy để demo")
        
        inputs = tf.keras.Input(shape=(self.max_length,))
        x = tf.keras.layers.Embedding(self.max_words, 128)(inputs)
        x = tf.keras.layers.LSTM(128)(x)
        outputs = tf.keras.layers.Dense(len(self.labels), activation='softmax')(x)
        
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.loaded = True
    
    def preprocess(self, text: str) -> np.ndarray:
        """Tiền xử lý văn bản đầu vào"""
        # Đảm bảo model và tokenizer đã được tải
        if not self.loaded:
            self.load_model()
        
        # Tiền xử lý text
        processed_text = preprocess_text(text)
        
        # Kiểm tra loại model để có phương pháp tiền xử lý phù hợp
        if self.model_type in ["bert", "phobert", "bert4news"]:
            # Sử dụng Hugging Face tokenizer nếu có
            try:
                from transformers import AutoTokenizer
                
                # Map model_type to pretrained model name
                model_name_map = {
                    "bert": "bert-base-multilingual-cased",
                    "phobert": "vinai/phobert-base",
                    "bert4news": "NlpHUST/vibert4news-base-cased"
                }
                
                model_name = model_name_map.get(self.model_type, "bert-base-multilingual-cased")
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Tokenize với BERT tokenizer
                encoded = tokenizer(
                    processed_text, 
                    truncation=True,
                    padding="max_length",
                    max_length=self.max_length,
                    return_tensors="tf"
                )
                
                return encoded
                
            except ImportError:
                logger.warning("Thư viện transformers không khả dụng, sử dụng tiền xử lý thông thường")
                # Fallback về phương pháp thông thường
        
        # Tiền xử lý thông thường với Keras Tokenizer
        sequences = self.tokenizer.texts_to_sequences([processed_text])
        padded = pad_sequences(sequences, maxlen=self.max_length)
        
        return padded
    
    def predict(self, text: str, model_type: str = None) -> Tuple[int, float, Dict[str, float]]:
        """
        Dự đoán phân loại cho văn bản
        
        Args:
            text: Văn bản cần phân loại
            model_type: Loại mô hình cần sử dụng (lstm, cnn, bert, phobert, bert4news, grn)
            
        Returns:
            Tuple[int, float, Dict[str, float]]: (predicted_class, confidence, probabilities)
        """
        # Đảm bảo model đã được tải
        if not self.loaded:
            self.load_model()
        
        # Xử lý văn bản trống
        if not text or not text.strip():
            # Trả về nhãn "clean" với độ tin cậy cao
            probabilities = {label: 0.0 for label in self.labels}
            probabilities[self.labels[0]] = 1.0
            return 0, 1.0, probabilities
        
        # Kiểm tra và sử dụng model_type được chỉ định
        current_model_type = self.model_type
        if model_type and model_type != self.model_type:
            try:
                # Lưu lại model_type hiện tại
                self.model_type = model_type
                
                # Kiểm tra các model mới trong thư mục model
                model_files = {
                    "lstm": "model/best_model_LSTM.h5",
                    "cnn": "model/cnn/model.safetensors",
                    "grn": "model/grn/model.safetensors",
                    "bert": "model/bert/model.safetensors",
                    "phobert": "model/phobert/model.safetensors",
                    "bert4news": "model/bert4news/model.safetensors"
                }
                
                # Kiểm tra nếu model tồn tại
                if model_type in model_files and os.path.exists(model_files[model_type]):
                    # Tải model mới
                    temp_model = ModelAdapter.load_model(model_files[model_type], self.device)
                    
                    # Tìm tokenizer phù hợp
                    tokenizer_path = model_files[model_type].replace('.h5', '_tokenizer.pkl').replace('.safetensors', '_tokenizer.pkl')
                    if not os.path.exists(tokenizer_path):
                        # Thử tìm trong thư mục model/
                        tokenizer_path = os.path.join("model", "tokenizer.pkl")
                    
                    temp_tokenizer = None
                    if os.path.exists(tokenizer_path):
                        with open(tokenizer_path, 'rb') as f:
                            temp_tokenizer = pickle.load(f)
                    
                    # Sử dụng model và tokenizer tạm thời
                    original_model = self.model
                    original_tokenizer = self.tokenizer
                    
                    self.model = temp_model
                    if temp_tokenizer:
                        self.tokenizer = temp_tokenizer
                    
                    # Thực hiện dự đoán
                    try:
                        processed_input = self.preprocess(text)
                        prediction = self.model.predict(processed_input)
                        
                        # Lấy kết quả
                        if isinstance(prediction, list):
                            probs = prediction[0]
                        else:
                            probs = prediction[0] if prediction.ndim > 1 else prediction
                        
                        # Lấy class có xác suất cao nhất
                        predicted_class = np.argmax(probs)
                        confidence = float(probs[predicted_class])
                        
                        # Chuẩn bị dictionary probabilities
                        probabilities = {
                            self.labels[i]: float(probs[i]) for i in range(len(self.labels))
                        }
                        
                        # Áp dụng rule-based heuristics cho spam
                        _, spam_features = preprocess_for_spam_detection(text)
                        
                        # Tích hợp phát hiện spam bổ sung
                        spam_class = 3  # Index cho spam
                        if predicted_class != spam_class and confidence < 0.8:
                            spam_score = 0
                            
                            if spam_features.get('has_url', False):
                                spam_score += 0.2
                            
                            if spam_features.get('has_suspicious_url', False):
                                spam_score += 0.3
                            
                            if spam_features.get('url_count', 0) > 1:
                                spam_score += 0.1 * spam_features.get('url_count', 0)
                            
                            if spam_features.get('spam_keyword_count', 0) > 0:
                                spam_score += 0.15 * spam_features.get('spam_keyword_count', 0)
                            
                            if spam_features.get('has_excessive_punctuation', False):
                                spam_score += 0.1
                            
                            if spam_features.get('has_all_caps_words', False):
                                spam_score += 0.1
                            
                            # Ghi đè dự đoán nếu spam_score đủ cao
                            if spam_score > 0.5:
                                predicted_class = spam_class
                                confidence = max(confidence, spam_score)
                                
                                # Cập nhật probabilities
                                probabilities = {label: 0.1 for label in self.labels}
                                probabilities[self.labels[spam_class]] = spam_score
                        
                        # Khôi phục model và tokenizer gốc
                        self.model = original_model
                        self.tokenizer = original_tokenizer
                        self.model_type = current_model_type
                        
                        return int(predicted_class), confidence, probabilities
                        
                    except Exception as e:
                        logger.error(f"Lỗi khi dự đoán với model {model_type}: {str(e)}")
                        # Khôi phục model và tokenizer gốc
                        self.model = original_model
                        self.tokenizer = original_tokenizer
                        self.model_type = current_model_type
                else:
                    logger.warning(f"Không tìm thấy model {model_type}, sử dụng model mặc định")
            except Exception as e:
                logger.error(f"Lỗi khi tải model {model_type}: {str(e)}")
                # Đảm bảo khôi phục model_type ban đầu
                self.model_type = current_model_type
        
        try:
            # Tiền xử lý text
            processed_input = self.preprocess(text)
            
            # Dự đoán
            prediction = self.model.predict(processed_input)
            
            # Lấy kết quả
            if isinstance(prediction, list):
                probs = prediction[0]
            else:
                probs = prediction[0] if prediction.ndim > 1 else prediction
            
            # Lấy class có xác suất cao nhất
            predicted_class = np.argmax(probs)
            confidence = float(probs[predicted_class])
            
            # Chuẩn bị dictionary probabilities
            probabilities = {
                self.labels[i]: float(probs[i]) for i in range(len(self.labels))
            }
            
            # Tích hợp phát hiện spam bổ sung
            _, spam_features = preprocess_for_spam_detection(text)
            
            # Áp dụng rule-based heuristics cho spam
            spam_class = 3  # Index cho spam
            if predicted_class != spam_class and confidence < 0.8:
                spam_score = 0
                
                if spam_features.get('has_url', False):
                    spam_score += 0.2
                
                if spam_features.get('has_suspicious_url', False):
                    spam_score += 0.3
                
                if spam_features.get('url_count', 0) > 1:
                    spam_score += 0.1 * spam_features.get('url_count', 0)
                
                if spam_features.get('spam_keyword_count', 0) > 0:
                    spam_score += 0.15 * spam_features.get('spam_keyword_count', 0)
                
                if spam_features.get('has_excessive_punctuation', False):
                    spam_score += 0.1
                
                if spam_features.get('has_all_caps_words', False):
                    spam_score += 0.1
                
                # Ghi đè dự đoán nếu spam_score đủ cao
                if spam_score > 0.5:
                    predicted_class = spam_class
                    confidence = max(confidence, spam_score)
                    
                    # Cập nhật probabilities
                    probabilities = {label: 0.1 for label in self.labels}
                    probabilities[self.labels[spam_class]] = spam_score
            
            return int(predicted_class), confidence, probabilities
            
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán: {str(e)}")
            # Fallback về clean với độ tin cậy thấp
            probabilities = {label: 0.2 for label in self.labels}
            probabilities[self.labels[0]] = 0.4
            return 0, 0.4, probabilities

# Singleton instance
_model_instance = None

def get_model_instance() -> MLModel:
    """
    Trả về singleton instance của MLModel
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = MLModel()
    return _model_instance

def predict_text(text: str) -> Tuple[int, float, Dict[str, float]]:
    """
    Hàm tiện ích để dự đoán text mà không cần tạo instance mới
    """
    model = get_model_instance()
    return model.predict(text)

def get_model_stats() -> Dict[str, Any]:
    """
    Lấy thống kê về model
    
    Returns:
        Dict[str, Any]: Thống kê về model
    """
    model = get_model_instance()
    return model.get_model_info()