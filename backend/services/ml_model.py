import os
import numpy as np
import tensorflow as tf
import json
from typing import Dict, Any, List, Tuple, Optional
import httpx
from sentence_transformers import SentenceTransformer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from backend.config.settings import settings

class ToxicityDetector:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.embedding_model = None
        self.max_sequence_length = 100
        self.labels = ["clean", "offensive", "hate", "spam"]
        self.is_huggingface_api = True  # Set to False to use local model
        self.initialize()

    def initialize(self):
        """Initialize the model and tokenizer"""
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading embedding model: {e}")

        # If using HuggingFace API, we don't need to load the local model
        if self.is_huggingface_api:
            print("Using HuggingFace API for toxicity detection")
            return

        # Load local model
        try:
            model_path = settings.MODEL_PATH
            if os.path.exists(model_path):
                self.model = load_model(model_path)
                print(f"Model loaded from {model_path}")
            else:
                print(f"Model file {model_path} not found")

            # Initialize tokenizer - this would normally be loaded from a saved tokenizer
            # For this example, we'll create a simple one
            self.tokenizer = Tokenizer(num_words=10000)
            
        except Exception as e:
            print(f"Error loading model: {e}")

    async def get_embeddings(self, text: str) -> np.ndarray:
        """Get text embeddings using sentence transformer"""
        if self.embedding_model is None:
            return np.zeros(768)  # Return zero vector if model not loaded
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return np.zeros(768)

    async def predict_local(self, text: str) -> Dict[str, Any]:
        """Predict toxicity using local model"""
        if self.model is None or self.tokenizer is None:
            return {
                "error": "Model not initialized",
                "classification": 0,  # Default to clean
                "probabilities": {
                    "clean": 1.0,
                    "offensive": 0.0,
                    "hate": 0.0,
                    "spam": 0.0
                }
            }
            
        # Tokenize and pad text
        sequences = self.tokenizer.texts_to_sequences([text])
        padded_sequences = pad_sequences(sequences, maxlen=self.max_sequence_length)
        
        # Predict
        predictions = self.model.predict(padded_sequences)[0]
        
        # Get class with highest probability
        class_idx = np.argmax(predictions)
        
        # Map predictions to labels
        result = {
            "classification": int(class_idx),
            "probabilities": {
                self.labels[i]: float(predictions[i])
                for i in range(len(self.labels))
            }
        }
        
        return result

    async def predict_huggingface(self, text: str) -> Dict[str, Any]:
        """Predict toxicity using HuggingFace API"""
        api_url = settings.HUGGINGFACE_API_URL
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={"inputs": text}
                )
                
                if response.status_code != 200:
                    return {
                        "error": f"API Error: {response.text}",
                        "classification": 0,  # Default to clean
                        "probabilities": {
                            "clean": 1.0,
                            "offensive": 0.0,
                            "hate": 0.0,
                            "spam": 0.0
                        }
                    }
                
                # Parse response
                api_result = response.json()
                
                # Expected format: [{"label": "LABEL_0", "score": 0.9}]
                # Adapt this to match your actual API response format
                if isinstance(api_result, list) and len(api_result) > 0:
                    # Get the prediction with highest confidence
                    sorted_results = sorted(api_result, key=lambda x: x.get("score", 0), reverse=True)
                    top_result = sorted_results[0]
                    
                    # Parse label to get class index (assuming format like "LABEL_0")
                    label = top_result.get("label", "LABEL_0")
                    try:
                        class_idx = int(label.split("_")[1])
                    except:
                        class_idx = 0  # Default to clean
                    
                    # Create probability dict with available scores
                    probabilities = {
                        self.labels[i]: 0.0 for i in range(len(self.labels))
                    }
                    
                    for result in api_result:
                        label = result.get("label", "")
                        try:
                            idx = int(label.split("_")[1])
                            if 0 <= idx < len(self.labels):
                                probabilities[self.labels[idx]] = result.get("score", 0.0)
                        except:
                            continue
                    
                    return {
                        "classification": class_idx,
                        "probabilities": probabilities
                    }
                else:
                    # Return default if response format unexpected
                    return {
                        "error": "Unexpected API response format",
                        "classification": 0,  # Default to clean
                        "probabilities": {
                            "clean": 1.0,
                            "offensive": 0.0,
                            "hate": 0.0,
                            "spam": 0.0
                        }
                    }
                
        except Exception as e:
            return {
                "error": f"Error calling HuggingFace API: {str(e)}",
                "classification": 0,  # Default to clean
                "probabilities": {
                    "clean": 1.0,
                    "offensive": 0.0,
                    "hate": 0.0,
                    "spam": 0.0
                }
            }

    async def predict(self, text: str) -> Dict[str, Any]:
        """Predict toxicity of text"""
        prediction_result = {}
        
        if self.is_huggingface_api:
            prediction_result = await self.predict_huggingface(text)
        else:
            prediction_result = await self.predict_local(text)
        
        # Generate embedding for vector storage regardless of prediction method
        embedding = await self.get_embeddings(text)
        
        # Add embedding to result as JSON
        prediction_result["embedding_json"] = json.dumps(embedding.tolist())
        
        return prediction_result

# Singleton instance
toxicity_detector = ToxicityDetector()