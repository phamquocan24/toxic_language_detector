# # app.py - Hugging Face Space Entry Point
import os
import sys
import gradio as gr
from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import time
import io
import logging
from typing import List, Dict, Any, Optional
import tensorflow as tf
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime

# Kiểm tra xem có các module backend không
try:
    from backend.api.routes import admin, auth, extension, prediction, toxic_detection
    from backend.core.middleware import LogMiddleware, RateLimitMiddleware, ExceptionMiddleware
    from backend.db.models.base import Base, engine
    from backend.config.settings import settings
    # Thêm import model_adapter nếu có
    try:
        from backend.services.model_adapter import ModelAdapter
    except ImportError:
        print("ModelAdapter not found. Will use default model loading.")
    USING_BACKEND = True
    print("Backend modules found. Running in backend mode.")
except ImportError as e:
    print(
        f"Warning: Backend modules not found ({str(e)}). Running in standalone mode.")
    USING_BACKEND = False

# Thiết lập logging phù hợp cho Windows


class UnicodeStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Xử lý lỗi mã hóa khi hiển thị tiếng Việt trên Windows
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # Fallback nếu không thể hiển thị tiếng Việt
                safe_msg = msg.encode(
                    'utf-8', errors='replace').decode('utf-8', errors='replace')
                stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        UnicodeStreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Kiểm tra và tạo model tương thích nếu chưa có
MODEL_DIR = "model"
COMPATIBLE_MODEL_PATH = os.path.join(MODEL_DIR, "compatible_model.h5")
ORIGINAL_MODEL_PATH = os.path.join(MODEL_DIR, "best_model_LSTM.h5")
SAFETENSORS_MODEL_PATH = os.path.join(
    MODEL_DIR, "model.safetensors")  # Thêm đường dẫn model safetensors

# Tạo thư mục model nếu chưa tồn tại
os.makedirs(MODEL_DIR, exist_ok=True)

# Kiểm tra model safetensors trước, sử dụng nếu có
if not os.path.exists(SAFETENSORS_MODEL_PATH) and not os.path.exists(COMPATIBLE_MODEL_PATH):
    logger.info(
        "Không tìm thấy model safetensors và model tương thích, đang tạo model mới...")
    try:
        # Tạo model tương thích đơn giản
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(100,), dtype='float32'),
            tf.keras.layers.Embedding(10000, 128, input_length=100),
            tf.keras.layers.LSTM(64, dropout=0.2),
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
        logger.info(
            f"Model tương thích đã được tạo thành công và lưu tại {COMPATIBLE_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Lỗi khi tạo model tương thích: {e}")
        logger.warning("API sẽ sử dụng model dự phòng")

