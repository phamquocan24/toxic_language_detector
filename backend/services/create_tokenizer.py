"""
Script to create a proper Vietnamese tokenizer for the model
"""
import os
import pickle
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("create_tokenizer")

def load_stopwords(filepath="data/vietnamese_stopwords.txt"):
    """Load Vietnamese stopwords"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            stopwords = [line.strip() for line in f.readlines()]
        logger.info(f"Loaded {len(stopwords)} Vietnamese stopwords")
        return stopwords
    except Exception as e:
        logger.error(f"Error loading stopwords: {e}")
        return []

def preprocess_text(text, stopwords=None):
    """Basic preprocessing for Vietnamese text"""
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove stopwords if provided
    if stopwords:
        words = text.split()
        words = [word for word in words if word not in stopwords]
        text = " ".join(words)
    
    return text

def create_tokenizer(max_words=20000, save_path="model/tokenizer.pkl"):
    """Create and save a Vietnamese tokenizer"""
    try:
        # Try to load training data
        train_data_path = "model/balanced_train.csv"
        if os.path.exists(train_data_path):
            logger.info(f"Loading training data from {train_data_path}")
            df = pd.read_csv(train_data_path)
            
            # Extract text column (assuming it's named 'text' or 'comment')
            text_col = next((col for col in df.columns if col.lower() in ['text', 'comment', 'content', 'văn bản']), None)
            
            if text_col:
                # Get texts from the dataset
                texts = df[text_col].astype(str).values
                logger.info(f"Found {len(texts)} texts in training data")
                
                # Preprocess texts
                stopwords = load_stopwords()
                processed_texts = [preprocess_text(text, stopwords) for text in texts]
                
                # Create tokenizer
                tokenizer = Tokenizer(num_words=max_words, oov_token='<OOV>')
                tokenizer.fit_on_texts(processed_texts)
                
                logger.info(f"Created tokenizer with {len(tokenizer.word_index)} words")
                
                # Save tokenizer
                with open(save_path, 'wb') as f:
                    pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                logger.info(f"Tokenizer saved to {save_path}")
                return tokenizer
            else:
                logger.warning("Could not find text column in training data")
        else:
            logger.warning(f"Training data not found at {train_data_path}")
        
        # Fallback to creating a basic tokenizer if training data isn't available
        logger.info("Creating basic tokenizer with common Vietnamese words")
        sample_texts = [
            "xin chào", "cảm ơn", "không", "có", "tốt", "xấu", "thích", "ghét",
            "vui", "buồn", "giận dữ", "bình thường", "tuyệt vời", "tệ", "ngôn từ",
            "tiếng việt", "ngôn ngữ", "học máy", "trí tuệ nhân tạo", "mô hình",
            "xúc phạm", "thù ghét", "độc hại", "bình luận", "mạng xã hội",
            "facebook", "youtube", "twitter", "instagram", "tiktok",
            "spam", "quảng cáo", "tin nhắn", "email", "tin tức",
            "chính trị", "kinh tế", "xã hội", "văn hóa", "thể thao"
        ]
        
        # Add words from offensive words list
        try:
            with open("data/vietnamese_offensive_words.txt", 'r', encoding='utf-8') as f:
                offensive_words = [line.strip() for line in f.readlines()]
                sample_texts.extend(offensive_words)
        except Exception as e:
            logger.error(f"Error loading offensive words: {e}")
        
        # Create tokenizer
        tokenizer = Tokenizer(num_words=max_words, oov_token='<OOV>')
        tokenizer.fit_on_texts(sample_texts)
        
        # Save tokenizer
        with open(save_path, 'wb') as f:
            pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.info(f"Basic tokenizer created and saved to {save_path}")
        return tokenizer
            
    except Exception as e:
        logger.error(f"Error creating tokenizer: {e}")
        raise

if __name__ == "__main__":
    create_tokenizer() 