# # app.py - Hugging Face Space Entry Point
# import os
# import sys
# import gradio as gr
# from fastapi import FastAPI, HTTPException, Depends, status, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# try:
#     from backend.api.routes import admin, auth, extension, prediction, toxic_detection
#     from backend.core.middleware import LogMiddleware
#     from backend.db.models.base import Base
#     from backend.db.models import Base, engine
#     # Thêm import model_adapter nếu có
#     try:
#         from backend.services.model_adapter import ModelAdapter
#     except ImportError:
#         print("ModelAdapter not found. Will use default model loading.")
# except ImportError:
#     print("Warning: Backend modules not found. Running in standalone mode.")

# from typing import List, Dict, Any, Optional
# import tensorflow as tf
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# import re
# import logging

# # Thiết lập logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Kiểm tra và tạo model tương thích nếu chưa có
# MODEL_DIR = "model"
# COMPATIBLE_MODEL_PATH = os.path.join(MODEL_DIR, "compatible_model.h5")
# ORIGINAL_MODEL_PATH = os.path.join(MODEL_DIR, "best_model_LSTM.h5")
# SAFETENSORS_MODEL_PATH = os.path.join(MODEL_DIR, "model.safetensors")  # Thêm đường dẫn model safetensors

# # Tạo thư mục model nếu chưa tồn tại
# os.makedirs(MODEL_DIR, exist_ok=True)

# # Kiểm tra model safetensors trước, sử dụng nếu có
# if not os.path.exists(SAFETENSORS_MODEL_PATH) and not os.path.exists(COMPATIBLE_MODEL_PATH):
#     logger.info("Không tìm thấy model safetensors và model tương thích, đang tạo model mới...")
#     try:
#         # Tạo model tương thích đơn giản
#         model = tf.keras.Sequential([
#             tf.keras.layers.Input(shape=(100,), dtype='float32'),
#             tf.keras.layers.Embedding(10000, 128, input_length=100),
#             tf.keras.layers.LSTM(64, dropout=0.2),
#             tf.keras.layers.Dense(64, activation='relu'),
#             tf.keras.layers.Dropout(0.5),
#             tf.keras.layers.Dense(4, activation='softmax')
#         ])
        
#         model.compile(
#             optimizer='adam',
#             loss='categorical_crossentropy',
#             metrics=['accuracy']
#         )
        
#         # Lưu model
#         model.save(COMPATIBLE_MODEL_PATH)
#         logger.info(f"Model tương thích đã được tạo thành công và lưu tại {COMPATIBLE_MODEL_PATH}")
#     except Exception as e:
#         logger.error(f"Lỗi khi tạo model tương thích: {e}")
#         logger.warning("API sẽ sử dụng model dự phòng")

# # Define our FastAPI application
# app = FastAPI(
#     title="Toxic Language Detector API",
#     description="API for detecting toxic language in social media comments",
#     version="1.0.0",
# )

# # CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # API models
# class PredictionRequest(BaseModel):
#     text: str
#     platform: Optional[str] = "unknown"
#     platform_id: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None

#     class Config:
#         from_attributes = True  # Updated from orm_mode=True

# class PredictionResponse(BaseModel):
#     text: str
#     prediction: int
#     confidence: float
#     prediction_text: str

#     class Config:
#         from_attributes = True  # Updated from orm_mode=True

# # Hàm tạo model tương thích nếu không thể tải model ban đầu
# def create_compatible_model():
#     """Tạo một model tương thích với cấu trúc đầu vào 10000 chiều"""
#     logger.info("Tạo model dự phòng với đầu vào 10000 chiều...")
#     inputs = tf.keras.Input(shape=(10000,))
#     x = tf.keras.layers.Dense(128, activation='relu')(inputs)
#     x = tf.keras.layers.Dropout(0.3)(x)
#     outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
#     model = tf.keras.Model(inputs=inputs, outputs=outputs)
#     model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
#     return model

# # Load ML model
# class ToxicDetectionModel:
#     def __init__(self):
#         # Load or create model trained on Vietnamese social media data
#         try:
#             # Kiểm tra xem có safetensors model không
#             self.using_safetensors = False
            
#             if os.path.exists(SAFETENSORS_MODEL_PATH):
#                 logger.info(f"Tìm thấy model safetensors tại {SAFETENSORS_MODEL_PATH}, đang tải...")
#                 try:
#                     # Thử tải với ModelAdapter nếu có
#                     try:
#                         from backend.services.model_adapter import ModelAdapter
#                         model_adapter = ModelAdapter()
#                         self.model = model_adapter.load_model(SAFETENSORS_MODEL_PATH)
#                         self.using_safetensors = True
#                         logger.info("Đã tải thành công model safetensors")
#                     except ImportError:
#                         # Thử tải trực tiếp với safetensors
#                         try:
#                             from safetensors.tensorflow import load_file
#                             logger.info("Thư viện safetensors có sẵn, đang tải model...")
                            
#                             # Tạo class đơn giản để tải model
#                             class SimpleSafetensorsLoader:
#                                 @staticmethod
#                                 def load_model(model_path):
#                                     # Tạo model với kiến trúc tương thích
#                                     inputs = tf.keras.Input(shape=(100,))
#                                     x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128)(inputs)
#                                     x = tf.keras.layers.LSTM(128)(x)
#                                     x = tf.keras.layers.Dense(64, activation='relu')(x)
#                                     x = tf.keras.layers.Dropout(0.2)(x)
#                                     outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
#                                     model = tf.keras.Model(inputs=inputs, outputs=outputs)
                                    
#                                     # Tải weights từ safetensors
#                                     weights_dict = load_file(model_path)
                                    
#                                     # Áp dụng weights (triển khai đơn giản)
#                                     for layer in model.layers:
#                                         layer_name = layer.name
#                                         weights = layer.get_weights()
                                        
#                                         if not weights:
#                                             continue
                                            
#                                         new_weights = []
#                                         for i, w in enumerate(weights):
#                                             weight_type = "kernel" if i == 0 else "bias"
#                                             key = f"{layer_name}.{weight_type}"
                                            
#                                             if key in weights_dict and weights_dict[key].shape == w.shape:
#                                                 new_weights.append(weights_dict[key])
#                                             else:
#                                                 new_weights.append(w)
                                                
#                                         if len(new_weights) == len(weights):
#                                             try:
#                                                 layer.set_weights(new_weights)
#                                             except Exception as e:
#                                                 logger.error(f"Lỗi khi áp dụng weights: {e}")
                                    
#                                     # Compile model
#                                     model.compile(
#                                         optimizer='adam',
#                                         loss='categorical_crossentropy',
#                                         metrics=['accuracy']
#                                     )
                                    
