# app.py - Hugging Face Space Entry Point
import os
import sys
import gradio as gr
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from api.routes import admin, auth, extension, prediction, toxic_detection
from core.middleware import LogMiddleware
from db.models.base import Base
from db.models.user import engine
from typing import List, Dict, Any, Optional
import tensorflow as tf
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re

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

class PredictionResponse(BaseModel):
    text: str
    prediction: int
    confidence: float
    prediction_text: str

# Load ML model
class ToxicDetectionModel:
    def __init__(self):
        # Load or create model trained on Vietnamese social media data
        try:
            self.model = tf.keras.models.load_model("model/best_model_LSTM.h5")
            print("Vietnamese toxicity model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Creating a dummy model for demonstration")
            self.model = self._create_dummy_model()
        
        # Initialize vectorizer for Vietnamese text
        # Vietnamese doesn't use the same stop words as English
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words=None,  # Don't use English stop words
            ngram_range=(1, 3)  # Use 1-3 grams for better Vietnamese phrase capture
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
                print("Vietnamese NLP library loaded successfully")
            else:
                self.has_vietnamese_nlp = False
                print("Vietnamese NLP library not found, using basic tokenization")
        except Exception:
            self.has_vietnamese_nlp = False
    
    def _create_dummy_model(self):
        # Create a simple model for demonstration
        inputs = tf.keras.Input(shape=(10000,))
        x = tf.keras.layers.Dense(128, activation='relu')(inputs)
        x = tf.keras.layers.Dropout(0.3)(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_text(self, text):
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
                print(f"Error in Vietnamese tokenization: {e}")
        
        # Vectorize
        if not hasattr(self.vectorizer, 'vocabulary_'):
            self.vectorizer.fit([text])
        
        features = self.vectorizer.transform([text]).toarray()
        return features
    
    def predict(self, text):
        # Preprocess text
        features = self.preprocess_text(text)
        
        # Make prediction
        predictions = self.model.predict(features)[0]
        
        # Get most likely class and confidence
        predicted_class = np.argmax(predictions)
        confidence = float(predictions[predicted_class])
        
        return int(predicted_class), confidence, self.label_mapping[int(predicted_class)]

# Initialize model
model = ToxicDetectionModel()

# API Key validation
API_KEY = os.environ.get("API_KEY", "test-api-key")

def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# API routes
@app.post("/extension/detect", response_model=PredictionResponse)
async def detect_toxic_language(
    request: PredictionRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

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
        </body>
    </html>
    """

# Gradio interface
def predict_toxic(text):
    prediction_class, confidence, prediction_text = model.predict(text)
    
    # Format response
    result = f"Prediction: {prediction_text.capitalize()} (Class {prediction_class})\n"
    result += f"Confidence: {confidence:.2f}"
    
    return result

# Create Gradio interface
interface = gr.Interface(
    fn=predict_toxic,
    inputs=gr.Textbox(lines=5, placeholder="Enter text to analyze for toxic language..."),
    outputs="text",
    title="Toxic Language Detector",
    description="Detects whether text contains toxic language. Classes: 0 (clean), 1 (offensive), 2 (hate), 3 (spam)."
)

# Mount Gradio app
app = gr.mount_gradio_app(app, interface, path="/gradio")

# For direct Hugging Face Space usage
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)