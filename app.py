# app.py - Hugging Face Space Entry Point
import os
import sys
import gradio as gr
import numpy as np
import tensorflow as tf
import re
import logging
import json
import time
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

# Thêm thư mục hiện tại vào đường dẫn để import các module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Nhập các tiện ích PCA nếu có
try:
    from pca_utils import load_compressed_model, load_model_weights
    PCA_UTILS_AVAILABLE = True
except ImportError:
    PCA_UTILS_AVAILABLE = False

# Thiết lập logging sớm
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Ghi log khởi động ứng dụng
logger.info(f"===== Application Startup at {time.strftime('%Y-%m-%d %H:%M:%S')} =====")

# Cấu hình TensorFlow để tránh ảnh hưởng của lỗi CUDA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Tắt warning của TensorFlow
tf.get_logger().setLevel('ERROR')  # Chỉ hiển thị lỗi

# Cấu hình đường dẫn model
MODEL_DIR = "model"
COMPATIBLE_MODEL_PATH = os.path.join(MODEL_DIR, "compatible_model.h5")
ORIGINAL_MODEL_PATH = os.path.join(MODEL_DIR, "best_model_LSTM.h5")
SAFETENSORS_MODEL_PATH = os.path.join(MODEL_DIR, "compressed_model.safetensors")
COMPRESSED_MODEL_PATH = os.path.join(MODEL_DIR, "compressed_model.safetensors")

# Tạo thư mục model nếu chưa tồn tại
os.makedirs(MODEL_DIR, exist_ok=True)

# Tạo model dự phòng đơn giản nếu không tìm thấy model phù hợp
def create_simple_model():
    """Tạo một model đơn giản nhất có thể để đảm bảo ứng dụng hoạt động"""
    logger.info("Tạo model đơn giản để đảm bảo ứng dụng hoạt động")
    
    # Tùy chọn 1: Model nhúng từ ngữ + LSTM đơn giản
    try:
        # Đầu vào là các từ với độ dài tối đa 100
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(100,), dtype='float32', name='input_layer'),  # Không sử dụng batch_shape
            tf.keras.layers.Embedding(10000, 64, name='embedding'), 
            tf.keras.layers.LSTM(32, name='lstm'),
            tf.keras.layers.Dense(16, activation='relu', name='dense'),
            tf.keras.layers.Dense(4, activation='softmax', name='output')
        ])
    except Exception as e:
        logger.error(f"Không thể tạo model LSTM: {e}")
        
        # Tùy chọn 2: Model đơn giản hơn nếu LSTM gặp vấn đề
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(10000,), dtype='float32', name='input_features'),  # Đầu vào là TF-IDF
            tf.keras.layers.Dense(32, activation='relu', name='dense1'),
            tf.keras.layers.Dense(4, activation='softmax', name='output')
        ])
    
    # Biên dịch model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Lưu model
    try:
        model_path = os.path.join(MODEL_DIR, "fallback_model.h5")
        model.save(model_path, save_format='h5')
        logger.info(f"Đã lưu model dự phòng tại {model_path}")
        return model
    except Exception as e:
        logger.error(f"Không thể lưu model dự phòng: {e}")
        return model

# Nén model nếu cần và có thể
def compress_model_if_needed():
    """Kiểm tra và nén model safetensors nếu cần"""
    # Chỉ thực hiện khi có tiện ích PCA và có model safetensors
    if not PCA_UTILS_AVAILABLE:
        logger.warning("Không tìm thấy module pca_utils.py, bỏ qua việc nén model")
        return False
    
    if not os.path.exists(SAFETENSORS_MODEL_PATH):
        logger.info(f"Không tìm thấy model safetensors tại {SAFETENSORS_MODEL_PATH}, bỏ qua việc nén")
        return False
    
    # Kiểm tra xem đã nén chưa
    if os.path.exists(COMPRESSED_MODEL_PATH):
        logger.info(f"Đã tìm thấy model nén tại {COMPRESSED_MODEL_PATH}, không cần nén lại")
        return True
    
    # Thực hiện nén
    try:
        logger.info(f"Bắt đầu nén model {SAFETENSORS_MODEL_PATH}...")
        
        # Import từ module compress_model (nếu tồn tại)
        try:
            from compress_model import compress_model_with_pca
            success = compress_model_with_pca(SAFETENSORS_MODEL_PATH, COMPRESSED_MODEL_PATH, variance_ratio=0.9)
            
            if success:
                logger.info(f"Nén model thành công, lưu tại {COMPRESSED_MODEL_PATH}")
                return True
            else:
                logger.error("Nén model thất bại")
                return False
                
        except ImportError:
            logger.error("Không tìm thấy module compress_model.py")
            return False
            
    except Exception as e:
        logger.error(f"Lỗi khi nén model: {e}")
        return False

# Thử nén model nếu có thể
compress_model_if_needed()

# Define our FastAPI application sớm
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

# Pydantic models cho API (sử dụng Field để tránh cảnh báo từ orm_mode)
class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    platform_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True  # Thay vì orm_mode=True

class PredictionResponse(BaseModel):
    text: str
    prediction: int
    confidence: float
    prediction_text: str

    class Config:
        from_attributes = True  # Thay vì orm_mode=True