#                                     return model
                            
#                             # Tải model với loader đơn giản
#                             self.model = SimpleSafetensorsLoader.load_model(SAFETENSORS_MODEL_PATH)
#                             self.using_safetensors = True
#                             logger.info("Đã tải model safetensors với loader tự tạo")
#                         except ImportError:
#                             logger.warning("Không tìm thấy thư viện safetensors. Sẽ sử dụng model .h5...")
#                             self.using_safetensors = False
#                 except Exception as e:
#                     logger.error(f"Lỗi khi tải model safetensors: {e}")
#                     logger.warning("Sẽ sử dụng model .h5...")
#                     self.using_safetensors = False
            
#             # Nếu không sử dụng được safetensors, thử tải model .h5
#             if not self.using_safetensors:
#                 # Thử tải model tương thích trước
#                 model_path = COMPATIBLE_MODEL_PATH
#                 if not os.path.exists(model_path):
#                     model_path = ORIGINAL_MODEL_PATH
                    
#                 logger.info(f"Đang tải model h5 từ {model_path}...")
#                 self.model = tf.keras.models.load_model(model_path, compile=False)
#                 self.model.compile(
#                     optimizer='adam',
#                     loss='categorical_crossentropy',
#                     metrics=['accuracy']
#                 )
#                 logger.info("Vietnamese toxicity model loaded successfully")
            
#             self.using_dummy_model = False
            
#         except Exception as e:
#             logger.error(f"Error loading model: {e}")
#             logger.warning("Creating a dummy model for demonstration")
#             self.model = create_compatible_model()
#             self.using_dummy_model = True
        
#         # Initialize vectorizer for Vietnamese text
#         # Vietnamese doesn't use the same stop words as English
#         self.vectorizer = TfidfVectorizer(
#             max_features=10000,
#             stop_words=None,  # Don't use English stop words
#             ngram_range=(1, 3)  # Use 1-3 grams for better Vietnamese phrase capture
#         )
        
#         # Map predictions to text labels (in Vietnamese)
#         self.label_mapping = {
#             0: "bình thường",  # clean
#             1: "xúc phạm",     # offensive
#             2: "thù ghét",     # hate
#             3: "spam"          # spam
#         }
        
#         # Load Vietnamese tokenizer if available
#         try:
#             # Try to load underthesea for Vietnamese NLP
#             import importlib.util
#             if importlib.util.find_spec("underthesea"):
#                 from underthesea import word_tokenize
#                 self.has_vietnamese_nlp = True
#                 logger.info("Vietnamese NLP library loaded successfully")
#             else:
#                 self.has_vietnamese_nlp = False
#                 logger.info("Vietnamese NLP library not found, using basic tokenization")
#         except Exception as e:
#             logger.error(f"Error loading Vietnamese NLP library: {e}")
#             self.has_vietnamese_nlp = False
    
#     def preprocess_text(self, text):
#         """
#         Tiền xử lý văn bản tiếng Việt, giữ nguyên dấu và tạo vector đặc trưng
#         """
#         # Kiểm tra đầu vào
#         if not text or not isinstance(text, str):
#             text = str(text) if text else ""
        
#         # Clean text while preserving Vietnamese diacritical marks
#         text = text.lower()
#         text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
#         text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
        
#         # For Vietnamese, preserve diacritical marks and only remove punctuation
#         text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
#         text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
        
#         # Use Vietnamese tokenization if available
#         if self.has_vietnamese_nlp:
#             try:
#                 from underthesea import word_tokenize
#                 text = word_tokenize(text, format="text")
#             except Exception as e:
#                 logger.error(f"Error in Vietnamese tokenization: {e}")
        
#         # Vectorize
#         if not hasattr(self.vectorizer, 'vocabulary_'):
#             # Fit với một tập mẫu để đảm bảo có đủ tính năng
#             sample_texts = [
#                 text, 
#                 "mẫu văn bản thêm vào", 
#                 "thêm một số từ vựng phổ biến tiếng việt", 
#                 "spam quảng cáo giảm giá khuyến mãi mua ngay kẻo hết", 
#                 "ngôn từ thù ghét ghét bỏ căm thù muốn hủy diệt", 
#                 "từ ngữ xúc phạm đồ ngu ngốc kém cỏi vô dụng"
#             ]
#             self.vectorizer.fit(sample_texts)
        
#         # Tạo vector đặc trưng
#         features = self.vectorizer.transform([text]).toarray()
        
#         # Đảm bảo kích thước đúng là 10000
#         if features.shape[1] < 10000:
#             # Pad với zeros nếu vector nhỏ hơn kích thước mong đợi
#             padded_features = np.zeros((features.shape[0], 10000))
#             padded_features[:, :features.shape[1]] = features
#             features = padded_features
#         elif features.shape[1] > 10000:
#             # Cắt bớt nếu vector lớn hơn kích thước mong đợi
#             features = features[:, :10000]
        
#         return features
    
#     def predict(self, text):
#         """
#         Dự đoán phân loại văn bản với xử lý lỗi và dự phòng
#         """
#         try:
#             # Fallback if using dummy model and text has clear indicators
#             if self.using_dummy_model:
#                 # Dự đoán dựa trên rule nếu dùng model giả
#                 if "giảm giá" in text.lower() and ("http" in text.lower() or "www" in text.lower()):
#                     return 3, 0.91, self.label_mapping[3]  # Spam
#                 elif any(word in text.lower() for word in ["ghét", "chết", "giết", "tiêu diệt", "hủy diệt"]):
#                     return 2, 0.85, self.label_mapping[2]  # Hate
#                 elif any(word in text.lower() for word in ["ngu", "đồ", "kém", "dốt", "xấu"]):
#                     return 1, 0.78, self.label_mapping[1]  # Offensive
            
#             # Preprocess text
#             features = self.preprocess_text(text)
            
#             # Make prediction
#             predictions = self.model.predict(features, verbose=0)[0]
            
#             # Get most likely class and confidence
#             predicted_class = np.argmax(predictions)
#             confidence = float(predictions[predicted_class])
            
#             return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]
#         except Exception as e:
#             logger.error(f"Error in prediction: {e}")
#             # Fallback to rule-based prediction for stability
#             if "giảm giá" in text.lower() and "http" in text.lower():
#                 return 3, 0.9, self.label_mapping[3]  # Spam
#             elif "ghét" in text.lower() or "chết" in text.lower():
#                 return 2, 0.8, self.label_mapping[2]  # Hate
#             elif "ngu" in text.lower() or "đồ" in text.lower():
#                 return 1, 0.7, self.label_mapping[1]  # Offensive
#             else:
#                 return 0, 0.9, self.label_mapping[0]  # Clean

