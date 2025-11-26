# DATABASE SCHEMA & API DOCUMENTATION

## 📋 MỤC LỤC
1. [Database Schema](#database-schema)
2. [API Endpoints](#api-endpoints)
3. [Request/Response Models](#requestresponse-models)
4. [Authentication](#authentication)
5. [Rate Limiting](#rate-limiting)

---

## 💾 1. DATABASE SCHEMA

### Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    Role     │◄──────│     User     │──────►│  UserSettings│
│             │ 1    *│              │1     1│             │
│ - id        │       │ - id         │       │ - id        │
│ - name      │       │ - username   │       │ - user_id   │
│ - permissions│      │ - email      │       │ - settings  │
└─────────────┘       │ - password   │       └─────────────┘
                      │ - role_id    │
                      │ - is_active  │
                      └──────┬───────┘
                             │
                             │ 1
                             │
                             │ *
              ┌──────────────┼──────────────┐
              │              │              │
              │              │              │
              ▼              ▼              ▼
      ┌──────────┐   ┌──────────┐   ┌──────────┐
      │ Comment  │   │   Log    │   │  Report  │
      │          │   │          │   │          │
      │ - id     │   │ - id     │   │ - id     │
      │ - content│   │ - action │   │ - type   │
      │ - user_id│   │ - user_id│   │ - user_id│
      └──────────┘   └──────────┘   └──────────┘

┌──────────────┐
│ Permission   │
│              │
│ - id         │
│ - name       │
│ - description│
└──────────────┘
       ▲
       │ *
       │
       │ *
┌──────────────┐
│ RolePermission│
│              │
│ - role_id    │
│ - permission_id│
└──────────────┘

┌──────────────┐
│ RefreshToken │
│              │
│ - id         │
│ - user_id    │
│ - token      │
│ - expires_at │
└──────────────┘
```

---

### Table: users

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    role_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    last_login_ip VARCHAR(45),
    last_activity TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expiry TIMESTAMP,
    verification_token VARCHAR(255),
    verification_expiry TIMESTAMP,
    extension_settings JSON,
    
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_active ON users(is_active);
```

**Fields**:
- **id**: Primary key, auto-increment
- **username**: Unique identifier for login, max 50 chars
- **email**: Unique email address, max 100 chars
- **name**: Full name, optional
- **hashed_password**: Bcrypt hashed password
- **role_id**: Foreign key to `roles` table
- **is_active**: Account active status
- **is_verified**: Email verification status
- **created_at**: Account creation timestamp
- **updated_at**: Last profile update
- **last_login**: Last successful login
- **last_login_ip**: IP address of last login
- **last_activity**: Last API activity
- **failed_login_attempts**: Counter for security
- **locked_until**: Account lock expiry
- **reset_token**: Password reset token
- **reset_token_expiry**: Reset token expiration
- **verification_token**: Email verification token
- **verification_expiry**: Verification token expiration
- **extension_settings**: JSON blob for extension preferences

---

### Table: roles

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default roles
INSERT INTO roles (name, display_name, description, permissions) VALUES
('admin', 'Administrator', 'Full system access', '["*"]'),
('user', 'User', 'Standard user access', '["read:own", "write:own"]'),
('service', 'Service Account', 'For browser extension', '["extension:detect", "extension:report"]');
```

**Default Roles**:
1. **admin**: Full access, all permissions
2. **user**: Normal user, can read/write own data
3. **service**: For extension, limited to detect and report

---

### Table: permissions

```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50),
    action VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample permissions
INSERT INTO permissions (name, description, resource, action) VALUES
('read:comments', 'Read comments', 'comments', 'read'),
('write:comments', 'Write comments', 'comments', 'write'),
('delete:comments', 'Delete comments', 'comments', 'delete'),
('read:users', 'Read users', 'users', 'read'),
('write:users', 'Manage users', 'users', 'write'),
('read:stats', 'Read statistics', 'stats', 'read'),
('admin:*', 'All admin actions', '*', '*');
```

---

### Table: comments

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    processed_content TEXT,
    platform VARCHAR(50),
    source_user_name VARCHAR(100),
    source_url TEXT,
    prediction INTEGER,
    prediction_text VARCHAR(20),
    confidence FLOAT,
    probabilities JSON,
    vector_representation BLOB,
    user_id INTEGER,
    meta_data JSON,
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    correct_label INTEGER,
    report_ids JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_comments_platform ON comments(platform);
CREATE INDEX idx_comments_prediction ON comments(prediction);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_created ON comments(created_at);
CREATE INDEX idx_comments_platform_pred ON comments(platform, prediction);
```

**Fields**:
- **id**: Primary key
- **content**: Original comment text
- **processed_content**: Preprocessed text for ML
- **platform**: Source platform (facebook, youtube, twitter)
- **source_user_name**: Username who posted comment
- **source_url**: URL of the comment
- **prediction**: Model prediction (0=clean, 1=offensive, 2=hate, 3=spam)
- **prediction_text**: Human-readable label
- **confidence**: Model confidence score (0-1)
- **probabilities**: JSON object with all class probabilities
- **vector_representation**: BLOB of TF-IDF vector (for similarity search)
- **user_id**: ID of extension user who submitted
- **meta_data**: Additional context (browser, version, etc.)
- **is_reviewed**: Manual review status
- **reviewed_by**: Admin who reviewed
- **reviewed_at**: Review timestamp
- **correct_label**: Corrected label if misclassified
- **report_ids**: Array of related report IDs
- **created_at**: First saved
- **updated_at**: Last modified

---

### Table: logs

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    username VARCHAR(50),
    action VARCHAR(100),
    resource VARCHAR(50),
    resource_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,
    status VARCHAR(20),
    error_message TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_user ON logs(user_id);
CREATE INDEX idx_logs_action ON logs(action);
CREATE INDEX idx_logs_resource ON logs(resource);
```

**Actions Logged**:
- `user:register`
- `user:login`
- `user:logout`
- `user:password_reset_request`
- `user:password_reset`
- `user:password_change`
- `comment:create`
- `comment:update`
- `comment:delete`
- `prediction:single`
- `prediction:batch`
- `extension:detect`
- `extension:report`
- `admin:dashboard_access`
- `admin:user_update`
- `export:comments`

---

### Table: reports

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type VARCHAR(50),
    content TEXT,
    predicted_category VARCHAR(20),
    suggested_category VARCHAR(20),
    comment_id INTEGER,
    source_url TEXT,
    metadata JSON,
    user_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_user ON reports(user_id);
CREATE INDEX idx_reports_created ON reports(created_at);
```

**Report Types**:
- `incorrect_prediction`: User reports wrong classification
- `false_positive`: Model flagged clean content as toxic
- `false_negative`: Model missed toxic content
- `wrong_category`: Category is incorrect (e.g., spam vs offensive)

**Status Values**:
- `pending`: Not yet reviewed
- `confirmed`: Admin confirmed the report
- `rejected`: Admin rejected the report
- `resolved`: Issue has been resolved

---

### Table: user_settings

```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Settings Structure (JSON)**:
```json
{
  "extension": {
    "enabled": true,
    "threshold": 0.5,
    "enabledPlatforms": ["facebook", "youtube", "twitter"],
    "displayStyle": "inline",
    "autoBlurHate": true,
    "soundEnabled": false,
    "modelType": "lstm"
  },
  "notifications": {
    "email": true,
    "browser": false
  },
  "privacy": {
    "shareStats": false,
    "saveHistory": true
  }
}
```

---

### Table: refresh_tokens

```sql
CREATE TABLE refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

---

## 🔌 2. API ENDPOINTS

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints

#### POST /auth/register
**Description**: Register a new user account

**Request Body**:
```json
{
  "username": "string (required, 3-50 chars)",
  "email": "string (required, valid email)",
  "name": "string (optional)",
  "password": "string (required, min 8 chars)"
}
```

**Response**: 201 Created
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-10-19T10:00:00Z"
}
```

**Errors**:
- 400: Username/email already exists
- 422: Validation error

---

#### POST /auth/token
**Description**: Login and get access token

**Request Body** (Form Data):
```
username: string
password: string
```

**Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": 1,
  "username": "newuser",
  "role": "user"
}
```

**Errors**:
- 401: Invalid credentials
- 403: Account locked/inactive

---

#### GET /auth/me
**Description**: Get current user info

**Headers**:
```
Authorization: Bearer {token}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "name": "John Doe",
  "role": {
    "id": 2,
    "name": "user",
    "display_name": "User"
  },
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-10-19T10:00:00Z",
  "last_login": "2024-10-19T11:00:00Z"
}
```

---

#### POST /auth/reset-password-request
**Description**: Request password reset email

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**: 200 OK
```json
{
  "detail": "Password reset email sent"
}
```

---

#### POST /auth/reset-password
**Description**: Reset password with token

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

**Response**: 200 OK
```json
{
  "detail": "Password reset successful"
}
```

---

#### POST /auth/change-password
**Description**: Change password (authenticated)

**Headers**:
```
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response**: 200 OK
```json
{
  "detail": "Password changed successfully"
}
```

---

### Extension Endpoints

#### POST /extension/detect
**Description**: Analyze single comment (for extension)

**Headers**:
```
Authorization: Basic {base64(extension_key)}
OR
Authorization: Bearer {user_token}
```

**Request Body**:
```json
{
  "text": "Comment content to analyze",
  "platform": "facebook",
  "platform_id": "comment_id_123",
  "source_user_name": "username",
  "source_url": "https://facebook.com/...",
  "save_to_db": true,
  "metadata": {
    "browser": "Chrome",
    "version": "1.0.0"
  }
}
```

**Response**: 200 OK
```json
{
  "text": "Comment content to analyze",
  "prediction": 1,
  "prediction_text": "xúc phạm",
  "confidence": 0.85,
  "probabilities": {
    "clean": 0.10,
    "offensive": 0.85,
    "hate": 0.03,
    "spam": 0.02
  },
  "timestamp": "2024-10-19T10:00:00Z",
  "model_type": "lstm",
  "comment_id": 123
}
```

**Errors**:
- 401: Invalid API key/token
- 422: Invalid request format
- 429: Rate limit exceeded

---

#### POST /extension/batch-detect
**Description**: Analyze multiple comments in batch

**Headers**:
```
Authorization: Basic {base64(extension_key)}
```

**Request Body**:
```json
{
  "items": [
    {
      "text": "Comment 1",
      "platform": "facebook",
      "platform_id": "id1"
    },
    {
      "text": "Comment 2",
      "platform": "youtube",
      "platform_id": "id2"
    }
  ],
  "save_to_db": true,
  "store_clean": false,
  "model_type": "lstm"
}
```

**Response**: 200 OK
```json
{
  "results": [
    {
      "text": "Comment 1",
      "prediction": 0,
      "prediction_text": "bình thường",
      "confidence": 0.95,
      "probabilities": {...}
    },
    {
      "text": "Comment 2",
      "prediction": 2,
      "prediction_text": "thù ghét",
      "confidence": 0.88,
      "probabilities": {...}
    }
  ],
  "count": 2,
  "timestamp": "2024-10-19T10:00:00Z",
  "processing_time": 0.15
}
```

---

#### GET /extension/stats
**Description**: Get extension usage statistics

**Headers**:
```
Authorization: Bearer {user_token}
```

**Query Parameters**:
```
period: "day" | "week" | "month" | "year" | "all" (default: "all")
platform: "facebook" | "youtube" | "twitter" (optional)
```

**Response**: 200 OK
```json
{
  "total_comments": 1234,
  "by_category": {
    "clean": 800,
    "offensive": 234,
    "hate": 100,
    "spam": 100
  },
  "by_platform": {
    "facebook": 600,
    "youtube": 400,
    "twitter": 234
  },
  "average_confidence": 0.82,
  "period": "all",
  "user_id": 1
}
```

---

#### GET /extension/settings
**Description**: Get extension settings

**Headers**:
```
Authorization: Bearer {user_token}
```

**Response**: 200 OK
```json
{
  "enabled": true,
  "threshold": 0.5,
  "enabledPlatforms": ["facebook", "youtube", "twitter"],
  "displayStyle": "inline",
  "autoBlurHate": true,
  "soundEnabled": false,
  "modelType": "lstm"
}
```

---

#### PUT /extension/settings
**Description**: Update extension settings

**Headers**:
```
Authorization: Bearer {user_token}
```

**Request Body**:
```json
{
  "enabled": true,
  "threshold": 0.7,
  "enabledPlatforms": ["facebook"],
  "autoBlurHate": false
}
```

**Response**: 200 OK
```json
{
  "detail": "Settings updated successfully",
  "settings": {...}
}
```

---

#### POST /extension/report
**Description**: Report incorrect analysis

**Headers**:
```
Authorization: Bearer {user_token}
OR
Authorization: Basic {base64(extension_key)}
```

**Request Body**:
```json
{
  "text": "Comment content",
  "predicted_category": "offensive",
  "suggested_category": "clean",
  "comment_id": "id123",
  "source_url": "https://...",
  "metadata": {
    "source": "extension"
  }
}
```

**Response**: 200 OK
```json
{
  "detail": "Report submitted successfully",
  "report_id": 456
}
```

---

### Prediction Endpoints

#### POST /prediction/single
**Description**: Analyze single text

**Headers**:
```
Authorization: Bearer {user_token}
```

**Request Body**:
```json
{
  "text": "Text to analyze",
  "save_to_db": true,
  "model_type": "lstm"
}
```

**Response**: 200 OK
```json
{
  "text": "Text to analyze",
  "prediction": 1,
  "prediction_text": "xúc phạm",
  "confidence": 0.85,
  "probabilities": {...},
  "timestamp": "2024-10-19T10:00:00Z"
}
```

---

#### POST /prediction/batch
**Description**: Analyze multiple texts

**Headers**:
```
Authorization: Bearer {user_token}
```

**Request Body**:
```json
{
  "texts": ["Text 1", "Text 2", "Text 3"],
  "save_to_db": false,
  "model_type": "bert"
}
```

**Response**: 200 OK
```json
{
  "results": [
    {"text": "Text 1", "prediction": 0, ...},
    {"text": "Text 2", "prediction": 1, ...},
    {"text": "Text 3", "prediction": 2, ...}
  ],
  "count": 3,
  "timestamp": "2024-10-19T10:00:00Z"
}
```

---

#### POST /prediction/upload-csv
**Description**: Upload CSV file for batch analysis

**Headers**:
```
Authorization: Bearer {user_token}
```

**Request Body** (Form Data):
```
file: CSV file (max 10MB)
text_column: "comment" (column name with text)
save_to_db: true
```

**Response**: 200 OK
```json
{
  "filename": "comments.csv",
  "total_rows": 500,
  "results": [...],
  "timestamp": "2024-10-19T10:00:00Z"
}
```

---

#### GET /prediction/similar/{comment_id}
**Description**: Find similar comments

**Headers**:
```
Authorization: Bearer {user_token}
```

**Query Parameters**:
```
limit: 10 (default)
threshold: 0.7 (similarity threshold, 0-1)
```

**Response**: 200 OK
```json
{
  "original_comment": {
    "id": 123,
    "content": "...",
    "prediction": 1
  },
  "similar_comments": [
    {
      "id": 456,
      "content": "...",
      "prediction": 1,
      "similarity": 0.92
    },
    ...
  ],
  "count": 5
}
```

---

### Admin Endpoints

#### GET /admin/dashboard
**Description**: Get dashboard statistics

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Query Parameters**:
```
period: "day" | "week" | "month" | "year" (default: "month")
```

**Response**: 200 OK
```json
{
  "statistics": {
    "total_comments": 5000,
    "clean_comments": 3000,
    "offensive_comments": 1000,
    "hate_comments": 500,
    "spam_comments": 500,
    "total_users": 100,
    "active_users": 50
  },
  "platforms": {
    "facebook": 2500,
    "youtube": 1500,
    "twitter": 1000
  },
  "recent_comments": [...],
  "model_stats": {
    "type": "lstm",
    "accuracy": 0.92,
    "precision": 0.88,
    "recall": 0.85
  },
  "period": "month"
}
```

---

#### GET /admin/users
**Description**: List all users

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Query Parameters**:
```
skip: 0 (pagination offset)
limit: 100 (max results)
role: "admin" | "user" | "service" (filter by role)
active: true | false (filter by active status)
search: "username or email" (search query)
```

**Response**: 200 OK
```json
{
  "users": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "role": "user",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-10-19T10:00:00Z"
    },
    ...
  ],
  "total": 100,
  "skip": 0,
  "limit": 100
}
```

---

#### POST /admin/users
**Description**: Create new user (admin)

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Request Body**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "name": "New User",
  "password": "password123",
  "role_name": "user",
  "is_active": true
}
```

**Response**: 201 Created
```json
{
  "id": 101,
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "is_active": true
}
```

---

#### PUT /admin/users/{user_id}
**Description**: Update user

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Request Body**:
```json
{
  "email": "newemail@example.com",
  "name": "Updated Name",
  "role_name": "admin",
  "is_active": false
}
```

**Response**: 200 OK
```json
{
  "detail": "User updated successfully",
  "user": {...}
}
```

---

#### DELETE /admin/users/{user_id}
**Description**: Delete user

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Response**: 200 OK
```json
{
  "detail": "User deleted successfully"
}
```

---

#### GET /admin/logs
**Description**: View system logs

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Query Parameters**:
```
skip: 0
limit: 100
action: "user:login" (filter by action)
user_id: 1 (filter by user)
start_date: "2024-01-01"
end_date: "2024-12-31"
```

**Response**: 200 OK
```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-10-19T10:00:00Z",
      "user_id": 1,
      "username": "user1",
      "action": "user:login",
      "ip_address": "192.168.1.1",
      "status": "success"
    },
    ...
  ],
  "total": 1000,
  "skip": 0,
  "limit": 100
}
```

---

#### GET /admin/comments
**Description**: View all comments

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Query Parameters**:
```
skip: 0
limit: 100
platform: "facebook"
prediction: 1 (filter by category)
start_date: "2024-01-01"
end_date: "2024-12-31"
search: "keyword"
user_id: 1
min_confidence: 0.5
max_confidence: 1.0
```

**Response**: 200 OK
```json
{
  "comments": [
    {
      "id": 1,
      "content": "...",
      "prediction": 1,
      "prediction_text": "xúc phạm",
      "confidence": 0.85,
      "platform": "facebook",
      "created_at": "2024-10-19T10:00:00Z"
    },
    ...
  ],
  "total": 5000,
  "skip": 0,
  "limit": 100
}
```

---

#### DELETE /admin/comments/{comment_id}
**Description**: Delete comment

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Response**: 200 OK
```json
{
  "detail": "Comment deleted successfully"
}
```

---

#### GET /admin/export/comments
**Description**: Export comments

**Headers**:
```
Authorization: Bearer {admin_token}
```

**Query Parameters**:
```
format: "csv" | "excel" | "pdf" (default: "csv")
platform: "facebook" (optional filter)
prediction: 1 (optional filter)
start_date: "2024-01-01"
end_date: "2024-12-31"
```

**Response**: File Download
```
Content-Type: text/csv | application/vnd.ms-excel | application/pdf
Content-Disposition: attachment; filename=comments_export.{format}
```

---

## 📝 3. REQUEST/RESPONSE MODELS

### Pydantic Models

#### User Models

```python
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        orm_mode = True
```

---

#### Prediction Models

```python
class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    platform: Optional[str] = None
    platform_id: Optional[str] = None
    source_user_name: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    save_to_db: bool = False
    metadata: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    text: str
    prediction: int = Field(..., ge=0, le=3)
    prediction_text: str
    confidence: float = Field(..., ge=0, le=1)
    probabilities: Dict[str, float]
    timestamp: datetime
    model_type: Optional[str] = None
    comment_id: Optional[int] = None

class BatchPredictionRequest(BaseModel):
    items: List[Dict[str, Any]]
    save_to_db: bool = False
    store_clean: bool = False
    model_type: Optional[str] = "lstm"

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    count: int
    timestamp: datetime
    processing_time: Optional[float] = None
```

---

#### Extension Models

```python
class ExtensionSettings(BaseModel):
    enabled: bool = True
    threshold: float = Field(0.5, ge=0, le=1)
    enabledPlatforms: List[str] = ["facebook", "youtube", "twitter"]
    displayStyle: str = "inline"
    autoBlurHate: bool = True
    soundEnabled: bool = False
    modelType: str = "lstm"

class ExtensionStatsResponse(BaseModel):
    total_comments: int
    by_category: Dict[str, int]
    by_platform: Dict[str, int]
    average_confidence: float
    period: str
    user_id: Optional[int]

class ReportRequest(BaseModel):
    text: str
    predicted_category: str
    suggested_category: Optional[str] = None
    comment_id: Optional[str] = None
    source_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

---

## 🔐 4. AUTHENTICATION

### JWT Token Structure

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "username",
  "role": "user",
  "exp": 1697788800,
  "iat": 1697702400
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret_key
)
```

---

### API Key Authentication

**Extension API Key**:
- Stored in `EXTENSION_API_KEY` environment variable
- Used with Basic Auth: `Authorization: Basic {base64(api_key)}`
- Limited to extension-specific endpoints

---

## ⏱️ 5. RATE LIMITING

### Configuration

```python
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_PERIOD = 60     # seconds
```

### Implementation

- **Algorithm**: Sliding window
- **Storage**: In-memory dict (production: Redis)
- **Key**: Client IP address
- **Endpoints**: All API endpoints
- **Response**: 429 Too Many Requests

**Response Example**:
```json
{
  "detail": "Too many requests. Please try again later.",
  "retry_after": 30
}
```

---

## 📊 ERROR RESPONSES

### Standard Error Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-10-19T10:00:00Z"
}
```

### HTTP Status Codes

- **200 OK**: Success
- **201 Created**: Resource created
- **400 Bad Request**: Invalid request
- **401 Unauthorized**: Missing/invalid auth
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

---

*Tài liệu được tạo tự động bởi AI Assistant*
*Ngày tạo: 2025-10-19*