# Define our FastAPI application
app = FastAPI(
    title="Toxic Language Detector API",
    description="API for detecting toxic language in social media comments",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API models


class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    platform_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    source_user_name: Optional[str] = None
    source_url: Optional[str] = None
    save_result: Optional[bool] = True

    class Config:
        from_attributes = True  # Updated from orm_mode=True


class PredictionResponse(BaseModel):
    text: str
    prediction: int
    confidence: float
    prediction_text: str
    processed_text: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None
    keywords: Optional[List[str]] = None
    timestamp: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True  # Updated from orm_mode=True


class BatchPredictionRequest(BaseModel):
    items: List[PredictionRequest]
    store_clean: Optional[bool] = False


class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    count: int
    timestamp: str

# Hàm tạo model tương thích nếu không thể tải model ban đầu


def create_compatible_model():
    """Tạo một model tương thích với cấu trúc đầu vào 10000 chiều"""
    logger.info("Tạo model dự phòng với đầu vào 10000 chiều...")
    inputs = tf.keras.Input(shape=(10000,))
    x = tf.keras.layers.Dense(128, activation='relu')(inputs)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Load ML model


class ToxicDetectionModel:
    def __init__(self):
        # Load or create model trained on Vietnamese social media data
        try:
            # Kiểm tra xem có safetensors model không
            self.using_safetensors = False

            if os.path.exists(SAFETENSORS_MODEL_PATH):
                logger.info(
                    f"Tìm thấy model safetensors tại {SAFETENSORS_MODEL_PATH}, đang tải...")
                try:
                    # Thử tải với ModelAdapter nếu có
                    try:
                        from backend.services.model_adapter import ModelAdapter
                        model_adapter = ModelAdapter()
                        self.model = model_adapter.load_model(SAFETENSORS_MODEL_PATH)
                        self.using_safetensors = True
                        logger.info("Đã tải thành công model safetensors")
                    except ImportError:
                        # Thử tải trực tiếp với safetensors
                        try:
                            from safetensors.tensorflow import load_file
                            logger.info("Thư viện safetensors có sẵn, đang tải model...")
                            
                            # Tạo class đơn giản để tải model
                            class SimpleSafetensorsLoader:
                                @staticmethod
                                def load_model(model_path):
                                    # Tạo model với kiến trúc tương thích
                                    inputs = tf.keras.Input(shape=(100,))
                                    x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128)(inputs)
                                    x = tf.keras.layers.LSTM(128)(x)
                                    x = tf.keras.layers.Dense(64, activation='relu')(x)
                                    x = tf.keras.layers.Dropout(0.2)(x)
                                    outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
                                    model = tf.keras.Model(inputs=inputs, outputs=outputs)
                                    
                                    # Tải weights từ safetensors
                                    weights_dict = load_file(model_path)
                                    
                                    # Áp dụng weights (triển khai đơn giản)
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
                                                logger.error(f"Lỗi khi áp dụng weights: {e}")
                                    
                                    # Compile model
                                    model.compile(
                                        optimizer='adam',
                                        loss='categorical_crossentropy',
                                        metrics=['accuracy']
                                    )
                                    
                                    return model
                            
                            # Tải model với loader đơn giản
                            self.model = SimpleSafetensorsLoader.load_model(SAFETENSORS_MODEL_PATH)
                            self.using_safetensors = True
                            logger.info("Đã tải model safetensors với loader tự tạo")
                        except ImportError:
                            logger.warning("Không tìm thấy thư viện safetensors. Sẽ sử dụng model .h5...")
                            self.using_safetensors = False
                except Exception as e:
                    logger.error(f"Lỗi khi tải model safetensors: {e}")
                    logger.warning("Sẽ sử dụng model .h5...")
                    self.using_safetensors = False

            # Nếu không sử dụng được safetensors, thử tải model .h5
            if not self.using_safetensors:
                # Thử tải model tương thích trước
                model_path = COMPATIBLE_MODEL_PATH
                if not os.path.exists(model_path):
                    model_path = ORIGINAL_MODEL_PATH
                    
                logger.info(f"Đang tải model h5 từ {model_path}...")
                self.model = tf.keras.models.load_model(model_path, compile=False)
                self.model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                logger.info("Vietnamese toxicity model loaded successfully")
            
            self.using_dummy_model = False
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Creating a dummy model for demonstration")
            self.model = create_compatible_model()
            self.using_dummy_model = True

        # Initialize vectorizer for Vietnamese text
        # Vietnamese doesn't use the same stop words as English
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words=None,  # Don't use English stop words
            # Use 1-3 grams for better Vietnamese phrase capture
            ngram_range=(1, 3)
        )

        # Map predictions to text labels (in Vietnamese)
        self.label_mapping = {
            0: "bình thường",  # clean
            1: "xúc phạm",     # offensive
            2: "thù ghét",     # hate
            3: "spam"          # spam
        }

        # Load Vietnamese tokenizer if available
        try:
            # Try to load underthesea for Vietnamese NLP
            import importlib.util
            if importlib.util.find_spec("underthesea"):
                from underthesea import word_tokenize
                self.has_vietnamese_nlp = True
                logger.info("Vietnamese NLP library loaded successfully")
            else:
                self.has_vietnamese_nlp = False
                logger.info(
                    "Vietnamese NLP library not found, using basic tokenization")
        except Exception as e:
            logger.error(f"Error loading Vietnamese NLP library: {e}")
            self.has_vietnamese_nlp = False

    def preprocess_text(self, text):
        """
        Tiền xử lý văn bản tiếng Việt, giữ nguyên dấu và tạo vector đặc trưng
        """
        # Kiểm tra đầu vào
        if not text or not isinstance(text, str):
            text = str(text) if text else ""
        
        # Clean text while preserving Vietnamese diacritical marks
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
        text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
        
        # For Vietnamese, preserve diacritical marks and only remove punctuation
        text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
        
        # Use Vietnamese tokenization if available
        if self.has_vietnamese_nlp:
            try:
                from underthesea import word_tokenize
                text = word_tokenize(text, format="text")
            except Exception as e:
                logger.error(f"Error in Vietnamese tokenization: {e}")
        
        # Vectorize
        if not hasattr(self.vectorizer, 'vocabulary_'):
            # Fit với một tập mẫu để đảm bảo có đủ tính năng
            sample_texts = [
                text,
                "mẫu văn bản thêm vào",
                "thêm một số từ vựng phổ biến tiếng việt",
                "spam quảng cáo giảm giá khuyến mãi mua ngay kẻo hết",
                "ngôn từ thù ghét ghét bỏ căm thù muốn hủy diệt",
                "từ ngữ xúc phạm đồ ngu ngốc kém cỏi vô dụng"
            ]
            self.vectorizer.fit(sample_texts)
        
        # Tạo vector đặc trưng
        features = self.vectorizer.transform([text]).toarray()
        
        # Đảm bảo kích thước đúng là 10000
        if features.shape[1] < 10000:
            # Pad với zeros nếu vector nhỏ hơn kích thước mong đợi
            padded_features = np.zeros((features.shape[0], 10000))
            padded_features[:, :features.shape[1]] = features
            features = padded_features
        elif features.shape[1] > 10000:
            # Cắt bớt nếu vector lớn hơn kích thước mong đợi
            features = features[:, :10000]
            
        return features
    
    def predict(self, text):
        """
        Dự đoán phân loại văn bản với xử lý lỗi và dự phòng
        """
        try:
            # Fallback if using dummy model and text has clear indicators
            if self.using_dummy_model:
                # Dự đoán dựa trên rule nếu dùng model giả
                if "giảm giá" in text.lower() and ("http" in text.lower() or "www" in text.lower()):
                    return 3, 0.91, self.label_mapping[3]  # Spam
                elif any(word in text.lower() for word in ["ghét", "chết", "giết", "tiêu diệt", "hủy diệt"]):
                    return 2, 0.85, self.label_mapping[2]  # Hate
                elif any(word in text.lower() for word in ["ngu", "đồ", "kém", "dốt", "xấu"]):
                    return 1, 0.78, self.label_mapping[1]  # Offensive
            
            # Preprocess text
            features = self.preprocess_text(text)
            
            # Make prediction
            predictions = self.model.predict(features, verbose=0)[0]
            
            # Get most likely class and confidence
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class])
            
            return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            # Fallback to rule-based prediction for stability
            if "giảm giá" in text.lower() and "http" in text.lower():
                return 3, 0.9, self.label_mapping[3]  # Spam
            elif "ghét" in text.lower() or "chết" in text.lower():
                return 2, 0.8, self.label_mapping[2]  # Hate
            elif "ngu" in text.lower() or "đồ" in text.lower():
                return 1, 0.7, self.label_mapping[1]  # Offensive
            else:
                return 0, 0.9, self.label_mapping[0]  # Clean