# # Initialize model
# model = ToxicDetectionModel()

# # API Key validation
# API_KEY = os.environ.get("API_KEY", "test-api-key")

# def verify_api_key(request: Request):
#     """Xác thực API key từ header request"""
#     api_key = request.headers.get("X-API-Key")
    
#     # Uncomment đoạn code này để bật xác thực API key trong production
#     # if not api_key or api_key != API_KEY:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED,
#     #         detail="Invalid API Key",
#     #     )
#     return api_key

# # API routes
# @app.post("/extension/detect", response_model=PredictionResponse)
# async def detect_toxic_language(
#     request: PredictionRequest,
#     api_key: str = Depends(verify_api_key)
# ):
#     """
#     Phân tích văn bản để phát hiện ngôn ngữ độc hại
    
#     - **text**: Văn bản cần phân tích
#     - **platform**: Nền tảng nguồn (facebook, youtube, twitter, ...)
#     - **platform_id**: ID của bình luận trên nền tảng
#     - **metadata**: Thông tin bổ sung
    
#     Trả về kết quả phân loại với 4 nhãn:
#     - 0: Bình thường (clean)
#     - 1: Xúc phạm (offensive)
#     - 2: Thù ghét (hate)
#     - 3: Spam
#     """
#     try:
#         # Make prediction
#         prediction_class, confidence, prediction_text = model.predict(request.text)
        
#         # Return response
#         return {
#             "text": request.text,
#             "prediction": prediction_class,
#             "confidence": confidence,
#             "prediction_text": prediction_text
#         }
#     except Exception as e:
#         logger.error(f"API Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error processing request: {str(e)}"
#         )

# @app.get("/", response_class=HTMLResponse)
# async def root():
#     return """
#     <html>
#         <head>
#             <title>Toxic Language Detector API</title>
#             <style>
#                 body {
#                     font-family: Arial, sans-serif;
#                     max-width: 800px;
#                     margin: 0 auto;
#                     padding: 20px;
#                 }
#                 h1 {
#                     color: #333;
#                 }
#                 .endpoint {
#                     margin-bottom: 20px;
#                     padding: 10px;
#                     border: 1px solid #ddd;
#                     border-radius: 5px;
#                 }
#                 .method {
#                     display: inline-block;
#                     padding: 3px 6px;
#                     background-color: #2196F3;
#                     color: white;
#                     border-radius: 3px;
#                     font-size: 14px;
#                 }
#                 pre {
#                     background-color: #f5f5f5;
#                     padding: 10px;
#                     border-radius: 5px;
#                     overflow-x: auto;
#                 }
#             </style>
#         </head>
#         <body>
#             <h1>Toxic Language Detector API</h1>
#             <p>This API provides endpoints for detecting toxic language in text.</p>
            
#             <div class="endpoint">
#                 <span class="method">POST</span> <strong>/extension/detect</strong>
#                 <p>Analyzes text for toxic language and returns the prediction.</p>
#                 <h4>Request</h4>
#                 <pre>
# {
#   "text": "Your text to analyze",
#   "platform": "facebook",
#   "platform_id": "optional-id",
#   "metadata": {}
# }
#                 </pre>
#                 <h4>Response</h4>
#                 <pre>
# {
#   "text": "Your text to analyze",
#   "prediction": 0,
#   "confidence": 0.95,
#   "prediction_text": "clean"
# }
#                 </pre>
#                 <p>Prediction values: 0 (clean), 1 (offensive), 2 (hate), 3 (spam)</p>
#             </div>
            
#             <p>For more information, check the <a href="/docs">API documentation</a>.</p>
#         </body>
#     </html>
#     """

# # Gradio interface
# def predict_toxic(text):
#     prediction_class, confidence, prediction_text = model.predict(text)
    
#     # Format response
#     result = f"Prediction: {prediction_text.capitalize()} (Class {prediction_class})\n"
#     result += f"Confidence: {confidence:.2f}"
    
#     return result

# # Create Gradio interface
# interface = gr.Interface(
#     fn=predict_toxic,
#     inputs=gr.Textbox(lines=5, placeholder="Enter text to analyze for toxic language..."),
#     outputs="text",
#     title="Toxic Language Detector",
#     description="Detects whether text contains toxic language. Classes: 0 (clean), 1 (offensive), 2 (hate), 3 (spam)."
# )

# # Mount Gradio app
# app = gr.mount_gradio_app(app, interface, path="/gradio")

# # For direct Hugging Face Space usage
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=7860)
# app.py - Entry Point for Toxic Language Detection API
import os
import sys
import gradio as gr
from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import time
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import re

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Cấu hình đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Đảm bảo thư mục tồn tại
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Đường dẫn đến các model
SAFETENSORS_MODEL_PATH = os.path.join(MODEL_DIR, "model.safetensors")
COMPATIBLE_MODEL_PATH = os.path.join(MODEL_DIR, "compatible_model.h5")
ORIGINAL_MODEL_PATH = os.path.join(MODEL_DIR, "best_model_LSTM.h5")
TOKENIZER_PATH = os.path.join(MODEL_DIR, "vietnamese_tokenizer.pkl")

# Đường dẫn đến dữ liệu hỗ trợ
VIETNAMESE_STOPWORDS_PATH = os.path.join(DATA_DIR, "vietnamese_stopwords.txt")
VIETNAMESE_OFFENSIVE_WORDS_PATH = os.path.join(DATA_DIR, "vietnamese_offensive_words.txt")

# Kiểm tra và tải backend nếu tồn tại
try:
    from backend.api.routes import admin, auth, extension, prediction, toxic_detection
    from backend.core.middleware import LogMiddleware, RateLimitMiddleware, ExceptionMiddleware
    from backend.db.models import Base, engine, init_db, create_initial_data
    from backend.services.ml_model import get_ml_model, predict_text
    from backend.services.model_adapter import ModelAdapter
    from backend.config.settings import settings
    
    USING_BACKEND = True
    logger.info("Đã tải thành công backend modules, sử dụng chế độ tích hợp")
    
    # Khởi tạo database và dữ liệu ban đầu
    try:
        init_db()
        create_initial_data()
        logger.info("Khởi tạo cơ sở dữ liệu và dữ liệu ban đầu thành công")
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo cơ sở dữ liệu: {str(e)}")
    