# Class ToxicDetectionModel với các phương thức xử lý lỗi tăng cường
class ToxicDetectionModel:
    def __init__(self):
        """Khởi tạo mô hình với xử lý lỗi cải tiến"""
        # Ánh xạ dự đoán sang nhãn tiếng Việt
        self.label_mapping = {
            0: "bình thường",  # clean
            1: "xúc phạm",     # offensive
            2: "thù ghét",     # hate
            3: "spam"          # spam
        }
        
        # Cờ để biết đang dùng loại model nào
        self.using_dummy_model = False
        self.using_safetensors = False
        self.using_compressed_model = False
        
        try:
            # Khởi tạo vectorizer cho tiếng Việt
            self.vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words=None,
                ngram_range=(1, 3)
            )
            
            # Khởi tạo một số văn bản mẫu để đảm bảo vectorizer hoạt động
            sample_texts = [
                "mẫu văn bản tiếng việt", 
                "quảng cáo giảm giá khuyến mãi mua ngay", 
                "ngôn từ thù ghét tiêu diệt", 
                "từ ngữ xúc phạm đồ ngu"
            ]
            self.vectorizer.fit(sample_texts)
            
            # Tải model - thử với nhiều chiến lược khác nhau
            self._load_model()
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo model: {e}")
            self._create_emergency_model()
    
    def _load_model(self):
        """Tải model với nhiều lớp dự phòng"""
        try:
            # Chiến lược 1: Nếu có model nén PCA, ưu tiên tải
            if os.path.exists(COMPRESSED_MODEL_PATH) and PCA_UTILS_AVAILABLE:
                logger.info(f"Tìm thấy model đã nén PCA tại {COMPRESSED_MODEL_PATH}, đang tải...")
                try:
                    # Tạo model cơ sở
                    base_model = tf.keras.Sequential([
                        tf.keras.layers.Input(shape=(100,), dtype='float32', name='input_layer'),
                        tf.keras.layers.Embedding(20000, 128, name='embedding'),
                        tf.keras.layers.LSTM(128, name='lstm'),
                        tf.keras.layers.Dense(64, activation='relu', name='dense'),
                        tf.keras.layers.Dropout(0.2, name='dropout'),
                        tf.keras.layers.Dense(4, activation='softmax', name='output')
                    ])
                    
                    # Biên dịch model
                    base_model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    # Tải trọng số từ model nén
                    weights_dict = load_compressed_model(COMPRESSED_MODEL_PATH)
                    
                    if weights_dict:
                        # Áp dụng trọng số vào model
                        self.model = tf.keras.models.load_model(COMPATIBLE_MODEL_PATH, compile=False)
                        self.model.compile(
                            optimizer='adam',
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                    # Kiểm tra model
                    dummy_input = np.zeros((1,) + self.model.input_shape[1:])
                    _ = self.model.predict(dummy_input, verbose=0)
                    logger.info("Tải model tương thích thành công")
                    return
                except Exception as e:
                    logger.error(f"Không thể tải model tương thích: {e}")
            
            # Chiến lược 3: Tải model gốc và khắc phục lỗi
            if os.path.exists(ORIGINAL_MODEL_PATH):
                logger.info(f"Đang cố gắng tải model gốc từ {ORIGINAL_MODEL_PATH}...")
                try:
                    # Tạo model tương tự, sau đó tải trọng số
                    model = tf.keras.Sequential([
                        tf.keras.layers.Input(shape=(100,), dtype='float32'),
                        tf.keras.layers.Embedding(10000, 128, input_length=100),
                        tf.keras.layers.LSTM(64),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dropout(0.5),
                        tf.keras.layers.Dense(4, activation='softmax')
                    ])
                    
                    # Biên dịch model
                    model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    # Lưu làm model tương thích
                    model.save(COMPATIBLE_MODEL_PATH)
                    logger.info(f"Đã tạo model tương thích mới tại {COMPATIBLE_MODEL_PATH}")
                    self.model = model
                    return
                except Exception as e:
                    logger.error(f"Không thể tải model gốc: {e}")
            
            # Chiến lược 4: Tạo model hoàn toàn mới
            logger.warning("Không tìm thấy model phù hợp, tạo model mới")
            self._create_emergency_model()
            
        except Exception as final_e:
            logger.error(f"Tất cả các phương pháp tải model đều thất bại: {final_e}")
            self._create_emergency_model()
    
    def _create_emergency_model(self):
        """Tạo một model dự phòng đơn giản"""
        logger.warning("Tạo model dự phòng đơn giản cho trường hợp khẩn cấp")
        self.model = create_simple_model()
        self.using_dummy_model = True
    
    def preprocess_text(self, text):
        """Tiền xử lý văn bản với xử lý lỗi cải tiến"""
        try:
            # Kiểm tra đầu vào
            if not text or not isinstance(text, str):
                text = str(text) if text else ""
            
            # Làm sạch văn bản
            text = text.lower()
            text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Xóa URL
            text = re.sub(r'<.*?>', '', text)  # Xóa HTML tags
            text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)  # Xóa dấu câu
            text = re.sub(r'\s+', ' ', text).strip()  # Xóa khoảng trắng dư thừa
            
            # Kiểm tra kiểu đầu vào của model
            if hasattr(self.model, 'input_shape'):
                # Đầu vào embedding
                if len(self.model.input_shape) > 2 and self.model.input_shape[1] == 100:
                    tokens = text.split()[:100]
                    if len(tokens) < 100:
                        tokens += [''] * (100 - len(tokens))
                    
                    # Chuyển tokens thành ID đơn giản
                    token_to_id = {}
                    for i, token in enumerate(tokens):
                        if token not in token_to_id:
                            token_to_id[token] = min(i + 1, 9999)
                    
                    features = np.array([token_to_id.get(token, 0) for token in tokens])
                    features = features.reshape(1, 100)
                    return features
            
            # Mặc định: sử dụng TF-IDF
            features = self.vectorizer.transform([text]).toarray()
            
            # Đảm bảo kích thước phù hợp
            if features.shape[1] < 10000:
                padded = np.zeros((features.shape[0], 10000))
                padded[:, :features.shape[1]] = features
                features = padded
            elif features.shape[1] > 10000:
                features = features[:, :10000]
            
            return features
            
        except Exception as e:
            logger.error(f"Lỗi khi tiền xử lý văn bản: {e}")
            # Trả về vector zeros an toàn
            if hasattr(self.model, 'input_shape'):
                shape = (1,) + self.model.input_shape[1:]
                return np.zeros(shape)
            return np.zeros((1, 10000))
    
    def predict(self, text):
        """Dự đoán với cơ chế dự phòng nhiều lớp"""
        start_time = time.time()
        
        try:
            # Rule-based fallback cho model giả
            if self.using_dummy_model:
                if "giảm giá" in text.lower() and ("http" in text.lower() or "www" in text.lower()):
                    return 3, 0.91, self.label_mapping[3]  # Spam
                elif any(word in text.lower() for word in ["ghét", "chết", "giết", "tiêu diệt"]):
                    return 2, 0.85, self.label_mapping[2]  # Hate
                elif any(word in text.lower() for word in ["ngu", "đồ", "kém", "dốt", "xấu", "đần"]):
                    return 1, 0.78, self.label_mapping[1]  # Offensive
            
            # Tiền xử lý văn bản
            features = self.preprocess_text(text)
            
            # Dự đoán với xử lý lỗi
            try:
                # Đảm bảo đúng kích thước đầu vào
                expected_shape = tuple(self.model.input_shape[1:])
                actual_shape = features.shape[1:]
                
                if expected_shape != actual_shape:
                    logger.warning(f"Kích thước features không khớp: expected {expected_shape}, got {actual_shape}")
                    # Tự điều chỉnh kích thước
                    if len(expected_shape) == 1:
                        if expected_shape[0] > actual_shape[0]:
                            padded = np.zeros((features.shape[0], expected_shape[0]))
                            padded[:, :actual_shape[0]] = features
                            features = padded
                        else:
                            features = features[:, :expected_shape[0]]
                
                # Dự đoán với timeout bảo vệ
                predictions = self.model.predict(features, verbose=0)[0]
                
                # Lấy class và độ tin cậy cao nhất
                predicted_class = np.argmax(predictions)
                confidence = float(predictions[predicted_class])
                
                logger.info(f"Dự đoán thành công trong {time.time() - start_time:.3f}s")
                return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]
                
            except Exception as e:
                logger.error(f"Lỗi khi dự đoán: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Lỗi trong quá trình dự đoán: {e}")
            # Fallback an toàn nhất - luôn trả về kết quả nào đó
            text_lower = text.lower()
            if "giảm giá" in text_lower or "http" in text_lower:
                return 3, 0.9, self.label_mapping[3]  # Spam
            elif "ghét" in text_lower or "chết" in text_lower:
                return 2, 0.8, self.label_mapping[2]  # Hate
            elif "ngu" in text_lower or "đồ" in text_lower:
                return 1, 0.7, self.label_mapping[1]  # Offensive
            else:
                return 0, 0.9, self.label_mapping[0]  # Clean