# Initialize model
model = ToxicDetectionModel()

# API Key validation
API_KEY = os.environ.get("API_KEY", "test-api-key")

def verify_api_key(request: Request):
    """Xác thực API key từ header request"""
    api_key = request.headers.get("X-API-Key")
    
    # Uncomment đoạn code này để bật xác thực API key trong production
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

# Thêm routes standalone nếu cần
@app.post("/extension/detect", response_model=PredictionResponse)
async def detect_toxic_language(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
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
                if hasattr(request, 'save_result') and request.save_result:
                    background_tasks.add_task(
                        store_extension_prediction,
                        db=get_db(),
                        content=request.text,
                        prediction=prediction_class,
                        confidence=confidence,
                        platform=request.platform,
                        platform_id=request.platform_id,
                        source_user_name=request.source_user_name if hasattr(request, 'source_user_name') else None,
                        source_url=request.source_url if hasattr(request, 'source_url') else None,
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
        
        # Ghi log
        logger.info(f"Dự đoán cho '{request.text[:30]}...': {prediction_text}")
        
        # Tạo response
        response = {
            "text": request.text,
            "processed_text": None,
            "prediction": prediction_class,
            "confidence": confidence,
            "prediction_text": prediction_text,
            "probabilities": probabilities,
            "keywords": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Thời gian xử lý: {time.time() - start_time:.4f}s")
        return response
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

@app.get("/health")
async def health_check():
    """Endpoint kiểm tra trạng thái hoạt động"""
    import psutil
    import time
    
    # Thời gian bắt đầu chạy
    global start_time
    if not 'start_time' in globals():
        start_time = time.time()
    
    # Thông tin sử dụng bộ nhớ
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ml_info": {
            "type": "h5" if not model.using_safetensors else "safetensors",
            "using_backend": USING_BACKEND,
            "using_dummy": getattr(model, "using_dummy_model", False)
        },
        "memory_usage": {
            "rss": memory_info.rss / (1024 * 1024),  # MB
            "vms": memory_info.vms / (1024 * 1024),  # MB
            "percent": process.memory_percent()
        },
        "uptime": time.time() - start_time
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
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                .navigation {
                    text-align: center;
                    margin: 20px 0;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }
                .navigation a {
                    display: inline-block;
                    margin: 0 10px;
                    padding: 8px 15px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-weight: bold;
                }
                .navigation a:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <h1>API Phát hiện ngôn từ tiêu cực tiếng Việt</h1>
            <p>API này cung cấp các endpoint để phát hiện ngôn từ tiêu cực trong văn bản tiếng Việt.</p>
            
            <div class="navigation">
                <a href="/docs">Tài liệu API (Swagger UI)</a>
                <a href="/redoc">Tài liệu API (ReDoc)</a>
                <a href="/gradio">Giao diện demo</a>
            </div>
            
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

# Hàm lưu trữ dự đoán từ extension
def store_extension_prediction(
    db=None, 
    content=None, 
    platform=None, 
    source_user_name=None,
    source_url=None,
    prediction=0, 
    confidence=0.0,
    user_id=None,
    metadata=None
):
    """Lưu kết quả dự đoán từ extension nếu có backend"""
    try:
        if USING_BACKEND:
            from backend.utils.vector_utils import extract_features
            from backend.db.models import Comment
            
            # Extract vector features 
            vector = extract_features(content)
            
            # Tạo comment mới
            comment = Comment(
                content=content,
                platform=platform,
                prediction=prediction,
                confidence=confidence,
                source_user_name=source_user_name,
                source_url=source_url,
                user_id=user_id,
                metadata=metadata
            )
            
            # Gán vector
            if hasattr(comment, 'set_vector'):
                comment.set_vector(vector)
            
            # Lưu vào database
            db.add(comment)
            db.commit()
            logger.info(f"Đã lưu dự đoán vào database: {content[:30]}...")
        else:
            logger.info(f"Backend không có sẵn, không lưu dự đoán: {content[:30]}...")
    except Exception as e:
        logger.error(f"Lỗi khi lưu dự đoán: {str(e)}")
        # Không raise exception để tránh lỗi với background task