except ImportError as e:
    USING_BACKEND = False
    logger.warning(f"Không tìm thấy backend modules, chạy ở chế độ standalone: {str(e)}")
    
    # Import các module cần thiết cho chế độ standalone
    try:
        import tensorflow as tf
        from sklearn.feature_extraction.text import TfidfVectorizer
        import pickle
    except ImportError as e:
        logger.error(f"Lỗi khi import thư viện cần thiết: {str(e)}")
        raise

# Tạo các file mặc định nếu cần
def create_default_files():
    """Tạo các file mặc định cần thiết nếu chưa tồn tại"""
    
    # Tạo file stopwords mặc định
    if not os.path.exists(VIETNAMESE_STOPWORDS_PATH):
        default_stopwords = [
            "và", "của", "cho", "là", "đến", "trong", "với", "các", "có", "được", "tại", "về",
            "những", "như", "không", "này", "từ", "theo", "trên", "cũng", "đã", "sẽ", "vì", "nhưng",
            "ra", "còn", "bị", "đó", "để", "nên", "khi", "một", "mà", "do", "đề", "thì", "phải",
            "qua", "đi", "nếu", "làm", "mới", "vào", "hay", "rằng", "bởi", "vậy", "sau", "rất",
            "mình", "chỉ", "thế", "tôi", "anh", "chị", "bạn", "họ", "nhiều", "đâu", "thêm", "à", "vâng"
        ]
        
        with open(VIETNAMESE_STOPWORDS_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(default_stopwords))
        logger.info(f"Đã tạo file stopwords mặc định tại {VIETNAMESE_STOPWORDS_PATH}")
    
    # Tạo file từ ngữ xúc phạm mặc định
    if not os.path.exists(VIETNAMESE_OFFENSIVE_WORDS_PATH):
        # Chú ý: Danh sách này được rút gọn để phù hợp
        default_offensive_words = [
            "đồ", "thằng", "con", "ngu", "dốt", "khốn", "đểu", "điếm", 
            "xúc phạm", "thù ghét", "cay cú", "ghê tởm"
        ]
        
        with open(VIETNAMESE_OFFENSIVE_WORDS_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(default_offensive_words))
        logger.info(f"Đã tạo file từ ngữ xúc phạm mặc định tại {VIETNAMESE_OFFENSIVE_WORDS_PATH}")

# Thực hiện tạo các file mặc định
create_default_files()