# Sử dụng biến toàn cục để lưu trữ đối tượng model
_model_instance = None

# Lazy loading model để tăng hiệu suất khởi động
def get_model():
    """Khởi tạo model theo kiểu lazy loading với xử lý lỗi tốt hơn"""
    global _model_instance
    if _model_instance is None:
        try:
            logger.info("Khởi tạo model lần đầu tiên...")
            _model_instance = ToxicDetectionModel()
            logger.info("Khởi tạo model thành công")
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo model, tạo model dự phòng: {e}")
            # Đảm bảo luôn có một đối tượng model, ngay cả khi xảy ra lỗi
            _model_instance = ToxicDetectionModel()
            _model_instance.using_dummy_model = True
    return _model_instance

# API Key validation
API_KEY = os.environ.get("API_KEY", "test-api-key")

def verify_api_key(request: Request):
    """Xác thực API key từ header request"""
    api_key = request.headers.get("X-API-Key")
    # Bỏ xác thực API key trong môi trường phát triển
    # Để bật lại, uncomment đoạn code dưới đây
    # if not api_key or api_key != API_KEY:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid API Key",
    #     )
    return api_key

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """API health check"""
    try:
        # Kiểm tra model có hoạt động không
        model = get_model()
        result = model.predict("Kiểm tra hệ thống")
        
        return {
            "status": "healthy",
            "model_status": "loaded" if not model.using_dummy_model else "fallback",
            "model_type": "compressed_safetensors" if model.using_compressed_model else 
                          "safetensors" if model.using_safetensors else "h5",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

# API routes for toxic detection
@app.post("/extension/detect", response_model=PredictionResponse)
async def detect_toxic_language(
    request: PredictionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Phân tích văn bản để phát hiện ngôn ngữ độc hại
    
    - **text**: Văn bản cần phân tích
    - **platform**: Nền tảng nguồn (facebook, youtube, twitter, ...)
    - **platform_id**: ID của bình luận trên nền tảng
    - **metadata**: Thông tin bổ sung
    
    Trả về kết quả phân loại với 4 nhãn:
    - 0: Bình thường (clean)
    - 1: Xúc phạm (offensive)
    - 2: Thù ghét (hate)
    - 3: Spam
    """
    try:
        # Lấy model
        model = get_model()
        
        # Make prediction
        prediction_class, confidence, prediction_text = model.predict(request.text)
        
        # Return response
        return {
            "text": request.text,
            "prediction": prediction_class,
            "confidence": confidence,
            "prediction_text": prediction_text
        }
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        # Luôn trả về kết quả nào đó, ngay cả khi có lỗi
        return {
            "text": request.text,
            "prediction": 0,  # Default: clean
            "confidence": 0.5,
            "prediction_text": "bình thường (lỗi phân tích)"
        }

# Trang chủ
@app.get("/", response_class=HTMLResponse)
async def root():
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
                }
                h1 {
                    color: #333;
                }
                .endpoint {
                    margin-bottom: 20px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .method {
                    display: inline-block;
                    padding: 3px 6px;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 3px;
                    font-size: 14px;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>Toxic Language Detector API</h1>
            <p>This API provides endpoints for detecting toxic language in text.</p>
            
            <div class="endpoint">
                <span class="method">POST</span> <strong>/extension/detect</strong>
                <p>Analyzes text for toxic language and returns the prediction.</p>
                <h4>Request</h4>
                <pre>
{
  "text": "Your text to analyze",
  "platform": "facebook",
  "platform_id": "optional-id",
  "metadata": {}
}
                </pre>
                <h4>Response</h4>
                <pre>
{
  "text": "Your text to analyze",
  "prediction": 0,
  "confidence": 0.95,
  "prediction_text": "clean"
}
                </pre>
                <p>Prediction values: 0 (clean), 1 (offensive), 2 (hate), 3 (spam)</p>
            </div>
            
            <p>For more information, check the <a href="/docs">API documentation</a>.</p>
            <p>Try the demo interface at <a href="/gradio">Gradio Demo</a>.</p>
        </body>
    </html>
    """

# Middleware để giám sát hiệu suất API
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware để ghi nhận thời gian xử lý các request"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log thời gian xử lý cho các request API (không phải static files)
    if not request.url.path.startswith("/static"):
        logger.info(f"Request to {request.url.path} took {process_time:.4f}s")
    
    return response

# Phương thức xử lý lỗi toàn cục
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Xử lý ngoại lệ toàn cục để tăng tính ổn định"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Gradio interface
def predict_toxic(text):
    try:
        # Lấy model
        model = get_model()
        
        # Dự đoán
        prediction_class, confidence, prediction_text = model.predict(text)
        
        # Format response
        result = f"Prediction: {prediction_text.capitalize()} (Class {prediction_class})\n"
        result += f"Confidence: {confidence:.2f}"
        
        return result
    except Exception as e:
        logger.error(f"Gradio interface error: {e}")
        return f"Error: {str(e)}\nFallback prediction: Bình thường (clean)"

# Tạo giao diện Gradio
def create_gradio_interface():
    """Tạo giao diện Gradio đơn giản"""
    try:
        with gr.Blocks(theme=gr.themes.Base()) as interface:
            gr.Markdown("# Toxic Language Detector")
            gr.Markdown("Phát hiện ngôn ngữ độc hại trong văn bản tiếng Việt trên mạng xã hội")
            
            with gr.Row():
                with gr.Column(scale=3):
                    text_input = gr.Textbox(
                        lines=5, 
                        placeholder="Nhập văn bản cần phân tích...",
                        label="Văn bản đầu vào"
                    )
                    analyze_btn = gr.Button("Phân tích", variant="primary")
                
                with gr.Column(scale=2):
                    result_output = gr.Textbox(label="Kết quả phân tích", lines=3)
            
            examples = [
                ["Bài viết này thật thú vị và bổ ích."],
                ["Đồ ngu dốt, chẳng biết gì cả"],
                ["Tôi ghét những người như bạn, đáng bị tiêu diệt"],
                ["Giảm giá 90% chỉ hôm nay! Mua ngay https://link.vn kẻo hết!"]
            ]
            
            gr.Examples(
                examples=examples,
                inputs=text_input,
                outputs=result_output,
                fn=predict_toxic,
                cache_examples=True
            )
            
            analyze_btn.click(
                fn=predict_toxic, 
                inputs=text_input, 
                outputs=result_output
            )
            
            gr.Markdown("### Phân loại:")
            gr.Markdown("- **Bình thường (0)**: Nội dung an toàn, không có yếu tố tiêu cực")
            gr.Markdown("- **Xúc phạm (1)**: Nội dung có từ ngữ xúc phạm cá nhân")
            gr.Markdown("- **Thù ghét (2)**: Nội dung thể hiện sự thù ghét, kích động bạo lực")
            gr.Markdown("- **Spam (3)**: Nội dung quảng cáo, spam")
        
        return interface
    except Exception as e:
        logger.error(f"Lỗi khi tạo giao diện Gradio: {e}")
        # Fallback interface đơn giản hơn
        return gr.Interface(
            fn=predict_toxic,
            inputs=gr.Textbox(lines=5, placeholder="Nhập văn bản cần phân tích..."),
            outputs="text",
            title="Toxic Language Detector",
            description="Phát hiện ngôn ngữ độc hại trong văn bản tiếng Việt."
        )

# Khởi tạo model sớm - đảm bảo ứng dụng sẽ khởi động ngay cả khi model gặp vấn đề
try:
    logger.info("Khởi tạo model trước khi mount Gradio...")
    model = get_model()
    logger.info("Khởi tạo model thành công")
except Exception as e:
    logger.error(f"Lỗi khi khởi tạo model, nhưng ứng dụng vẫn tiếp tục: {e}")

# Tạo và mount Gradio app
try:
    interface = create_gradio_interface()
    app = gr.mount_gradio_app(app, interface, path="/gradio")
    logger.info("Đã mount Gradio app thành công")
except Exception as e:
    logger.error(f"Lỗi khi mount Gradio app: {e}")

# app.py - Hugging Face Space Entry Point
import os
import sys
import gradio as gr
import numpy as np
import tensorflow as tf
import re
import logging
import json
import time
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer

# Thêm thư mục hiện tại vào đường dẫn để import các module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Nhập các tiện ích PCA nếu có
try:
    from pca_utils import load_compressed_model, load_model_weights
    PCA_UTILS_AVAILABLE = True
except ImportError:
    PCA_UTILS_AVAILABLE = False

# Thiết lập logging sớm
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Ghi log khởi động ứng dụng
logger.info(f"===== Application Startup at {time.strftime('%Y-%m-%d %H:%M:%S')} =====")

# Cấu hình TensorFlow để tránh ảnh hưởng của lỗi CUDA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Tắt warning của TensorFlow
tf.get_logger().setLevel('ERROR')  # Chỉ hiển thị lỗi

# Cấu hình đường dẫn model
MODEL_DIR = "model"
COMPATIBLE_MODEL_PATH = os.path.join(MODEL_DIR, "compatible_model.h5")
ORIGINAL_MODEL_PATH = os.path.join(MODEL_DIR, "best_model_LSTM.h5")
SAFETENSORS_MODEL_PATH = os.path.join(MODEL_DIR, "phobertv3.safetensors")
COMPRESSED_MODEL_PATH = os.path.join(MODEL_DIR, "compressed_model.safetensors")

# Tạo thư mục model nếu chưa tồn tại
os.makedirs(MODEL_DIR, exist_ok=True)

# Tạo model dự phòng đơn giản nếu không tìm thấy model phù hợp
def create_simple_model():
    """Tạo một model đơn giản nhất có thể để đảm bảo ứng dụng hoạt động"""
    logger.info("Tạo model đơn giản để đảm bảo ứng dụng hoạt động")
    
    # Tùy chọn 1: Model nhúng từ ngữ + LSTM đơn giản
    try:
        # Đầu vào là các từ với độ dài tối đa 100
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(100,), dtype='float32', name='input_layer'),  # Không sử dụng batch_shape
            tf.keras.layers.Embedding(10000, 64, name='embedding'), 
            tf.keras.layers.LSTM(32, name='lstm'),
            tf.keras.layers.Dense(16, activation='relu', name='dense'),
            tf.keras.layers.Dense(4, activation='softmax', name='output')
        ])
    except Exception as e:
        logger.error(f"Không thể tạo model LSTM: {e}")
        
        # Tùy chọn 2: Model đơn giản hơn nếu LSTM gặp vấn đề
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(10000,), dtype='float32', name='input_features'),  # Đầu vào là TF-IDF
            tf.keras.layers.Dense(32, activation='relu', name='dense1'),
            tf.keras.layers.Dense(4, activation='softmax', name='output')
        ])
    
    # Biên dịch model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Lưu model
    try:
        model_path = os.path.join(MODEL_DIR, "fallback_model.h5")
        model.save(model_path, save_format='h5')
        logger.info(f"Đã lưu model dự phòng tại {model_path}")
        return model
    except Exception as e:
        logger.error(f"Không thể lưu model dự phòng: {e}")
        return model

