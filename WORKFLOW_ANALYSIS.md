# PHÂN TÍCH CHI TIẾT CÁC LUỒNG HOẠT ĐỘNG

## 📋 MỤC LỤC
1. [Luồng Extension Scanning](#luồng-extension-scanning)
2. [Luồng Batch Processing](#luồng-batch-processing)
3. [Luồng Authentication](#luồng-authentication)
4. [Luồng ML Prediction](#luồng-ml-prediction)
5. [Luồng User Feedback](#luồng-user-feedback)
6. [Luồng Admin Dashboard](#luồng-admin-dashboard)

---

## 🔍 1. LUỒNG EXTENSION SCANNING

### Mục đích
Tự động quét và phân loại comments trên các trang mạng xã hội khi người dùng browse.

### Chi tiết từng bước

#### Bước 1: Platform Detection (content.js)
```javascript
// Xác định platform hiện tại
let currentPlatform = '';
if (window.location.hostname.includes("facebook.com")) {
  currentPlatform = PLATFORMS.FACEBOOK;
} else if (window.location.hostname.includes("youtube.com")) {
  currentPlatform = PLATFORMS.YOUTUBE;
} else if (window.location.hostname.includes("twitter.com")) {
  currentPlatform = PLATFORMS.TWITTER;
}
```

**Output**: `currentPlatform` variable được set

---

#### Bước 2: Start MutationObserver
```javascript
commentObserver = new MutationObserver((mutations) => {
  const commentSelectors = getCommentSelectors();
  
  for (const mutation of mutations) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const comments = node.matches(commentSelectors) ? 
            [node] : Array.from(node.querySelectorAll(commentSelectors));
          
          for (const comment of comments) {
            processComment(comment);
          }
        }
      }
    }
  }
});
```

**Comment Selectors** cho từng platform:
- **Facebook**: `.x1y1aw1k div[dir="auto"]`
- **YouTube**: `ytd-comment-renderer #content-text`
- **Twitter**: `[data-testid="tweetText"]`

---

#### Bước 3: Process Comment
```javascript
function processComment(commentElement) {
  const commentId = getCommentId(commentElement);
  
  // Skip if already processed
  if (processedComments.has(commentId)) return;
  processedComments.add(commentId);
  
  // Get comment text
  const commentText = getCommentText(commentElement);
  if (!commentText || commentText.trim().length < 5) return;
  
  // Send to background for analysis
  chrome.runtime.sendMessage({
    action: "analyzeText",
    text: commentText,
    platform: currentPlatform,
    commentId: commentId
  }, (response) => {
    if (response && !response.error) {
      applyToxicityIndicator(commentElement, response);
    }
  });
}
```

**Key Points**:
- Comments được track bằng `processedComments` Set để tránh process duplicate
- Minimum length: 5 characters
- Async communication với background script

---

#### Bước 4: Buffer Comments (background.js)

```javascript
let commentsBuffer = [];
const BATCH_SIZE = 100;
let batchProcessingTimeout = null;

function addToBuffer(text, platform, commentId, sourceUrl) {
  return new Promise((resolve, reject) => {
    const commentIdentifier = `${platform}_${commentId}`;
    
    // Check duplicate
    if (commentsBuffer.findIndex(item => 
      item.identifier === commentIdentifier) >= 0) {
      resolve({ status: "buffered" });
      return;
    }
    
    // Add to buffer
    commentsBuffer.push({
      text, platform, 
      platform_id: commentId,
      source_url: sourceUrl,
      identifier: commentIdentifier,
      resolve, reject
    });
    
    // Process if batch is full
    if (commentsBuffer.length >= BATCH_SIZE) {
      clearTimeout(batchProcessingTimeout);
      processCommentsBatch();
    } else if (!batchProcessingTimeout) {
      // Set timeout nếu chưa đủ batch
      batchProcessingTimeout = setTimeout(() => {
        processCommentsBatch();
        batchProcessingTimeout = null;
      }, 2000); // 2 seconds
    }
  });
}
```

**Batch Strategy**:
- **BATCH_SIZE**: 100 comments
- **Timeout**: 2 giây nếu không đủ batch
- **Rationale**: Giảm số lượng API calls, tăng performance

---

#### Bước 5: Send Batch Request
```javascript
async function processCommentsBatch() {
  const batchToProcess = [...commentsBuffer];
  commentsBuffer = []; // Reset buffer
  
  const batchItems = batchToProcess.map(item => ({
    text: item.text,
    platform: item.platform,
    platform_id: item.platform_id,
    source_url: item.source_url,
    metadata: item.metadata
  }));
  
  // Call API
  const response = await fetch(`${API_ENDPOINT}/extension/batch-detect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Basic ${BASIC_AUTH_TOKEN}`
    },
    body: JSON.stringify({
      items: batchItems,
      store_clean: false,
      save_to_db: false
    })
  });
  
  const batchResult = await response.json();
  
  // Map results và resolve promises
  batchToProcess.forEach(item => {
    const result = resultsMap[item.identifier];
    if (result) {
      item.resolve(result);
    }
  });
}
```

---

#### Bước 6: Backend Processing (backend/api/routes/extension.py)

```python
@router.post("/batch-detect", response_model=BatchPredictionResponse)
async def extension_batch_detect(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    results = []
    
    for item in request.items:
        # Predict
        prediction, confidence, probabilities = ml_model.predict(
            item['text'], 
            model_type=request.model_type
        )
        
        prediction_text = {
            0: "bình thường", 
            1: "xúc phạm", 
            2: "thù ghét", 
            3: "spam"
        }[prediction]
        
        # Save to DB if needed
        if request.save_to_db and (prediction != 0 or request.store_clean):
            background_tasks.add_task(
                store_extension_prediction,
                db=db,
                content=item['text'],
                platform=item.get('platform'),
                prediction=prediction,
                confidence=confidence,
                user_id=current_user.id if current_user else None
            )
        
        results.append({
            "text": item['text'],
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
            "prediction_text": prediction_text
        })
    
    return {
        "results": results,
        "count": len(results),
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

#### Bước 7: Apply Visual Indicators (content.js)

```javascript
function applyToxicityIndicator(commentElement, prediction) {
  const categoryNames = ["clean", "offensive", "hate", "spam"];
  const category = categoryNames[prediction.prediction];
  
  const style = CATEGORY_STYLES[category];
  
  // Create indicator
  const indicator = document.createElement('div');
  indicator.className = `toxic-indicator ${style.className}`;
  indicator.style.backgroundColor = style.color;
  indicator.textContent = style.label;
  indicator.title = `Phân loại: ${style.label} (${(prediction.confidence * 100).toFixed(1)}%)`;
  
  // Create report button
  const reportBtn = document.createElement('button');
  reportBtn.className = 'report-incorrect-btn';
  reportBtn.textContent = 'Báo cáo phân tích sai';
  reportBtn.addEventListener('click', (e) => {
    reportIncorrectAnalysis(commentElement, category);
  });
  
  // Add to DOM
  const indicatorContainer = document.createElement('div');
  indicatorContainer.className = 'toxic-indicator-container';
  indicatorContainer.appendChild(indicator);
  indicatorContainer.appendChild(reportBtn);
  
  commentElement.parentNode.insertBefore(
    indicatorContainer, 
    commentElement.nextSibling
  );
  
  // Add border
  commentElement.style.borderLeft = `3px solid ${style.color}`;
  commentElement.style.paddingLeft = '10px';
  
  // Blur hate speech
  if (category === 'hate') {
    commentElement.classList.add('toxic-blur');
    const revealBtn = document.createElement('button');
    revealBtn.textContent = 'Hiện nội dung';
    revealBtn.onclick = () => {
      commentElement.classList.remove('toxic-blur');
      revealBtn.remove();
    };
    indicatorContainer.appendChild(revealBtn);
  }
}
```

**Visual Indicators**:
- **Border color** matching category
- **Label badge** với tên category
- **Confidence** hiển thị trong tooltip
- **Report button** để feedback
- **Blur effect** cho hate speech với reveal button

---

### Timeline Example

```
T+0ms:    User navigates to facebook.com/post/123
T+100ms:  MutationObserver detects new comment nodes
T+150ms:  processComment() called for each comment
T+200ms:  10 comments added to buffer
T+2000ms: Timeout triggers → processCommentsBatch()
T+2050ms: API request sent với 10 comments
T+2500ms: Backend processes batch
          - Preprocess 10 texts
          - ML model prediction
          - Return results
T+2550ms: Results mapped và resolve promises
T+2600ms: Visual indicators applied to 10 comments
```

---

## 📦 2. LUỒNG BATCH PROCESSING

### Use Case
User muốn phân tích một lượng lớn text cùng lúc (từ file hoặc paste).

### Chi tiết Implementation

#### Frontend (popup.js)

```javascript
async function processBatchText() {
  const batchInputText = batchInput.value.trim();
  
  // Split by newlines
  const allComments = batchInputText.split('\n')
    .map(text => text.trim())
    .filter(text => text.length > 0);
  
  if (allComments.length === 0) {
    showNotification('Không tìm thấy bình luận hợp lệ', 'warning');
    return;
  }
  
  // Get auth data
  const authData = await getAuthData();
  const isLoggedIn = !!authData;
  
  // Prepare headers
  const headers = {
    'Content-Type': 'application/json',
  };
  if (isLoggedIn) {
    headers['Authorization'] = `Bearer ${authData.access_token}`;
  }
  
  // Process in chunks
  const CHUNK_SIZE = 100;
  const totalChunks = Math.ceil(allComments.length / CHUNK_SIZE);
  let allResults = [];
  
  for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
    // Update progress
    const progressPercent = Math.round((chunkIndex / totalChunks) * 100);
    updateProgress(progressPercent);
    
    // Get chunk
    const startIndex = chunkIndex * CHUNK_SIZE;
    const endIndex = Math.min(startIndex + CHUNK_SIZE, allComments.length);
    const currentChunk = allComments.slice(startIndex, endIndex);
    
    // Prepare items
    const items = currentChunk.map(text => ({
      text: text,
      platform: platform
    }));
    
    // API call
    const response = await fetch(`${API_ENDPOINT}/extension/batch-detect`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        items: items,
        save_to_db: isLoggedIn,
        store_clean: false,
        model_type: modelType
      })
    });
    
    const result = await response.json();
    allResults = allResults.concat(result.results);
    
    // Delay between chunks
    if (chunkIndex < totalChunks - 1) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }
  
  // Display results
  displayBatchResults({ results: allResults, count: allResults.length });
}
```

**Key Features**:
- **Chunking**: Process 100 items per API call
- **Progress tracking**: Real-time progress bar
- **Delay between chunks**: 300ms để tránh overwhelm server
- **Auto-save**: Chỉ save nếu logged in

---

#### Display Results

```javascript
function displayBatchResults(batchData) {
  batchResultList.innerHTML = '';
  
  const results = batchData.results || [];
  const counts = { clean: 0, offensive: 0, hate: 0, spam: 0 };
  
  results.forEach(result => {
    // Update counts
    counts[categoryNames[result.prediction]]++;
    
    // Create result item
    const resultItem = document.createElement('div');
    resultItem.className = 'batch-result-item';
    resultItem.innerHTML = `
      <div class="result-text">${result.text}</div>
      <div class="result-meta">
        <span class="label ${categoryNames[result.prediction]}">
          ${result.prediction_text}
        </span>
        <span class="confidence">${Math.round(result.confidence * 100)}%</span>
      </div>
    `;
    batchResultList.appendChild(resultItem);
  });
  
  // Update summary
  document.getElementById('batch-clean-count').textContent = counts.clean;
  document.getElementById('batch-offensive-count').textContent = counts.offensive;
  document.getElementById('batch-hate-count').textContent = counts.hate;
  document.getElementById('batch-spam-count').textContent = counts.spam;
}
```

---

## 🔐 3. LUỒNG AUTHENTICATION

### Register Flow

```
User Input (popup)
    │
    ▼
Validate Fields
    ├─ Username: required, unique
    ├─ Email: required, unique, valid format
    ├─ Password: required
    └─ Confirm Password: must match
    │
    ▼
POST /auth/register
    {
      "username": "string",
      "email": "string",
      "name": "string",
      "password": "string"
    }
    │
    ▼
Backend Processing
    ├─ Check username exists
    ├─ Check email exists
    ├─ Get default "user" role
    ├─ Hash password (bcrypt)
    ├─ Create User record
    └─ Create Log entry
    │
    ▼
Response: 201 Created
    {
      "id": 123,
      "username": "string",
      "email": "string",
      "role": "user",
      ...
    }
    │
    ▼
Frontend Actions
    ├─ Show success notification
    ├─ Switch to login form
    └─ Pre-fill username
```

---

### Login Flow

```
User Input (popup)
    │
    ▼
POST /auth/token (Form Data)
    username=...&password=...
    │
    ▼
Backend Processing
    ├─ Query User by username
    ├─ Verify password (bcrypt.verify)
    ├─ Check is_active
    ├─ Generate JWT token
    │   ├─ Payload: { sub: username, role: role_name }
    │   ├─ Secret: SECRET_KEY
    │   ├─ Algorithm: HS256
    │   └─ Expiry: ACCESS_TOKEN_EXPIRE_MINUTES
    ├─ Update last_login, last_login_ip
    └─ Create Log entry
    │
    ▼
Response: 200 OK
    {
      "access_token": "eyJ...",
      "token_type": "bearer",
      "user_id": 123,
      "username": "string",
      "role": "user",
      "expires_in": 86400
    }
    │
    ▼
Frontend Actions
    ├─ Save to chrome.storage.local
    │   {
    │     "toxicDetector_auth": {
    │       "access_token": "...",
    │       "user_id": 123,
    │       ...
    │     }
    │   }
    ├─ Fetch /auth/me to get full profile
    ├─ Update body class: add 'logged-in'
    ├─ Show profile section
    ├─ Update tab visibility
    │   ├─ Show: Stats tab
    │   ├─ Show: Batch mode
    │   └─ Enable: Save data checkbox
    └─ Show success notification
```

---

### Authenticated Request Flow

```
Every API Request (if logged in)
    │
    ▼
Get Token from Storage
    chrome.storage.local.get(['toxicDetector_auth'])
    │
    ▼
Add Authorization Header
    headers: {
      'Authorization': `Bearer ${authData.access_token}`
    }
    │
    ▼
Backend Middleware (dependencies.py)
    │
    ├─ Extract token from header
    ├─ Decode JWT token
    │   ├─ Verify signature with SECRET_KEY
    │   ├─ Check expiration
    │   └─ Extract username from 'sub'
    ├─ Query User by username
    ├─ Check is_active
    ├─ Update last_activity
    └─ Return User object
    │
    ▼
If Valid: Process Request
If Invalid: Return 401 Unauthorized
    │
    ▼
Frontend Error Handler (401)
    ├─ Clear auth data
    ├─ Update UI to logged-out state
    ├─ Show login form
    └─ Show notification: "Vui lòng đăng nhập lại"
```

---

## 🤖 4. LUỒNG ML PREDICTION

### Text Preprocessing Pipeline

```python
def preprocess_text(text: str) -> str:
    """
    Step-by-step preprocessing
    """
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 3. Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # 4. Remove/normalize punctuation
    text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
    
    # 5. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 6. Vietnamese tokenization
    try:
        from underthesea import word_tokenize
        text = word_tokenize(text, format="text")
    except ImportError:
        pass  # Skip if underthesea not available
    
    return text
```

---

### Model Prediction Flow

```python
def predict(self, text: str, model_type: str = None):
    """
    Full prediction pipeline
    """
    # 1. Load model nếu chưa load
    if not self.loaded:
        self.load_model()
    
    # 2. Handle empty text
    if not text or not text.strip():
        return 0, 1.0, {"clean": 1.0, "offensive": 0, "hate": 0, "spam": 0}
    
    # 3. Switch model nếu cần
    if model_type and model_type != self.model_type:
        model_files = {
            "lstm": "model/best_model_LSTM.h5",
            "cnn": "model/cnn/model.safetensors",
            "bert": "model/bert/model.safetensors",
            "phobert": "model/phobert/model.safetensors",
            ...
        }
        temp_model = ModelAdapter.load_model(model_files[model_type])
        # Use temp_model for this prediction
    
    # 4. Preprocess
    processed_input = self.preprocess(text)
    
    # 5. Model inference
    prediction = self.model.predict(processed_input)
    probs = prediction[0]
    
    # 6. Get class và confidence
    predicted_class = np.argmax(probs)
    confidence = float(probs[predicted_class])
    
    # 7. Apply spam heuristics
    _, spam_features = preprocess_for_spam_detection(text)
    
    spam_score = 0
    if spam_features.get('has_url'):
        spam_score += 0.2
    if spam_features.get('has_suspicious_url'):
        spam_score += 0.3
    if spam_features.get('url_count', 0) > 1:
        spam_score += 0.1 * spam_features['url_count']
    if spam_features.get('spam_keyword_count', 0) > 0:
        spam_score += 0.15 * spam_features['spam_keyword_count']
    if spam_features.get('has_excessive_punctuation'):
        spam_score += 0.1
    if spam_features.get('has_all_caps_words'):
        spam_score += 0.1
    
    # 8. Override nếu spam_score cao
    spam_class = 3
    if predicted_class != spam_class and confidence < 0.8 and spam_score > 0.5:
        predicted_class = spam_class
        confidence = max(confidence, spam_score)
        probabilities = {label: 0.1 for label in self.labels}
        probabilities[self.labels[spam_class]] = spam_score
    else:
        probabilities = {
            self.labels[i]: float(probs[i]) 
            for i in range(len(self.labels))
        }
    
    # 9. Return
    return int(predicted_class), confidence, probabilities
```

**Key Points**:
- **Model switching**: Có thể chọn model khác nhau cho mỗi prediction
- **Spam heuristics**: Rule-based system bổ sung cho ML
- **Confidence threshold**: 0.8 để apply spam rules
- **Probabilities**: Return đầy đủ xác suất cho tất cả classes

---

### Spam Detection Heuristics Details

```python
def preprocess_for_spam_detection(text: str):
    """
    Extract spam-related features
    """
    features = {}
    
    # URL detection
    url_pattern = r'https?://\S+|www\.\S+'
    urls = re.findall(url_pattern, text)
    features['has_url'] = len(urls) > 0
    features['url_count'] = len(urls)
    
    # Suspicious URL domains
    suspicious_domains = [
        'bit.ly', 'tinyurl.com', 'goo.gl',
        't.co', 'ow.ly', 'is.gd'
    ]
    features['has_suspicious_url'] = any(
        domain in url for url in urls for domain in suspicious_domains
    )
    
    # Spam keywords (Vietnamese)
    spam_keywords = [
        'giảm giá', 'khuyến mãi', 'mua ngay', 'click here',
        'inbox', 'zalo', 'liên hệ', 'tại đây', 'free'
    ]
    text_lower = text.lower()
    features['spam_keyword_count'] = sum(
        1 for keyword in spam_keywords if keyword in text_lower
    )
    
    # Excessive punctuation (>30% of text)
    punctuation_count = len([c for c in text if c in '!?.,;:'])
    features['has_excessive_punctuation'] = (
        punctuation_count / max(len(text), 1) > 0.3
    )
    
    # All caps words
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 3]
    features['has_all_caps_words'] = len(caps_words) > 2
    
    return text, features
```

---

## 📢 5. LUỒNG USER FEEDBACK

### Report Incorrect Analysis

```
User clicks "Báo cáo phân tích sai"
    │
    ▼
content.js: reportIncorrectAnalysis()
    ├─ Get comment text
    ├─ Get predicted category
    └─ Get comment ID
    │
    ▼
Send to background.js
    chrome.runtime.sendMessage({
      action: "reportIncorrectAnalysis",
      text: commentText,
      predictedCategory: category,
      commentId: commentId
    })
    │
    ▼
background.js: reportIncorrectAnalysis()
    │
    ▼
POST /extension/report
    {
      "text": "string",
      "predicted_category": "offensive",
      "comment_id": "string",
      "source_url": "string",
      "metadata": {
        "source": "extension",
        "browser": "user_agent",
        "timestamp": "ISO8601",
        "version": "1.0.0"
      }
    }
    │
    ▼
Backend: Store Report
    ├─ Create Log entry
    ├─ (Optional) Create Feedback entry
    └─ (Future) Add to retraining dataset
    │
    ▼
Response: 200 OK
    {"detail": "Báo cáo đã được ghi nhận"}
    │
    ▼
Frontend Actions
    ├─ Show success notification
    ├─ Update button state: "Đã báo cáo"
    └─ Disable button
```

---

## 📊 6. LUỒNG ADMIN DASHBOARD

### Dashboard Data Flow

```
Admin navigates to Dashboard
    │
    ▼
GET /admin/dashboard?period=month
    Headers: Authorization: Bearer <admin_token>
    │
    ▼
Backend: get_dashboard_data()
    │
    ├─ Verify admin role
    ├─ Calculate date range (day/week/month/year)
    ├─ Query statistics
    │   ├─ Total comments
    │   ├─ Comments by category (clean/offensive/hate/spam)
    │   ├─ Total users
    │   ├─ Active users in period
    │   └─ Comments by platform
    ├─ Get ML model stats
    └─ Return aggregated data
    │
    ▼
Response: 200 OK
    {
      "statistics": {
        "total_comments": 1234,
        "clean_comments": 800,
        "offensive_comments": 200,
        "hate_comments": 134,
        "spam_comments": 100,
        "total_users": 50,
        "active_users": 30
      },
      "platforms": {
        "facebook": 600,
        "youtube": 400,
        "twitter": 234
      },
      "model_stats": {
        "type": "lstm",
        "accuracy": 0.92,
        ...
      },
      "period": "month"
    }
    │
    ▼
Dashboard Rendering
    ├─ Update statistics cards
    ├─ Render pie chart (by category)
    ├─ Render bar chart (by platform)
    └─ Display recent comments table
```

---

### Comment Management Flow

```
Admin searches comments
    │
    ▼
GET /admin/comments?
    platform=facebook&
    prediction=2&
    start_date=2024-01-01&
    end_date=2024-12-31&
    search=keyword&
    skip=0&
    limit=100
    │
    ▼
Backend: get_comments()
    │
    ├─ Verify admin role
    ├─ Build query với filters
    │   ├─ Platform filter
    │   ├─ Prediction filter
    │   ├─ Date range filter
    │   ├─ Search in content
    │   ├─ Confidence range
    │   └─ User filter
    ├─ Execute query với pagination
    └─ Return comments list
    │
    ▼
Response: 200 OK
    [
      {
        "id": 123,
        "content": "...",
        "prediction": 2,
        "prediction_text": "hate",
        "confidence": 0.85,
        "platform": "facebook",
        "source_user_name": "user123",
        "created_at": "2024-10-19T..."
      },
      ...
    ]
    │
    ▼
Dashboard Actions
    ├─ Display in table
    ├─ Enable actions:
    │   ├─ View details
    │   ├─ Edit/Review
    │   ├─ Delete
    │   └─ Export
    └─ Show pagination controls
```

---

### Export Comments Flow

```
Admin clicks "Export"
    │
    ▼
Select format: CSV | Excel | PDF
    │
    ▼
GET /admin/export/comments?
    format=csv&
    (same filters as search)
    │
    ▼
Backend: export_comments()
    │
    ├─ Verify admin role
    ├─ Query comments với filters (no limit)
    ├─ Convert to DataFrame
    ├─ Generate file theo format
    │   ├─ CSV: df.to_csv()
    │   ├─ Excel: df.to_excel()
    │   └─ PDF: ReportLab + Table
    └─ Create Log entry
    │
    ▼
Response: File Download
    Content-Type: text/csv | application/vnd.ms-excel | application/pdf
    Content-Disposition: attachment; filename=comments_export.xxx
    │
    ▼
Browser downloads file
```

---

## 🔄 TỔNG KẾT INTERACTION PATTERNS

### 1. Extension ↔ Backend
- **Protocol**: HTTP REST API
- **Auth**: Basic Auth hoặc JWT Bearer token
- **Data Format**: JSON
- **Batch Size**: 100 items max per request
- **Retry Logic**: Fallback to individual analysis on batch failure

### 2. Popup ↔ Background
- **Protocol**: Chrome Runtime Messaging
- **Method**: `chrome.runtime.sendMessage()`
- **Pattern**: Request-Response với callback
- **Error Handling**: Error object trong response

### 3. Content ↔ Background
- **Protocol**: Chrome Runtime Messaging
- **Pattern**: 
  - Content → Background: Request analysis
  - Background → Content: Return result
- **Async**: Promise-based communication

### 4. Frontend ↔ Backend (Dashboard)
- **Protocol**: HTTP REST API
- **Auth**: JWT Bearer token
- **CORS**: Enabled với specific origins
- **Rate Limiting**: 100 requests / 60 seconds

---

## 📈 PERFORMANCE CONSIDERATIONS

### Extension
- **Debouncing**: MutationObserver events
- **Batching**: 100 comments per API call
- **Timeout**: 2s before processing incomplete batch
- **Caching**: Processed comments in Set
- **Lazy Loading**: Only analyze visible comments

### Backend
- **Connection Pooling**: SQLAlchemy pool_size=5
- **Model Caching**: Singleton pattern cho MLModel
- **Background Tasks**: Database writes
- **Rate Limiting**: IP-based with Redis (future)
- **Vector Indexing**: For similarity search

### Database
- **Indexes**: 
  - users(username, email)
  - comments(platform, prediction, created_at)
  - logs(timestamp, user_id)
- **Partitioning**: By created_at (future)
- **Archiving**: Old comments (future)

---

*Tài liệu được tạo tự động bởi AI Assistant*
*Ngày tạo: 2025-10-19*

