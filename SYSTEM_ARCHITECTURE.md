# KIẾN TRÚC VÀ LUỒNG HOẠT ĐỘNG HỆ THỐNG TOXIC LANGUAGE DETECTOR

## 📋 MỤC LỤC
1. [Tổng quan hệ thống](#tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
3. [Các thành phần chính](#các-thành-phần-chính)
4. [Luồng dữ liệu](#luồng-dữ-liệu)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Mô hình ML](#mô-hình-ml)
8. [Authentication Flow](#authentication-flow)

---

## 🎯 TỔNG QUAN HỆ THỐNG

### Mục đích
Hệ thống **Toxic Language Detector** là một giải pháp toàn diện để phát hiện và phân loại ngôn từ tiêu cực trên các nền tảng mạng xã hội (Facebook, YouTube, Twitter, TikTok, Zalo).

### Phân loại ngôn từ
Hệ thống phân loại văn bản thành 4 nhãn:
- **0: Clean (Bình thường)** - Nội dung không có vấn đề
- **1: Offensive (Xúc phạm)** - Nội dung xúc phạm, mạng miệng
- **2: Hate (Thù ghét)** - Ngôn từ thù ghét, kích động
- **3: Spam** - Nội dung spam, quảng cáo rác

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────────┐
│                      HỆ THỐNG TOXIC LANGUAGE DETECTOR            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   EXTENSION  │      │   BACKEND    │      │  WEB         │  │
│  │   (Chrome)   │◄────►│   (FastAPI)  │◄────►│  DASHBOARD   │  │
│  │              │      │              │      │  (Laravel)   │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                     │           │
│         │                      │                     │           │
│         ▼                      ▼                     ▼           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               POSTGRESQL/SQLITE DATABASE                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  ML MODELS (TensorFlow)                   │  │
│  │  • LSTM         • CNN          • GRU                      │  │
│  │  • BERT         • PhoBERT      • BERT4News                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 CÁC THÀNH PHẦN CHÍNH

### 1. BACKEND API (FastAPI)

#### Cấu trúc thư mục
```
backend/
├── api/
│   ├── routes/           # API endpoints
│   │   ├── admin.py      # Quản trị hệ thống
│   │   ├── auth.py       # Authentication
│   │   ├── extension.py  # API cho extension
│   │   ├── prediction.py # API dự đoán
│   │   ├── feedback.py   # API feedback
│   │   └── toxic_detection.py
│   └── models/           # Pydantic models
│       └── prediction.py
├── config/
│   ├── settings.py       # Cấu hình hệ thống
│   └── security.py       # JWT, password hashing
├── core/
│   ├── dependencies.py   # Dependency injection
│   ├── middleware.py     # Logging, CORS, Rate limiting
│   └── security.py       # Security utilities
├── db/
│   └── models/           # SQLAlchemy models
│       ├── user.py
│       ├── role.py
│       ├── comment.py
│       ├── log.py
│       ├── report.py
│       └── permission.py
├── services/
│   ├── ml_model.py       # ML Model service
│   ├── model_adapter.py  # Adapter cho nhiều loại model
│   ├── email.py          # Email service
│   ├── social_media.py   # Social media API integration
│   └── user_service.py
└── utils/
    ├── text_processing.py   # Tiền xử lý văn bản
    ├── vector_utils.py      # Vector embedding
    └── rate_limiter.py
```

#### Các model ML được hỗ trợ
1. **LSTM** (Long Short-Term Memory) - Model mặc định
2. **CNN** (Convolutional Neural Network)
3. **GRU** (Gated Recurrent Unit)
4. **BERT** (Bidirectional Encoder Representations from Transformers)
5. **PhoBERT** - BERT được train trên tiếng Việt
6. **BERT4News** - BERT cho văn bản tin tức tiếng Việt

#### Tính năng chính
- **Authentication**: JWT-based authentication + Basic Auth
- **Rate Limiting**: Giới hạn request để tránh spam
- **Logging**: Ghi log tất cả requests và responses
- **Vector Search**: Tìm kiếm comments tương tự
- **Batch Processing**: Xử lý hàng loạt comments
- **Real-time Analysis**: Phân tích real-time từ extension

### 2. CHROME EXTENSION

#### Cấu trúc
```
extension/
├── manifest.json         # Extension config
├── background.js         # Service worker
├── content.js            # Content script
├── styles.css            # CSS cho UI overlay
├── popup/
│   ├── popup.html        # Popup UI
│   ├── popup.js          # Popup logic
│   ├── popup.css         # Popup styling
│   └── chart-loader.js   # Chart visualization
└── icons/                # Extension icons
```

#### Chức năng chính

**background.js**:
- Quản lý API calls
- Xử lý batch detection (100 comments/lần)
- Lưu trữ authentication tokens
- Quản lý settings
- Buffer comments để xử lý batch

**content.js**:
- Detect platform (Facebook, YouTube, Twitter, TikTok, Zalo)
- Scan comments trên trang
- Apply visual indicators (màu sắc, blur)
- Mutation Observer để theo dõi comments mới
- Report incorrect analysis

**popup.js**:
- Quản lý UI settings
- Xác thực người dùng
- Phân tích text trực tiếp
- Batch analysis
- Hiển thị statistics
- Theme switching (light/dark/auto)

#### Features
1. **Real-time Detection**: Tự động quét comments khi browse
2. **Visual Indicators**: Màu sắc khác nhau cho từng loại
   - 🟢 Green: Clean
   - 🟠 Orange: Offensive
   - 🔴 Red: Hate
   - 🟣 Purple: Spam
3. **Content Blur**: Tự động blur nội dung hate speech
4. **User Feedback**: Báo cáo phân tích sai
5. **Statistics**: Theo dõi số lượng comments đã quét
6. **Multi-model**: Chọn model phân tích (LSTM, BERT, etc.)

### 3. WEB DASHBOARD (Laravel)

#### Cấu trúc modules
```
webdashboard/modules/
├── Admin/                # Module quản trị
│   ├── Controllers/
│   │   └── DashboardController.php
│   └── Resources/
│       ├── views/        # Dashboard views
│       └── assets/       # CSS, JS, Images
├── User/                 # Module người dùng
│   ├── Controllers/
│   │   ├── AuthController.php
│   │   └── UserController.php
│   └── Entities/
│       ├── User.php
│       └── Role.php
├── Comment/              # Module comments
│   ├── Controllers/
│   │   └── CommentController.php
│   └── Entities/
│       └── Comment.php
├── Prediction/           # Module prediction
│   └── Controllers/
│       └── PredictionController.php
├── Statistics/           # Module thống kê
│   └── Controllers/
│       └── StatisticsController.php
└── Log/                  # Module logs
    └── Controllers/
        └── LogController.php
```

#### Chức năng
1. **Dashboard**: Tổng quan thống kê
2. **User Management**: Quản lý người dùng, roles, permissions
3. **Comment Management**: Xem, filter, export comments
4. **Analytics**: Biểu đồ, reports, trends
5. **Settings**: Cấu hình hệ thống
6. **Logs**: Xem logs hoạt động

---

## 🔄 LUỒNG DỮ LIỆU

### 1. Luồng Phân Tích Comment từ Extension

```
┌──────────────┐
│  User Browse │
│  Social      │
│  Media       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Content      │  ◄─── MutationObserver detect new comments
│ Script       │
│ (content.js) │
└──────┬───────┘
       │ Collect comments
       ▼
┌──────────────┐
│ Background   │  ◄─── Buffer comments (max 100)
│ Service      │       Timeout: 2s
│ (background) │
└──────┬───────┘
       │ Send batch request
       ▼
┌──────────────────────────────┐
│ Backend API                  │
│ /extension/batch-detect      │
│                              │
│  1. Preprocess text          │
│  2. Extract features         │
│  3. ML Model prediction      │
│  4. Apply spam heuristics    │
│  5. Save to DB (if logged)   │
└──────┬───────────────────────┘
       │ Return results
       ▼
┌──────────────┐
│ Content      │
│ Script       │  ◄─── Apply visual indicators
│              │       - Border colors
│              │       - Blur (hate speech)
│              │       - Report button
└──────────────┘
```

### 2. Luồng Phân Tích Trực Tiếp từ Popup

```
┌──────────────┐
│ User Input   │
│ Text in      │
│ Popup        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ popup.js     │
│ analyzeText()│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Backend API                  │
│ /extension/detect            │
│                              │
│  1. Validate input           │
│  2. Get model_type           │
│  3. Load model               │
│  4. Preprocess text          │
│  5. Predict                  │
│  6. Return probabilities     │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────┐
│ Display      │
│ Results      │  ◄─── Show category, confidence
│              │       Show progress bars
│              │       Show keywords
└──────────────┘
```

### 3. Luồng Xác Thực

```
┌──────────────┐
│ User Login   │
│ (popup)      │
└──────┬───────┘
       │ username, password
       ▼
┌──────────────────────────────┐
│ Backend API                  │
│ /auth/token                  │
│                              │
│  1. Verify credentials       │
│  2. Generate JWT token       │
│  3. Update last_login        │
│  4. Create log entry         │
└──────┬───────────────────────┘
       │ Return access_token
       ▼
┌──────────────┐
│ Save Token   │  ◄─── chrome.storage.local
│ + User Info  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Update UI    │  ◄─── Show profile
│              │       Enable auth-required tabs
│              │       Enable batch mode
└──────────────┘
```

---

## 🗄️ DATABASE SCHEMA

### Các bảng chính

#### 1. **users**
```sql
- id: INTEGER (PK)
- username: STRING(50) UNIQUE
- email: STRING(100) UNIQUE
- name: STRING(100)
- hashed_password: STRING(255)
- is_active: BOOLEAN
- is_verified: BOOLEAN
- role_id: INTEGER (FK -> roles)
- last_login: TIMESTAMP
- last_activity: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 2. **roles**
```sql
- id: INTEGER (PK)
- name: STRING(50) UNIQUE
- description: TEXT
- created_at: TIMESTAMP
```

#### 3. **comments**
```sql
- id: INTEGER (PK)
- content: TEXT
- processed_content: TEXT
- platform: STRING(50)
- source_user_name: STRING(255)
- source_url: TEXT
- prediction: INTEGER (0-3)
- confidence: FLOAT
- probabilities: TEXT (JSON)
- vector_representation: TEXT (JSON)
- user_id: INTEGER (FK -> users)
- meta_data: JSON
- is_reviewed: BOOLEAN
- created_at: TIMESTAMP
```

#### 4. **logs**
```sql
- id: INTEGER (PK)
- user_id: INTEGER (FK -> users)
- action: STRING
- request_path: STRING
- request_method: STRING
- response_status: INTEGER
- client_ip: STRING
- timestamp: TIMESTAMP
```

#### 5. **permissions**
```sql
- id: INTEGER (PK)
- code: STRING UNIQUE
- name: STRING
- description: TEXT
```

#### 6. **role_permissions**
```sql
- role_id: INTEGER (FK -> roles)
- permission_id: INTEGER (FK -> permissions)
```

---

## 🔌 API ENDPOINTS

### Extension Endpoints

#### `POST /extension/detect`
Phân tích một comment đơn lẻ
```json
Request:
{
  "text": "string",
  "platform": "facebook|youtube|twitter",
  "save_to_db": boolean,
  "model_type": "lstm|bert|phobert|..."
}

Response:
{
  "text": "string",
  "prediction": 0-3,
  "confidence": 0.0-1.0,
  "prediction_text": "clean|offensive|hate|spam",
  "probabilities": {
    "clean": 0.0-1.0,
    "offensive": 0.0-1.0,
    "hate": 0.0-1.0,
    "spam": 0.0-1.0
  },
  "timestamp": "ISO8601"
}
```

#### `POST /extension/batch-detect`
Phân tích hàng loạt comments
```json
Request:
{
  "items": [
    {
      "text": "string",
      "platform": "string",
      ...
    }
  ],
  "save_to_db": boolean,
  "store_clean": boolean,
  "model_type": "string"
}

Response:
{
  "results": [...],
  "count": integer,
  "timestamp": "ISO8601"
}
```

#### `GET /extension/stats?period=day|week|month|all`
Lấy thống kê (yêu cầu auth)

### Auth Endpoints

#### `POST /auth/register`
Đăng ký người dùng mới

#### `POST /auth/token`
Đăng nhập (form data: username, password)

#### `GET /auth/me`
Lấy thông tin user hiện tại

#### `POST /auth/logout`
Đăng xuất

### Admin Endpoints (Yêu cầu role admin)

#### `GET /admin/dashboard`
Dashboard data

#### `GET /admin/users`
Danh sách users

#### `GET /admin/comments`
Danh sách comments với filters

#### `GET /admin/logs`
System logs

---

## 🤖 MÔ HÌNH ML

### Kiến trúc MLModel Class

```python
class MLModel:
    def __init__(self):
        self.model_path = settings.MODEL_PATH
        self.tokenizer = None
        self.model = None
        self.max_length = 100
        self.max_words = 20000
        self.labels = ["clean", "offensive", "hate", "spam"]
        
    def load_model(self):
        # Hỗ trợ nhiều loại model:
        # - .h5 files (Keras)
        # - .safetensors files
        # - Transformer models
        
    def preprocess(self, text):
        # 1. Lowercase
        # 2. Remove URLs, HTML tags
        # 3. Vietnamese tokenization (underthesea)
        # 4. Tokenize và pad sequences
        # 5. Return processed input
        
    def predict(self, text, model_type=None):
        # 1. Preprocess text
        # 2. Load specific model if model_type provided
        # 3. Get predictions
        # 4. Apply spam detection heuristics
        # 5. Return (class, confidence, probabilities)
```

### Spam Detection Heuristics

Ngoài ML model, hệ thống áp dụng các rule-based heuristics:

```python
spam_features = {
    'has_url': bool,
    'has_suspicious_url': bool,
    'url_count': int,
    'spam_keyword_count': int,
    'has_excessive_punctuation': bool,
    'has_all_caps_words': bool
}

# Tính spam_score dựa trên features
# Nếu spam_score > 0.5 và model confidence < 0.8
# → Override prediction thành Spam
```

### Model Files Structure

```
model/
├── best_model_LSTM.h5          # LSTM model chính
├── tokenizer.pkl               # Keras tokenizer
├── config.json                 # Model configuration
├── model.safetensors           # Safetensors format
├── cnn/
│   └── text_cnn_model.h5
├── grn/
│   └── gru_model.h5
├── bert/
│   ├── config_bert.json
│   └── model_bert.safetensors
├── phobert/
│   └── model_phobert.safetensors
└── bert4news/
    └── model_bert4news.safetensors
```

---

## 🔐 AUTHENTICATION FLOW

### JWT Token Flow

```
1. User login → Backend verifies credentials
2. Backend generates JWT token with:
   - sub: username
   - role: user role
   - exp: expiration time
3. Token saved to chrome.storage
4. Subsequent requests include: Authorization: Bearer <token>
5. Backend verifies token on each request
6. Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 1440 = 24h)
```

### Extension API Key (Backward compatibility)

Extension cũng hỗ trợ API key authentication:
- Header: `X-API-Key: <api_key>`
- Dùng cho service account
- Không hết hạn như JWT

### Permission System

```
roles -> role_permissions <- permissions
   │                             │
   └──────── users ──────────────┘
   
Permissions:
- view_dashboard
- manage_users
- view_reports
- create_reports
- manage_settings
- export_data
- view_statistics
- analyze_text
```

---

## 📊 TEXT PREPROCESSING PIPELINE

```
Input Text
    │
    ▼
1. Lowercase
    │
    ▼
2. Remove URLs
    │
    ▼
3. Remove HTML tags
    │
    ▼
4. Remove/normalize punctuation
    │
    ▼
5. Vietnamese tokenization (underthesea)
    │
    ▼
6. Remove stopwords (optional)
    │
    ▼
7. Tokenize with Keras Tokenizer
    │
    ▼
8. Pad sequences to max_length
    │
    ▼
9. Create vector representation (TF-IDF hoặc embedding)
    │
    ▼
Output: Processed input ready for model
```

---

## 🌐 SETTINGS & CONFIGURATION

### Backend Settings (settings.py)

```python
# API Settings
PROJECT_NAME = "Vietnamese Toxic Language Detector"
API_V1_STR = "/api/v1"
DEBUG = bool

# Server
HOST = "0.0.0.0"
PORT = 7860

# Security
SECRET_KEY = str
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Database
DATABASE_URL = "sqlite:///./toxic_detector.db"

# ML Model
MODEL_PATH = "model/model.safetensors"
MODEL_DEVICE = "cpu"
MODEL_LABELS = ["clean", "offensive", "hate", "spam"]

# Rate Limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 60  # seconds

# Email
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = str
MAIL_PASSWORD = str
```

### Extension Settings

```javascript
{
  enabled: true,
  threshold: 0.7,
  highlightToxic: true,
  saveData: true,
  modelType: 'lstm',
  platforms: {
    facebook: true,
    youtube: true,
    twitter: true,
    tiktok: false,
    zalo: false
  },
  displayOptions: {
    showClean: true,
    showOffensive: true,
    showHate: true,
    showSpam: true
  },
  theme: 'auto'  // light|dark|auto
}
```

---

## 🚀 DEPLOYMENT

### Backend Deployment

1. **Local Development**:
   ```bash
   uvicorn app:app --reload --port 7860
   ```

2. **Production (Docker)**:
   ```dockerfile
   FROM python:3.9
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

3. **Hugging Face Spaces**:
   - Sử dụng file `app.py` làm entry point
   - Cấu hình SDK: gradio
   - Mount FastAPI vào Gradio

### Extension Deployment

1. **Development**:
   - Load unpacked trong Chrome extensions
   - Developer mode enabled

2. **Production**:
   - Đóng gói thành .zip
   - Upload lên Chrome Web Store
   - Review và publish

---

## 🔧 TROUBLESHOOTING

### Common Issues

1. **Model không load được**:
   - Check file paths
   - Verify model format (.h5 hoặc .safetensors)
   - Check TensorFlow version compatibility

2. **Extension không detect comments**:
   - Check platform detection
   - Verify content script injection
   - Check MutationObserver configuration
   - Inspect console logs

3. **API 401 Unauthorized**:
   - Token expired → Re-login
   - Invalid API key
   - User account disabled

4. **Batch processing timeout**:
   - Reduce BATCH_SIZE
   - Increase timeout duration
   - Check server resources

---

## 📈 FUTURE IMPROVEMENTS

1. **Model Training Pipeline**:
   - Tự động retrain model với feedback data
   - A/B testing multiple models

2. **Real-time Monitoring**:
   - Dashboard real-time analytics
   - Alert system for toxic content spikes

3. **Multi-language Support**:
   - Extend beyond Vietnamese
   - Language detection

4. **Advanced Features**:
   - Sentiment analysis
   - Intent detection
   - Contextual understanding
   - User reputation system

5. **Performance Optimization**:
   - Model quantization
   - Edge deployment
   - Caching strategies

---

## 📚 REFERENCES

- FastAPI Documentation: https://fastapi.tiangolo.com/
- TensorFlow: https://www.tensorflow.org/
- Chrome Extension Development: https://developer.chrome.com/docs/extensions/
- Laravel Modules: https://nwidart.com/laravel-modules/
- SQLAlchemy: https://www.sqlalchemy.org/
- underthesea (Vietnamese NLP): https://github.com/undertheseanlp/underthesea

---

*Tài liệu được tạo tự động bởi AI Assistant*
*Ngày tạo: 2025-10-19*

