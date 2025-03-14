---
<<<<<<< HEAD
title: My Hugging Face Space
emoji: 🚀

colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.25.0"
app_file: app.py
pinned: false
---

Check out the configuration reference at [Hugging Face Spaces Config](https://huggingface.co/docs/hub/spaces-config-reference).

# Social Media Toxicity Detector

A browser extension that detects toxic, offensive, hate speech, and spam content on social media platforms using a machine learning model.

## Features

- Detection of toxic content on Facebook, Twitter, and YouTube
- Classification into 4 categories: Clean (0), Offensive (1), Hate Speech (2), and Spam (3)
- Real-time content scanning on social media platforms
- Manual text analysis
- Admin dashboard for content monitoring and analytics
- User role-based access control
- Comment log and history tracking

## Project Structure

The project is organized into two main components:

1. **Backend API**: FastAPI-based REST API for model inference, user management, and data storage
2. **Browser Extension**: Chrome extension for content detection and user interface

## Backend Setup

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-media-toxicity-detector.git
cd social-media-toxicity-detector
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables by creating a `.env` file:
```
# API Configuration
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=toxicity_detector
POSTGRES_PORT=5432

# ML Model Configuration
MODEL_PATH=model/toxicity_detector.h5
HUGGINGFACE_API_URL=https://api-inference.huggingface.co/models/your-model-endpoint
HUGGINGFACE_API_TOKEN=your-huggingface-token

# Social Media APIs
FACEBOOK_API_KEY=your-facebook-api-key
TWITTER_API_KEY=your-twitter-api-key
YOUTUBE_API_KEY=your-youtube-api-key
```

5. Initialize the database:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. Start the API server:
```bash
uvicorn backend.main:app --reload
```

### API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Extension Setup

1. Navigate to the extension directory:
```bash
cd extension
```

2. Configure the API endpoint in `background.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api'; // Change to your actual API endpoint
```

3. Install the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension` directory

## Usage

1. After installing the extension, click on the extension icon in the toolbar
2. Log in with your credentials
3. Visit Facebook, Twitter, or YouTube to activate content scanning
4. Use the extension popup to scan pages manually or analyze specific text
5. Access the admin dashboard at `http://localhost:8000/admin` (requires admin login)

## Model Training

The toxicity detection model was trained using a dataset with 4 labels:
- 0: Clean content
- 1: Offensive content
- 2: Hate speech
- 3: Spam

The model file (.h5) should be placed in the `model` directory or served via Hugging Face API.

## Database Schema

The system uses PostgreSQL with pgvector extension for vector similarity search:

- **Users**: User accounts with role-based permissions
- **Roles**: User roles (admin, moderator, user)
- **Comments**: Detected comments with classification results and vector embeddings
- **Logs**: System activity logs

## Security Features

- JWT authentication
- Role-based access control
- Password hashing with bcrypt
- Request logging
- Input validation and sanitization

## License

[MIT License](LICENSE)
=======
title: Toxic Language Detectorv1
emoji: 📉
colorFrom: green
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: Phát hiện ngôn từ mang tính tiêu cực trên nền tảng mạng xhội
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
>>>>>>> 63f018187613dc0194465eb9793c738c52e78f2c