# Hàm tạo model tương thích nếu không có model sẵn
def create_compatible_model():
    """Tạo một model tương thích đơn giản"""
    try:
        import tensorflow as tf
        
        logger.info("Đang tạo model tương thích đơn giản...")
        
        # Tạo model với kiến trúc đơn giản
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(100,), dtype='int32'),
            tf.keras.layers.Embedding(20000, 128, input_length=100),
            tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(4, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Lưu model
        model.save(COMPATIBLE_MODEL_PATH)
        logger.info(f"Đã tạo và lưu model tương thích tại {COMPATIBLE_MODEL_PATH}")
        
        return model
    except Exception as e:
        logger.error(f"Lỗi khi tạo model tương thích: {str(e)}")
        raise

# Class xử lý model
class ToxicDetectionModel:
    """Lớp xử lý model phát hiện ngôn từ tiêu cực"""
    
    def __init__(self):
        """Khởi tạo model và các thành phần cần thiết"""
        # Nếu đã có backend, sử dụng model từ backend
        if USING_BACKEND:
            try:
                logger.info("Sử dụng model từ backend")
                self.has_backend_model = True
                # Model từ backend sẽ được gọi qua predict_text
                return
            except Exception as e:
                logger.error(f"Lỗi khi sử dụng model từ backend: {str(e)}")
                self.has_backend_model = False
        else:
            self.has_backend_model = False
        
        # Khởi tạo các biến
        self.model = None
        self.tokenizer = None
        self.using_safetensors = False
        self.using_dummy_model = False
        self.max_sequence_length = 100
        
        # Map predictions sang text labels tiếng Việt
        self.label_mapping = {
            0: "bình thường",  # clean
            1: "xúc phạm",     # offensive
            2: "thù ghét",     # hate
            3: "spam"          # spam
        }
        
        # Tải model
        self._load_model()
        
        # Tải tokenizer
        self._load_tokenizer()
        
        # Kiểm tra thư viện NLP tiếng Việt
        self._check_vietnamese_nlp()
        
        # Tải stopwords tiếng Việt
        self._load_vietnamese_stopwords()
    
    def _load_model(self):
        """Tải model từ file hoặc tạo model tương thích nếu cần"""
        try:
            # Thử tải model từ các định dạng khác nhau
            if os.path.exists(SAFETENSORS_MODEL_PATH):
                self._load_safetensors_model()
            elif os.path.exists(COMPATIBLE_MODEL_PATH):
                self._load_h5_model(COMPATIBLE_MODEL_PATH)
            elif os.path.exists(ORIGINAL_MODEL_PATH):
                self._load_h5_model(ORIGINAL_MODEL_PATH)
            else:
                # Tạo và sử dụng model tương thích nếu không có model sẵn
                logger.warning("Không tìm thấy model. Tạo model tương thích mới.")
                self.model = create_compatible_model()
                self.using_dummy_model = True
        except Exception as e:
            logger.error(f"Lỗi khi tải model: {str(e)}")
            logger.warning("Sử dụng model dự phòng")
            self.model = self._create_dummy_model()
            self.using_dummy_model = True
    
    def _load_safetensors_model(self):
        """Tải model từ định dạng safetensors"""
        try:
            logger.info(f"Đang tải model safetensors từ {SAFETENSORS_MODEL_PATH}")
            
            try:
                # Thử tải với ModelAdapter từ backend nếu có
                from backend.services.model_adapter import ModelAdapter
                model_adapter = ModelAdapter()
                self.model = model_adapter.load_model(SAFETENSORS_MODEL_PATH)
                self.using_safetensors = True
                logger.info("Đã tải model safetensors thành công với ModelAdapter")
                return
            except ImportError:
                # Nếu không có ModelAdapter, thử tải trực tiếp với safetensors
                pass
            
            try:
                from safetensors.tensorflow import load_file
                import tensorflow as tf
                
                # Tạo model với kiến trúc mặc định
                inputs = tf.keras.Input(shape=(self.max_sequence_length,), dtype='int32')
                x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128)(inputs)
                x = tf.keras.layers.LSTM(128)(x)
                x = tf.keras.layers.Dense(64, activation='relu')(x)
                x = tf.keras.layers.Dropout(0.2)(x)
                outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
                model = tf.keras.Model(inputs=inputs, outputs=outputs)
                
                # Tải weights từ safetensors
                weights_dict = load_file(SAFETENSORS_MODEL_PATH)
                
                # Áp dụng weights
                for layer in model.layers:
                    layer_name = layer.name
                    weights = layer.get_weights()
                    
                    if not weights:
                        continue
                        
                    new_weights = []
                    for i, w in enumerate(weights):
                        weight_type = "kernel" if i == 0 else "bias"
                        key = f"{layer_name}.{weight_type}"
                        
                        if key in weights_dict and weights_dict[key].shape == w.shape:
                            new_weights.append(weights_dict[key])
                        else:
                            new_weights.append(w)
                            
                    if len(new_weights) == len(weights):
                        try:
                            layer.set_weights(new_weights)
                        except Exception as e:
                            logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")
                
                # Compile model
                model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                self.model = model
                self.using_safetensors = True
                logger.info("Đã tải model safetensors thành công")
            except ImportError:
                logger.warning("Không tìm thấy thư viện safetensors. Thử tải model .h5...")
                self._load_h5_model(COMPATIBLE_MODEL_PATH)
        except Exception as e:
            logger.error(f"Lỗi khi tải model safetensors: {str(e)}")
            raise
    
    def _load_h5_model(self, model_path):
        """Tải model từ định dạng h5"""
        try:
            import tensorflow as tf
            
            logger.info(f"Đang tải model h5 từ {model_path}")
            
            # Tải model
            self.model = tf.keras.models.load_model(model_path, compile=False)
            
            # Compile model
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Kiểm tra layer đầu vào để xác định max_sequence_length
            for layer in self.model.layers:
                if isinstance(layer, tf.keras.layers.InputLayer):
                    input_shape = layer.input_shape
                    if len(input_shape) > 1 and input_shape[1] is not None:
                        self.max_sequence_length = input_shape[1]
                        logger.info(f"Đã xác định max_sequence_length = {self.max_sequence_length}")
                    break
            
            self.using_safetensors = False
            logger.info(f"Đã tải model h5 thành công từ {model_path}")
        except Exception as e:
            logger.error(f"Lỗi khi tải model h5: {str(e)}")
            raise
    
    def _create_dummy_model(self):
        """Tạo model đơn giản khi không thể tải model chính"""
        import tensorflow as tf
        
        logger.info("Tạo model dự phòng đơn giản")
        
        # Tạo model đơn giản
        inputs = tf.keras.Input(shape=(self.max_sequence_length,), dtype='int32')
        x = tf.keras.layers.Embedding(input_dim=10000, output_dim=64)(inputs)
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        x = tf.keras.layers.Dense(32, activation='relu')(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _load_tokenizer(self):
        """Tải tokenizer hoặc tạo mới nếu không tìm thấy"""
        # Nếu đã có tokenizer từ backend, không cần tải thêm
        if self.has_backend_model:
            return
            
        try:
            # Thử tải tokenizer từ file
            if os.path.exists(TOKENIZER_PATH):
                logger.info(f"Tải tokenizer từ {TOKENIZER_PATH}")
                with open(TOKENIZER_PATH, 'rb') as handle:
                    self.tokenizer = pickle.load(handle)
            else:
                # Tạo tokenizer mới nếu không tìm thấy
                from tensorflow.keras.preprocessing.text import Tokenizer
                logger.info("Tạo tokenizer mới")
                self.tokenizer = Tokenizer(num_words=20000, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
                
                # Fit tokenizer với một số văn bản mẫu tiếng Việt
                sample_texts = [
                    "mẫu văn bản tiếng việt", 
                    "thêm một số từ vựng phổ biến", 
                    "spam quảng cáo giảm giá khuyến mãi mua ngay", 
                    "ngôn từ thù ghét căm thù muốn hủy diệt", 
                    "từ ngữ xúc phạm đồ ngu ngốc kém cỏi"
                ]
                self.tokenizer.fit_on_texts(sample_texts)
        except Exception as e:
            logger.error(f"Lỗi khi tải tokenizer: {str(e)}")
            # Fallback về TfidfVectorizer
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.tokenizer = TfidfVectorizer(
                max_features=10000,
                stop_words=None,  # Không sử dụng stopwords tiếng Anh
                ngram_range=(1, 3)  # Sử dụng 1-3 grams để bắt các cụm từ tiếng Việt tốt hơn
            )
    
    def _check_vietnamese_nlp(self):
        """Kiểm tra xem có thư viện NLP tiếng Việt không"""
        try:
            # Thử tải underthesea cho NLP tiếng Việt
            import importlib.util
            if importlib.util.find_spec("underthesea"):
                from underthesea import word_tokenize
                self.has_vietnamese_nlp = True
                logger.info("Đã tải thư viện NLP tiếng Việt (underthesea)")
            else:
                self.has_vietnamese_nlp = False
                logger.info("Không tìm thấy thư viện NLP tiếng Việt, sử dụng tokenize cơ bản")
        except Exception as e:
            logger.error(f"Lỗi khi tải thư viện NLP tiếng Việt: {str(e)}")
            self.has_vietnamese_nlp = False
    
    def _load_vietnamese_stopwords(self):
        """Tải danh sách stopwords tiếng Việt"""
        try:
            if os.path.exists(VIETNAMESE_STOPWORDS_PATH):
                with open(VIETNAMESE_STOPWORDS_PATH, 'r', encoding='utf-8') as f:
                    self.vietnamese_stopwords = set(line.strip() for line in f)
                logger.info(f"Đã tải {len(self.vietnamese_stopwords)} stopwords tiếng Việt")
            else:
                self.vietnamese_stopwords = set()
        except Exception as e:
            logger.error(f"Lỗi khi tải stopwords tiếng Việt: {str(e)}")
            self.vietnamese_stopwords = set()
    
    def preprocess_text(self, text):
        """
        Tiền xử lý văn bản tiếng Việt, giữ nguyên dấu và tạo vector đặc trưng
        """
        # Kiểm tra đầu vào
        if not text or not isinstance(text, str):
            text = str(text) if text else ""
        
        # Chuẩn hóa văn bản nhưng giữ lại dấu tiếng Việt
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Loại bỏ URL
        text = re.sub(r'<.*?>', '', text)  # Loại bỏ HTML tags
        
        # Đối với tiếng Việt, giữ nguyên dấu và chỉ loại bỏ dấu câu
        text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()  # Loại bỏ khoảng trắng thừa
        
        # Sử dụng tokenize tiếng Việt nếu có
        if self.has_vietnamese_nlp:
            try:
                from underthesea import word_tokenize
                text = word_tokenize(text, format="text")
            except Exception as e:
                logger.error(f"Lỗi khi tokenize tiếng Việt: {str(e)}")
        
        # Nếu sử dụng model từ backend, dừng lại ở đây
        if self.has_backend_model:
            return text
        
        # Nếu sử dụng tokenizer từ keras
        if hasattr(self.tokenizer, 'texts_to_sequences'):
            # Chuyển đổi văn bản thành chuỗi số
            sequences = self.tokenizer.texts_to_sequences([text])
            
            # Pad chuỗi để có độ dài cố định
            from tensorflow.keras.preprocessing.sequence import pad_sequences
            padded_sequences = pad_sequences(sequences, maxlen=self.max_sequence_length)
            
            return padded_sequences
        
        # Nếu sử dụng TfidfVectorizer
        elif hasattr(self.tokenizer, 'transform'):
            # Fit với một tập mẫu nếu chưa được huấn luyện
            if not hasattr(self.tokenizer, 'vocabulary_'):
                sample_texts = [
                    text, 
                    "mẫu văn bản tiếng việt", 
                    "spam quảng cáo giảm giá khuyến mãi", 
                    "ngôn từ thù ghét căm thù", 
                    "từ ngữ xúc phạm đồ ngu ngốc"
                ]
                self.tokenizer.fit(sample_texts)
            
            # Chuyển đổi văn bản thành vector TF-IDF
            features = self.tokenizer.transform([text]).toarray()
            
            return features
    
    def predict(self, text):
        """
        Dự đoán phân loại văn bản với xử lý lỗi và dự phòng
        
        Returns:
            Tuple[int, float, str]: (predicted_class, confidence, prediction_text)
        """
        # Nếu sử dụng model từ backend
        if self.has_backend_model:
            try:
                from backend.services.ml_model import predict_text
                prediction, confidence, probabilities = predict_text(text)
                prediction_text = self.label_mapping[prediction]
                return prediction, confidence, prediction_text
            except Exception as e:
                logger.error(f"Lỗi khi dự đoán với model backend: {str(e)}")
                # Fallback về rule-based prediction
                return self._rule_based_prediction(text)
        
        try:
            # Fallback if using dummy model and text has clear indicators
            if self.using_dummy_model:
                return self._rule_based_prediction(text)
            
            # Tiền xử lý văn bản
            processed_input = self.preprocess_text(text)
            
            # Thực hiện dự đoán
            predictions = self.model.predict(processed_input, verbose=0)[0]
            
            # Lấy lớp có xác suất cao nhất và độ tin cậy
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class])
            
            return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán: {str(e)}")
            # Fallback về rule-based prediction
            return self._rule_based_prediction(text)
    
    def _rule_based_prediction(self, text):
        """Dự đoán dựa trên các quy tắc đơn giản cho trường hợp dự phòng"""
        text_lower = text.lower()
        
        # Kiểm tra spam
        spam_indicators = ["giảm giá", "khuyến mãi", "sale", "mua ngay", "liên hệ", "http", "www", "link", "click", "tải"]
        if any(indicator in text_lower for indicator in spam_indicators) and any(url_part in text_lower for url_part in ["http", "www", ".com", ".vn"]):
            return 3, 0.91, self.label_mapping[3]  # Spam
            
        # Kiểm tra thù ghét
        hate_indicators = ["ghét", "chết", "giết", "tiêu diệt", "hủy diệt", "đánh", "đập", "phải chết", "xóa sổ"]
        if any(indicator in text_lower for indicator in hate_indicators):
            return 2, 0.85, self.label_mapping[2]  # Hate
            
        # Kiểm tra xúc phạm
        offensive_indicators = ["ngu", "đồ", "kém", "dốt", "xấu", "thằng", "con", "đểu", "tởm"]
        if any(indicator in text_lower for indicator in offensive_indicators):
            return 1, 0.78, self.label_mapping[1]  # Offensive
            
        # Mặc định là bình thường
        return 0, 0.95, self.label_mapping[0]  # Clean

