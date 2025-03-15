# services/ml_model.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import os

class MLModel:
    def __init__(self, model_path="model/best_model_LSTM.h5", max_length=100, max_words=10000):
        self.model_path = model_path
        self.max_length = max_length
        self.max_words = max_words
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the pretrained model"""
        if os.path.exists(self.model_path):
            self.model = tf.keras.models.load_model(self.model_path)
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"Model not found at {self.model_path}. Using dummy model.")
            # Create a dummy model for testing
            self.model = self._create_dummy_model()
        
        # Initialize tokenizer - in production, this should be loaded from a saved tokenizer
        self.tokenizer = Tokenizer(num_words=self.max_words)
    
    def _create_dummy_model(self):
        """Create a dummy model for testing purposes"""
        inputs = tf.keras.Input(shape=(self.max_length,))
        x = tf.keras.layers.Embedding(self.max_words, 64, input_length=self.max_length)(inputs)
        x = tf.keras.layers.LSTM(64)(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_text(self, text):
        """Preprocess text for prediction"""
        # Clean text
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Tokenize and pad
        sequences = self.tokenizer.texts_to_sequences([text])
        padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        
        return padded_sequences
    
    def predict(self, text):
        """Predict the class of the text"""
        # Preprocess text
        preprocessed_text = self.preprocess_text(text)
        
        # Make prediction
        prediction = self.model.predict(preprocessed_text)[0]
        
        # Get class and confidence
        predicted_class = np.argmax(prediction)
        confidence = float(prediction[predicted_class])
        
        return int(predicted_class), confidence