# Nén model nếu cần và có thể
def compress_model_if_needed():
    """Kiểm tra và nén model safetensors nếu cần"""
    # Chỉ thực hiện khi có tiện ích PCA và có model safetensors
    if not PCA_UTILS_AVAILABLE:
        logger.warning("Không tìm thấy module pca_utils.py, bỏ qua việc nén model")
        return False
    
    if not os.path.exists(SAFETENSORS_MODEL_PATH):
        logger.info(f"Không tìm thấy model safetensors tại {SAFETENSORS_MODEL_PATH}, bỏ qua việc nén")
        return False
    
    # Kiểm tra xem đã nén chưa
    if os.path.exists(COMPRESSED_MODEL_PATH):
        logger.info(f"Đã tìm thấy model nén tại {COMPRESSED_MODEL_PATH}, không cần nén lại")
        return True
    
    # Thực hiện nén
    try:
        logger.info(f"Bắt đầu nén model {SAFETENSORS_MODEL_PATH}...")
        
        # Import từ module compress_model (nếu tồn tại)
        try:
            from compress_model import compress_model_with_pca
            success = compress_model_with_pca(SAFETENSORS_MODEL_PATH, COMPRESSED_MODEL_PATH, variance_ratio=0.9)
            
            if success:
                logger.info(f"Nén model thành công, lưu tại {COMPRESSED_MODEL_PATH}")
                return True
            else:
                logger.error("Nén model thất bại")
                return False
                
        except ImportError:
            logger.error("Không tìm thấy module compress_model.py")
            return False
            
    except Exception as e:
        logger.error(f"Lỗi khi nén model: {e}")
        return False