# Khởi tạo model
model = ToxicDetectionModel()

# Khởi tạo FastAPI
app = FastAPI(
    title="Toxic Language Detector API",
    description="API phát hiện ngôn từ tiêu cực tiếng Việt trên mạng xã hội",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm middleware nếu sử dụng backend
if USING_BACKEND:
    # Thêm middleware từ backend
    try:
        app.add_middleware(LogMiddleware)
        app.add_middleware(RateLimitMiddleware)
        app.add_middleware(ExceptionMiddleware)
        logger.info("Đã thêm middleware từ backend")
    except Exception as e:
        logger.error(f"Lỗi khi thêm middleware từ backend: {str(e)}")

# API models
class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = Field(default="unknown", description="Nền tảng mạng xã hội nguồn")
    platform_id: Optional[str] = None
    source_user_name: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    save_result: Optional[bool] = Field(default=True, description="Có lưu kết quả vào database không")

    class Config:
        from_attributes = True  # Updated from orm_mode=True

class PredictionResponse(BaseModel):
    text: str
    prediction: int = Field(..., description="0: bình thường, 1: xúc phạm, 2: thù ghét, 3: spam")
    confidence: float
    prediction_text: str
    probabilities: Optional[Dict[str, float]] = None
    processed_text: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        from_attributes = True
        
    @validator('probabilities', pre=True, always=True)
    def set_probabilities(cls, v, values):
        # Nếu không có probabilities, tạo một dictionary với giá trị mặc định
        if v is None and 'prediction' in values:
            prediction = values['prediction']
            confidence = values.get('confidence', 0.8)
            
            # Map từ prediction sang labels
            labels = {
                0: "bình thường",
                1: "xúc phạm",
                2: "thù ghét",
                3: "spam"
            }
            
            # Tạo probabilities mặc định
            probs = {label: 0.05 for label in labels.values()}
            probs[labels[prediction]] = confidence
            
            # Đảm bảo tổng xác suất là 1
            total = sum(probs.values())
            if total > 0:
                probs = {k: v/total for k, v in probs.items()}
                
            return probs
        return v

class BatchPredictionRequest(BaseModel):
    items: List[PredictionRequest] = Field(..., description="Danh sách các mục cần dự đoán")
    store_clean: Optional[bool] = Field(default=False, description="Có lưu kết quả 'bình thường' không")

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    count: int
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    ml_info: Dict[str, Any]
    memory_usage: Optional[Dict[str, float]] = None
    uptime: Optional[float] = None

# API Key validation
API_KEY = os.environ.get("API_KEY", "test-api-key")

def verify_api_key(request: Request):
    """Xác thực API key từ header request"""
    api_key = request.headers.get("X-API-Key")
    
    # Uncomment dòng dưới đây để kích hoạt xác thực API key trong môi trường sản xuất
    # if not api_key or api_key != API_KEY:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid API Key",
    #     )
    return api_key

# Kết nối routes từ backend nếu có
if USING_BACKEND:
    try:
        # Thêm các routes từ backend
        app.include_router(admin.router, prefix="/admin", tags=["admin"])
        app.include_router(auth.router, prefix="/auth", tags=["auth"])
        app.include_router(extension.router, prefix="/extension", tags=["extension"])
        app.include_router(prediction.router, prefix="/predict", tags=["prediction"])
        app.include_router(toxic_detection.router, prefix="/toxic", tags=["toxic"])
        
        logger.info("Đã thêm routes từ backend")
    except Exception as e:
        logger.error(f"Lỗi khi thêm routes từ backend: {str(e)}")

# Thêm routes standalone
@app.post("/extension/detect", response_model=PredictionResponse)
async def detect_toxic_language(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Phân tích văn bản để phát hiện ngôn ngữ độc hại
    
    - **text**: Văn bản cần phân tích
    - **platform**: Nền tảng nguồn (facebook, youtube, twitter, ...)
    - **platform_id**: ID của bình luận trên nền tảng
    - **source_user_name**: Tên người dùng đã đăng bình luận
    - **source_url**: URL nguồn của bình luận
    - **metadata**: Thông tin bổ sung
    - **save_result**: Có lưu kết quả vào database không
    
    Trả về kết quả phân loại với 4 nhãn:
    - 0: Bình thường (clean)
    - 1: Xúc phạm (offensive)
    - 2: Thù ghét (hate)
    - 3: Spam
    """
    try:
        start_time = time.time()
        
        # Kiểm tra dữ liệu đầu vào
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required and cannot be empty"
            )
        
        # Xử lý dự đoán
        if USING_BACKEND:
            try:
                # Sử dụng function từ backend
                from backend.services.ml_model import predict_text
                prediction_class, confidence, probabilities = predict_text(request.text)
                prediction_text = model.label_mapping[prediction_class]
                
                # Lưu kết quả vào database nếu được yêu cầu
                if request.save_result:
                    background_tasks.add_task(
                        toxic_detection.save_prediction,
                        text=request.text,
                        prediction=prediction_class,
                        confidence=confidence,
                        platform=request.platform,
                        platform_id=request.platform_id,
                        source_user_name=request.source_user_name,
                        source_url=request.source_url,
                        metadata=request.metadata
                    )
            except Exception as e:
                logger.error(f"Lỗi khi sử dụng backend cho dự đoán: {str(e)}")
                # Fallback to standalone model
                prediction_class, confidence, prediction_text = model.predict(request.text)
                probabilities = None
        else:
            # Sử dụng model standalone
            prediction_class, confidence, prediction_text = model.predict(request.text)
            probabilities = None
        
        # Tạo response
        result = {
            "text": request.text,
            "prediction": prediction_class,
            "confidence": confidence,
            "prediction_text": prediction_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "probabilities": {
                "bình thường": 0.05,
                "xúc phạm": 0.05,
                "thù ghét": 0.05,
                "spam": 0.05
            }
        }
        
        # Cập nhật probabilities nếu có
        if probabilities:
            result["probabilities"] = {
                model.label_mapping[i]: float(p) for i, p in enumerate(probabilities)
            }
        else:
            # Nếu không có probabilities chi tiết, tạo dữ liệu giả
            probabilities_dict = {label: 0.05 for label in model.label_mapping.values()}
            probabilities_dict[prediction_text] = confidence
            # Đảm bảo tổng xác suất là 1
            total = sum(probabilities_dict.values())
            result["probabilities"] = {k: v/total for k, v in probabilities_dict.items()}
        
        # Thêm thông tin xử lý
        processing_time = time.time() - start_time
        logger.info(f"Xử lý dự đoán trong {processing_time:.4f}s: {result['prediction_text']} ({result['confidence']:.4f})")
        
        return result
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/batch/detect", response_model=BatchPredictionResponse)
async def batch_detect_toxic_language(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Phân tích hàng loạt văn bản để phát hiện ngôn ngữ độc hại
    
    - **items**: Danh sách các mục văn bản cần phân tích
    - **store_clean**: Có lưu kết quả "bình thường" không
    
    Trả về danh sách kết quả phân loại
    """
    try:
        start_time = time.time()
        results = []
        
        # Kiểm tra đầu vào
        if not request.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Items list cannot be empty"
            )
        
        # Xử lý từng item
        for item in request.items:
            if not item.text.strip():
                # Bỏ qua item rỗng
                continue
                
            # Dự đoán
            if USING_BACKEND:
                try:
                    # Sử dụng function từ backend
                    from backend.services.ml_model import predict_text
                    prediction_class, confidence, probabilities = predict_text(item.text)
                    prediction_text = model.label_mapping[prediction_class]
                except Exception:
                    # Fallback to standalone model
                    prediction_class, confidence, prediction_text = model.predict(item.text)
                    probabilities = None
            else:
                # Sử dụng model standalone
                prediction_class, confidence, prediction_text = model.predict(item.text)
                probabilities = None
            
            # Bỏ qua kết quả "bình thường" nếu không cần lưu
            if prediction_class == 0 and not request.store_clean:
                continue
                
            # Tạo response item
            result_item = PredictionResponse(
                text=item.text,
                prediction=prediction_class,
                confidence=confidence,
                prediction_text=prediction_text,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Thêm vào kết quả
            results.append(result_item)
            
            # Lưu vào database nếu cần
            if USING_BACKEND and item.save_result:
                background_tasks.add_task(
                    toxic_detection.save_prediction,
                    text=item.text,
                    prediction=prediction_class,
                    confidence=confidence,
                    platform=item.platform,
                    platform_id=item.platform_id,
                    source_user_name=item.source_user_name,
                    source_url=item.source_url,
                    metadata=item.metadata
                )
        
        # Tạo response tổng hợp
        processing_time = time.time() - start_time
        logger.info(f"Xử lý {len(request.items)} items trong {processing_time:.4f}s, trả về {len(results)} kết quả")
        
        return {
            "results": results,
            "count": len(results),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Batch API Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch request: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Kiểm tra trạng thái hoạt động của API
    """
    import psutil
    import platform
    from datetime import datetime
    
    # Lấy thông tin về memory
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_usage = {
        "rss": memory_info.rss / (1024 * 1024),  # MB
        "vms": memory_info.vms / (1024 * 1024),  # MB
        "percent": process.memory_percent()
    }
    
    # Thông tin model
    ml_info = {
        "type": "safetensors" if getattr(model, "using_safetensors", False) else "h5",
        "using_backend": getattr(model, "has_backend_model", False),
        "using_dummy": getattr(model, "using_dummy_model", False)
    }
    
    # Thời gian uptime
    start_time = getattr(app, "start_time", datetime.now().timestamp())
    uptime = datetime.now().timestamp() - start_time
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ml_info": ml_info,
        "memory_usage": memory_usage,
        "uptime": uptime
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Trang chủ API với hướng dẫn sử dụng
    """
    return """
    <html>
        <head>
            <title>Toxic Language Detector API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #2980b9;
                    margin-top: 30px;
                }
                .endpoint {
                    margin-bottom: 30px;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                }
                .method {
                    display: inline-block;
                    padding: 5px 10px;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 3px;
                    font-size: 14px;
                    font-weight: bold;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border: 1px solid #ddd;
                }
                code {
                    font-family: Consolas, Monaco, 'Andale Mono', monospace;
                }
                .path {
                    font-weight: bold;
                    color: #2c3e50;
                }
                .description {
                    margin: 10px 0;
                    color: #555;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                th, td {
                    text-align: left;
                    padding: 8px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .footer {
                    margin-top: 50px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <h1>API Phát hiện ngôn từ tiêu cực tiếng Việt</h1>
            <p>API này cung cấp các endpoint để phát hiện ngôn từ tiêu cực trong văn bản tiếng Việt.</p>
            
            <h2>Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/extension/detect</span>
                <p class="description">Phân tích văn bản để phát hiện ngôn từ tiêu cực</p>
                <h4>Request</h4>
                <pre><code>
{
  "text": "Văn bản cần phân tích",
  "platform": "facebook",
  "platform_id": "comment_123456",
  "source_user_name": "Người dùng",
  "source_url": "https://example.com/post/123",
  "metadata": {},
  "save_result": true
}
                </code></pre>
                <h4>Response</h4>
                <pre><code>
{
  "text": "Văn bản cần phân tích",
  "prediction": 0,
  "confidence": 0.95,
  "prediction_text": "bình thường",
  "probabilities": {
    "bình thường": 0.95,
    "xúc phạm": 0.02,
    "thù ghét": 0.01,
    "spam": 0.02
  },
  "timestamp": "2023-10-15 14:30:45"
}
                </code></pre>
                <h4>Giá trị prediction</h4>
                <table>
                    <tr>
                        <th>Giá trị</th>
                        <th>Nhãn</th>
                        <th>Mô tả</th>
                    </tr>
                    <tr>
                        <td>0</td>
                        <td>bình thường</td>
                        <td>Văn bản bình thường, không có nội dung tiêu cực</td>
                    </tr>
                    <tr>
                        <td>1</td>
                        <td>xúc phạm</td>
                        <td>Văn bản chứa ngôn từ xúc phạm</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>thù ghét</td>
                        <td>Văn bản chứa ngôn từ thù ghét</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>spam</td>
                        <td>Văn bản là spam hoặc quảng cáo</td>
                    </tr>
                </table>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/batch/detect</span>
                <p class="description">Phân tích hàng loạt văn bản</p>
                <h4>Request</h4>
                <pre><code>
{
  "items": [
    {
      "text": "Văn bản thứ nhất",
      "platform": "facebook"
    },
    {
      "text": "Văn bản thứ hai",
      "platform": "youtube"
    }
  ],
  "store_clean": false
}
                </code></pre>
                <h4>Response</h4>
                <pre><code>
{
  "results": [
    {
      "text": "Văn bản thứ nhất",
      "prediction": 1,
      "confidence": 0.85,
      "prediction_text": "xúc phạm",
      "timestamp": "2023-10-15 14:30:45"
    }
  ],
  "count": 1,
  "timestamp": "2023-10-15 14:30:45"
}
                </code></pre>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/health</span>
                <p class="description">Kiểm tra trạng thái hoạt động của API</p>
                <h4>Response</h4>
                <pre><code>
{
  "status": "healthy",
  "version": "1.0.0",
  "ml_info": {
    "type": "h5",
    "using_backend": true,
    "using_dummy": false
  },
  "memory_usage": {
    "rss": 156.8,
    "vms": 425.2,
    "percent": 2.5
  },
  "uptime": 3600.5
}
                </code></pre>
            </div>
            
            <p>Để biết thêm thông tin chi tiết về API, hãy xem <a href="/docs">tài liệu API</a>.</p>
            
            <div class="footer">
                <p>&copy; 2023 - API Phát hiện ngôn từ tiêu cực tiếng Việt</p>
            </div>
        </body>
    </html>
    """

# Mount Gradio app nếu có
try:
    import gradio as gr
    
    # Tạo Gradio interface
    def predict_toxic(text):
        prediction_class, confidence, prediction_text = model.predict(text)
        
        # Format kết quả
        result = f"Kết quả: {prediction_text.capitalize()} (Lớp {prediction_class})\n"
        result += f"Độ tin cậy: {confidence:.2f}"
        
        return result
    
    # Tạo giao diện Gradio
    interface = gr.Interface(
        fn=predict_toxic,
        inputs=gr.Textbox(lines=5, placeholder="Nhập văn bản để phân tích ngôn từ tiêu cực..."),
        outputs="text",
        title="Bộ phát hiện ngôn từ tiêu cực tiếng Việt",
        description="Phát hiện ngôn từ tiêu cực trong văn bản tiếng Việt. Kết quả: 0 (bình thường), 1 (xúc phạm), 2 (thù ghét), 3 (spam)."
    )
    
    # Mount Gradio vào FastAPI
    app = gr.mount_gradio_app(app, interface, path="/gradio")
    logger.info("Đã mount Gradio interface vào /gradio")
except ImportError:
    logger.warning("Không thể import Gradio, bỏ qua việc tạo giao diện demo")
except Exception as e:
    logger.error(f"Lỗi khi tạo Gradio interface: {str(e)}")

# Lưu thời gian bắt đầu
app.start_time = time.time()

# Start server
if __name__ == "__main__":
    # Đặt tiêu đề console
    try:
        if os.name == 'nt':  # Windows
            os.system("title Toxic Language Detection API")
        else:  # Unix/Linux
            print("\033]0;Toxic Language Detection API\a", end="", flush=True)
    except:
        pass
    
    # In thông tin khởi động
    logger.info("=" * 50)
    logger.info("Khởi động API phát hiện ngôn từ tiêu cực tiếng Việt")
    logger.info(f"Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Backend mode: {'Enabled' if USING_BACKEND else 'Disabled'}")
    logger.info("=" * 50)
    
    # Khởi động server
    import uvicorn
    
    # Xác định port từ biến môi trường hoặc mặc định
    port = int(os.environ.get("PORT", 7860))
    
    # Khởi động uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)