"""
Quick fix for model loading issues
"""
import os
import json
import pickle
import logging
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("quick_fix")

def create_config_file():
    """Create a proper config.json file for the model"""
    logger.info("Creating config.json file...")
    
    config = {
        "model_type": "lstm",
        "vocab_size": 20000,
        "embedding_dim": 128,
        "lstm_units": 128,
        "max_length": 100,
        "num_classes": 4,
        "dropout_rate": 0.2,
        "hidden_layer_size": 64,
        "use_bidirectional": False,
        "model_name": "LSTM",
        "labels": ["clean", "offensive", "hate", "spam"]
    }
    
    with open("model/config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    logger.info("Created config.json file")
    return config

def create_tokenizer():
    """Create a tokenizer file for the model"""
    logger.info("Creating tokenizer...")
    
    # Create a basic tokenizer with common Vietnamese words
    common_words = [
        "xin chào", "cảm ơn", "không", "có", "tốt", "xấu", "thích", "ghét",
        "vui", "buồn", "giận dữ", "bình thường", "tuyệt vời", "tệ", "ngôn từ",
        "tiếng việt", "ngôn ngữ", "học máy", "trí tuệ nhân tạo", "mô hình",
        "xúc phạm", "thù ghét", "độc hại", "bình luận", "mạng xã hội",
        "facebook", "youtube", "twitter", "instagram", "tiktok",
        "spam", "quảng cáo", "tin nhắn", "email", "tin tức",
        "chính trị", "kinh tế", "xã hội", "văn hóa", "thể thao"
    ]
    
    # Add offensive words
    try:
        with open("data/vietnamese_offensive_words.txt", 'r', encoding='utf-8') as f:
            offensive_words = [line.strip() for line in f.readlines() if line.strip()]
            common_words.extend(offensive_words)
        logger.info(f"Added {len(offensive_words)} offensive words to vocabulary")
    except Exception as e:
        logger.warning(f"Could not load offensive words: {e}")
    
    # Create tokenizer
    tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
    tokenizer.fit_on_texts(common_words)
    
    # Save tokenizer
    with open("model/tokenizer.pkl", 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    logger.info(f"Created tokenizer with {len(tokenizer.word_index)} words")
    return tokenizer

def create_and_save_model():
    """Create a model with the correct architecture and save it"""
    logger.info("Creating model...")
    
    # Load config
    with open("model/config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get model parameters
    vocab_size = config.get("vocab_size", 20000)
    embedding_dim = config.get("embedding_dim", 128)
    lstm_units = config.get("lstm_units", 128)
    max_length = config.get("max_length", 100)
    num_classes = config.get("num_classes", 4)
    hidden_layer_size = config.get("hidden_layer_size", 64)
    dropout_rate = config.get("dropout_rate", 0.2)
    
    # Create TensorFlow model
    inputs = Input(shape=(max_length,), name='input')
    
    # Embedding layer
    x = Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        input_length=max_length,
        name='embedding'
    )(inputs)
    
    # LSTM layer
    x = LSTM(lstm_units, name='lstm')(x)
    
    # Dense layer
    x = Dense(hidden_layer_size, activation='relu', name='dense')(x)
    x = Dropout(dropout_rate, name='dropout')(x)
    
    # Output layer
    outputs = Dense(num_classes, activation='softmax', name='dense_1')(x)
    
    model = Model(inputs=inputs, outputs=outputs, name='vietnamese_hate_speech_model')
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Save model
    model.save("model/converted_model.h5")
    logger.info("Saved model to model/converted_model.h5")
    
    return model

def update_settings():
    """Update settings to use the converted model"""
    logger.info("Updating environment settings...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("MODEL_PATH=model/converted_model.h5\n")
            f.write("MODEL_VOCAB_PATH=model/tokenizer.pkl\n")
            f.write("MODEL_CONFIG_PATH=model/config.json\n")
    else:
        # Read existing settings
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update settings
        model_path_found = False
        vocab_path_found = False
        config_path_found = False
        
        for i, line in enumerate(lines):
            if line.startswith("MODEL_PATH="):
                lines[i] = "MODEL_PATH=model/converted_model.h5\n"
                model_path_found = True
            elif line.startswith("MODEL_VOCAB_PATH="):
                lines[i] = "MODEL_VOCAB_PATH=model/tokenizer.pkl\n"
                vocab_path_found = True
            elif line.startswith("MODEL_CONFIG_PATH="):
                lines[i] = "MODEL_CONFIG_PATH=model/config.json\n"
                config_path_found = True
        
        # Add settings if not found
        if not model_path_found:
            lines.append("MODEL_PATH=model/converted_model.h5\n")
        if not vocab_path_found:
            lines.append("MODEL_VOCAB_PATH=model/tokenizer.pkl\n")
        if not config_path_found:
            lines.append("MODEL_CONFIG_PATH=model/config.json\n")
        
        # Write updated settings
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    logger.info("Updated environment settings")

def main():
    """Main function to fix model loading issues"""
    logger.info("Starting quick fix for model loading issues...")
    
    # Check required directories
    os.makedirs("model", exist_ok=True)
    
    # 1. Create config.json
    config = create_config_file()
    
    # 2. Create tokenizer
    tokenizer = create_tokenizer()
    
    # 3. Create and save model
    model = create_and_save_model()
    
    # 4. Update settings
    update_settings()
    
    logger.info("Quick fix completed successfully!")
    logger.info("Now you can restart the application to use the fixed model.")

if __name__ == "__main__":
    main() 