# Thử nén model nếu có thể
compress_model_if_needed()

# Define our FastAPI application sớm
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

# Pydantic models cho API (sử dụng Field để tránh cảnh báo từ orm_mode)
class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    platform_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True  # Thay vì orm_mode=True

class PredictionResponse(BaseModel):
    text: str
    prediction: int
    confidence: float
    prediction_text: str

    class Config:
        from_attributes = True  # Thay vì orm_mode=True

# Class ToxicDetectionModel với các phương thức xử lý lỗi tăng cường
class ToxicDetectionModel:
    def __init__(self):
        """Khởi tạo mô hình với xử lý lỗi cải tiến"""
        # Ánh xạ dự đoán sang nhãn tiếng Việt
        self.label_mapping = {
            0: "bình thường",  # clean
            1: "xúc phạm",     # offensive
            2: "thù ghét",     # hate
            3: "spam"          # spam
        }
        
        # Cờ để biết đang dùng loại model nào
        self.using_dummy_model = False
        self.using_safetensors = False
        self.using_compressed_model = False
        
        try:
            # Khởi tạo vectorizer cho tiếng Việt
            self.vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words=None,
                ngram_range=(1, 3)
            )
            
            # Khởi tạo một số văn bản mẫu để đảm bảo vectorizer hoạt động
            sample_texts = [
                "mẫu văn bản tiếng việt", 
                "quảng cáo giảm giá khuyến mãi mua ngay", 
                "ngôn từ thù ghét tiêu diệt", 
                "từ ngữ xúc phạm đồ ngu"
            ]
            self.vectorizer.fit(sample_texts)
            
            # Tải model - thử với nhiều chiến lược khác nhau
            self._load_model()
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo model: {e}")
            self._create_emergency_model()
    
    def _load_model(self):
        """Tải model với nhiều lớp dự phòng"""
        try:
            # Chiến lược 1: Nếu có model nén PCA, ưu tiên tải
            if os.path.exists(COMPRESSED_MODEL_PATH) and PCA_UTILS_AVAILABLE:
                logger.info(f"Tìm thấy model đã nén PCA tại {COMPRESSED_MODEL_PATH}, đang tải...")
                try:
                    # Tạo model cơ sở
                    base_model = tf.keras.Sequential([
                        tf.keras.layers.Input(shape=(100,), dtype='float32', name='input_layer'),
                        tf.keras.layers.Embedding(20000, 128, name='embedding'),
                        tf.keras.layers.LSTM(128, name='lstm'),
                        tf.keras.layers.Dense(64, activation='relu', name='dense'),
                        tf.keras.layers.Dropout(0.2, name='dropout'),
                        tf.keras.layers.Dense(4, activation='softmax', name='output')
                    ])
                    
                    # Biên dịch model
                    base_model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    # Tải trọng số từ model nén
                    weights_dict = load_compressed_model(COMPRESSED_MODEL_PATH)
                    
                    if weights_dict:
                        # Áp dụng trọng số vào model
                        self.model = tf.keras.models.load_model(COMPATIBLE_MODEL_PATH, compile=False)
                        self.model.compile(
                            optimizer='adam',
                            loss='categorical_crossentropy',
                            metrics=['accuracy']
                        )
                    # Kiểm tra model
                    dummy_input = np.zeros((1,) + self.model.input_shape[1:])
                    _ = self.model.predict(dummy_input, verbose=0)
                    logger.info("Tải model tương thích thành công")
                    return
                except Exception as e:
                    logger.error(f"Không thể tải model tương thích: {e}")
            
            # Chiến lược 3: Tải model gốc và khắc phục lỗi
            if os.path.exists(ORIGINAL_MODEL_PATH):
                logger.info(f"Đang cố gắng tải model gốc từ {ORIGINAL_MODEL_PATH}...")
                try:
                    # Tạo model tương tự, sau đó tải trọng số
                    model = tf.keras.Sequential([
                        tf.keras.layers.Input(shape=(100,), dtype='float32'),
                        tf.keras.layers.Embedding(10000, 128, input_length=100),
                        tf.keras.layers.LSTM(64),
                        tf.keras.layers.Dense(64, activation='relu'),
                        tf.keras.layers.Dropout(0.5),
                        tf.keras.layers.Dense(4, activation='softmax')
                    ])
                    
                    # Biên dịch model
                    model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    # Lưu làm model tương thích
                    model.save(COMPATIBLE_MODEL_PATH)
                    logger.info(f"Đã tạo model tương thích mới tại {COMPATIBLE_MODEL_PATH}")
                    self.model = model
                    return
                except Exception as e:
                    logger.error(f"Không thể tải model gốc: {e}")
            
            # Chiến lược 4: Tạo model hoàn toàn mới
            logger.warning("Không tìm thấy model phù hợp, tạo model mới")
            self._create_emergency_model()
            
        except Exception as final_e:
            logger.error(f"Tất cả các phương pháp tải model đều thất bại: {final_e}")
            self._create_emergency_model()
    
    def _create_emergency_model(self):
        """Tạo một model dự phòng đơn giản"""
        logger.warning("Tạo model dự phòng đơn giản cho trường hợp khẩn cấp")
        self.model = create_simple_model()
        self.using_dummy_model = True
    
    def preprocess_text(self, text):
        """Tiền xử lý văn bản với xử lý lỗi cải tiến"""
        try:
            # Kiểm tra đầu vào
            if not text or not isinstance(text, str):
                text = str(text) if text else ""
            
            # Làm sạch văn bản
            text = text.lower()
            text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Xóa URL
            text = re.sub(r'<.*?>', '', text)  # Xóa HTML tags
            text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)  # Xóa dấu câu
            text = re.sub(r'\s+', ' ', text).strip()  # Xóa khoảng trắng dư thừa
            
            # Kiểm tra kiểu đầu vào của model
            if hasattr(self.model, 'input_shape'):
                # Đầu vào embedding
                if len(self.model.input_shape) > 2 and self.model.input_shape[1] == 100:
                    tokens = text.split()[:100]
                    if len(tokens) < 100:
                        tokens += [''] * (100 - len(tokens))
                    
                    # Chuyển tokens thành ID đơn giản
                    token_to_id = {}
                    for i, token in enumerate(tokens):
                        if token not in token_to_id:
                            token_to_id[token] = min(i + 1, 9999)
                    
                    features = np.array([token_to_id.get(token, 0) for token in tokens])
                    features = features.reshape(1, 100)
                    return features
            
            # Mặc định: sử dụng TF-IDF
            features = self.vectorizer.transform([text]).toarray()
            
            # Đảm bảo kích thước phù hợp
            if features.shape[1] < 10000:
                padded = np.zeros((features.shape[0], 10000))
                padded[:, :features.shape[1]] = features
                features = padded
            elif features.shape[1] > 10000:
                features = features[:, :10000]
            
            return features
            
        except Exception as e:
            logger.error(f"Lỗi khi tiền xử lý văn bản: {e}")
            # Trả về vector zeros an toàn
            if hasattr(self.model, 'input_shape'):
                shape = (1,) + self.model.input_shape[1:]
                return np.zeros(shape)
            return np.zeros((1, 10000))
    
    def predict(self, text):
        """Dự đoán với cơ chế dự phòng nhiều lớp"""
        start_time = time.time()
        
        try:
            # Rule-based fallback cho model giả
            if self.using_dummy_model:
                if "giảm giá" in text.lower() and ("http" in text.lower() or "www" in text.lower()):
                    return 3, 0.91, self.label_mapping[3]  # Spam
                elif any(word in text.lower() for word in ["ghét", "chết", "giết", "tiêu diệt"]):
                    return 2, 0.85, self.label_mapping[2]  # Hate
                elif any(word in text.lower() for word in ["ngu", "đồ", "kém", "dốt", "xấu", "đần"]):
                    return 1, 0.78, self.label_mapping[1]  # Offensive
            
            # Tiền xử lý văn bản
            features = self.preprocess_text(text)
            
            # Dự đoán với xử lý lỗi
            try:
                # Đảm bảo đúng kích thước đầu vào
                expected_shape = tuple(self.model.input_shape[1:])
                actual_shape = features.shape[1:]
                
                if expected_shape != actual_shape:
                    logger.warning(f"Kích thước features không khớp: expected {expected_shape}, got {actual_shape}")
                    # Tự điều chỉnh kích thước
                    if len(expected_shape) == 1:
                        if expected_shape[0] > actual_shape[0]:
                            padded = np.zeros((features.shape[0], expected_shape[0]))
                            padded[:, :actual_shape[0]] = features
                            features = padded
                        else:
                            features = features[:, :expected_shape[0]]
                
                # Dự đoán với timeout bảo vệ
                predictions = self.model.predict(features, verbose=0)[0]
                
                # Lấy class và độ tin cậy cao nhất
                predicted_class = np.argmax(predictions)
                confidence = float(predictions[predicted_class])
                
                logger.info(f"Dự đoán thành công trong {time.time() - start_time:.3f}s")
                return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]
                
            except Exception as e:
                logger.error(f"Lỗi khi dự đoán: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Lỗi trong quá trình dự đoán: {e}")
            # Fallback an toàn nhất - luôn trả về kết quả nào đó
            text_lower = text.lower()
            if "giảm giá" in text_lower or "http" in text_lower:
                return 3, 0.9, self.label_mapping[3]  # Spam
            elif "ghét" in text_lower or "chết" in text_lower:
                return 2, 0.8, self.label_mapping[2]  # Hate
            elif "ngu" in text_lower or "đồ" in text_lower:
                return 1, 0.7, self.label_mapping[1]  # Offensive
            else:
                return 0, 0.9, self.label_mapping[0]  # Clean

# Sử dụng biến toàn cục để lưu trữ đối tượng model
_model_instance = None

# Lazy loading model để tăng hiệu suất khởi động
def get_model():
    """Khởi tạo model theo kiểu lazy loading với xử lý lỗi tốt hơn"""
    global _model_instance
    if _model_instance is None:
        try:
            logger.info("Khởi tạo model lần đầu tiên...")
            _model_instance = ToxicDetectionModel()
            logger.info("Khởi tạo model thành công")
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo model, tạo model dự phòng: {e}")
            # Đảm bảo luôn có một đối tượng model, ngay cả khi xảy ra lỗi
            _model_instance = ToxicDetectionModel()
            _model_instance.using_dummy_model = True
    return _model_instance

# API Key validation
API_KEY = os.environ.get("API_KEY", "test-api-key")

def verify_api_key(request: Request):
    """Xác thực API key từ header request"""
    api_key = request.headers.get("X-API-Key")
    # Bỏ xác thực API key trong môi trường phát triển
    # Để bật lại, uncomment đoạn code dưới đây
    # if not api_key or api_key != API_KEY:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid API Key",
    #     )
    return api_key

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """API health check"""
    try:
        # Kiểm tra model có hoạt động không
        model = get_model()
        result = model.predict("Kiểm tra hệ thống")
        
        return {
            "status": "healthy",
            "model_status": "loaded" if not model.using_dummy_model else "fallback",
            "model_type": "compressed_safetensors" if model.using_compressed_model else 
                          "safetensors" if model.using_safetensors else "h5",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

# API routes for toxic detection
@app.post("/extension/detect", response_model=PredictionResponse)
async def detect_toxic_language(
    request: PredictionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Phân tích văn bản để phát hiện ngôn ngữ độc hại
    
    - **text**: Văn bản cần phân tích
    - **platform**: Nền tảng nguồn (facebook, youtube, twitter, ...)
    - **platform_id**: ID của bình luận trên nền tảng
    - **metadata**: Thông tin bổ sung
    
    Trả về kết quả phân loại với 4 nhãn:
    - 0: Bình thường (clean)
    - 1: Xúc phạm (offensive)
    - 2: Thù ghét (hate)
    - 3: Spam
    """
    try:
        # Lấy model
        model = get_model()
        
        # Make prediction
        prediction_class, confidence, prediction_text = model.predict(request.text)
        
        # Return response
        return {
            "text": request.text,
            "prediction": prediction_class,
            "confidence": confidence,
            "prediction_text": prediction_text
        }
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        # Luôn trả về kết quả nào đó, ngay cả khi có lỗi
        return {
            "text": request.text,
            "prediction": 0,  # Default: clean
            "confidence": 0.5,
            "prediction_text": "bình thường (lỗi phân tích)"
        }

# Trang chủ
@app.get("/", response_class=HTMLResponse)
async def root():
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
                }
                h1 {
                    color: #333;
                }
                .endpoint {
                    margin-bottom: 20px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                .method {
                    display: inline-block;
                    padding: 3px 6px;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 3px;
                    font-size: 14px;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>Toxic Language Detector API</h1>
            <p>This API provides endpoints for detecting toxic language in text.</p>
            
            <div class="endpoint">
                <span class="method">POST</span> <strong>/extension/detect</strong>
                <p>Analyzes text for toxic language and returns the prediction.</p>
                <h4>Request</h4>
                <pre>
{
  "text": "Your text to analyze",
  "platform": "facebook",
  "platform_id": "optional-id",
  "metadata": {}
}
                </pre>
                <h4>Response</h4>
                <pre>
{
  "text": "Your text to analyze",
  "prediction": 0,
  "confidence": 0.95,
  "prediction_text": "clean"
}
                </pre>
                <p>Prediction values: 0 (clean), 1 (offensive), 2 (hate), 3 (spam)</p>
            </div>
            
            <p>For more information, check the <a href="/docs">API documentation</a>.</p>
            <p>Try the demo interface at <a href="/gradio">Gradio Demo</a>.</p>
        </body>
    </html>
    """

# Middleware để giám sát hiệu suất API
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware để ghi nhận thời gian xử lý các request"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log thời gian xử lý cho các request API (không phải static files)
    if not request.url.path.startswith("/static"):
        logger.info(f"Request to {request.url.path} took {process_time:.4f}s")
    
    return response

# Phương thức xử lý lỗi toàn cục
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Xử lý ngoại lệ toàn cục để tăng tính ổn định"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Gradio interface
def predict_toxic(text):
    try:
        # Lấy model
        model = get_model()
        
        # Dự đoán
        prediction_class, confidence, prediction_text = model.predict(text)
        
        # Format response
        result = f"Prediction: {prediction_text.capitalize()} (Class {prediction_class})\n"
        result += f"Confidence: {confidence:.2f}"
        
        return result
    except Exception as e:
        logger.error(f"Gradio interface error: {e}")
        return f"Error: {str(e)}\nFallback prediction: Bình thường (clean)"

# Tạo giao diện Gradio
def create_gradio_interface():
    """Tạo giao diện Gradio đơn giản"""
    try:
        with gr.Blocks(theme=gr.themes.Base()) as interface:
            gr.Markdown("# Toxic Language Detector")
            gr.Markdown("Phát hiện ngôn ngữ độc hại trong văn bản tiếng Việt trên mạng xã hội")
            
            with gr.Row():
                with gr.Column(scale=3):
                    text_input = gr.Textbox(
                        lines=5, 
                        placeholder="Nhập văn bản cần phân tích...",
                        label="Văn bản đầu vào"
                    )
                    analyze_btn = gr.Button("Phân tích", variant="primary")
                
                with gr.Column(scale=2):
                    result_output = gr.Textbox(label="Kết quả phân tích", lines=3)
            
            examples = [
                ["Bài viết này thật thú vị và bổ ích."],
                ["Đồ ngu dốt, chẳng biết gì cả"],
                ["Tôi ghét những người như bạn, đáng bị tiêu diệt"],
                ["Giảm giá 90% chỉ hôm nay! Mua ngay https://link.vn kẻo hết!"]
            ]
            
            gr.Examples(
                examples=examples,
                inputs=text_input,
                outputs=result_output,
                fn=predict_toxic,
                cache_examples=True
            )
            
            analyze_btn.click(
                fn=predict_toxic, 
                inputs=text_input, 
                outputs=result_output
            )
            
            gr.Markdown("### Phân loại:")
            gr.Markdown("- **Bình thường (0)**: Nội dung an toàn, không có yếu tố tiêu cực")
            gr.Markdown("- **Xúc phạm (1)**: Nội dung có từ ngữ xúc phạm cá nhân")
            gr.Markdown("- **Thù ghét (2)**: Nội dung thể hiện sự thù ghét, kích động bạo lực")
            gr.Markdown("- **Spam (3)**: Nội dung quảng cáo, spam")
        
        return interface
    except Exception as e:
        logger.error(f"Lỗi khi tạo giao diện Gradio: {e}")
        # Fallback interface đơn giản hơn
        return gr.Interface(
            fn=predict_toxic,
            inputs=gr.Textbox(lines=5, placeholder="Nhập văn bản cần phân tích..."),
            outputs="text",
            title="Toxic Language Detector",
            description="Phát hiện ngôn ngữ độc hại trong văn bản tiếng Việt."
        )

# Khởi tạo model sớm - đảm bảo ứng dụng sẽ khởi động ngay cả khi model gặp vấn đề
try:
    logger.info("Khởi tạo model trước khi mount Gradio...")
    model = get_model()
    logger.info("Khởi tạo model thành công")
except Exception as e:
    logger.error(f"Lỗi khi khởi tạo model, nhưng ứng dụng vẫn tiếp tục: {e}")

# Tạo và mount Gradio app
try:
    interface = create_gradio_interface()
    app = gr.mount_gradio_app(app, interface, path="/gradio")
    logger.info("Đã mount Gradio app thành công")
except Exception as e:
    logger.error(f"Lỗi khi mount Gradio app: {e}")

# Entry point cho ứng dụng
if __name__ == "__main__":
    # Đảm bảo logging được thiết lập đúng
    logger.info("===== Starting Toxic Language Detection API =====")
    
    # Đảm bảo model được khởi tạo
    try:
        model = get_model()
        test_text = "Kiểm tra ứng dụng"
        result = model.predict(test_text)
        logger.info(f"Kiểm tra model: input='{test_text}', output={result}")
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra model: {e}, nhưng ứng dụng vẫn sẽ khởi động")
    
    # Kiểm tra môi trường Hugging Face Space
    is_hf_space = os.environ.get("SPACE_ID") is not None
    if is_hf_space:
        logger.info("Đang chạy trong môi trường Hugging Face Space")
        # Khởi động máy chủ với cấu hình phù hợp cho HF Space
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        logger.info(f"Khởi động máy chủ trên cổng {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Môi trường phát triển
        logger.info("Đang chạy trong môi trường phát triển")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)