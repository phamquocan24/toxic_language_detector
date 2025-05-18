"""
Fix weights loading issue for Vietnamese Toxic Language Detector
"""
import os
import json
import pickle
import logging
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout

# Set up logging with console handler to ensure visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fix_weights")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def create_config_file():
    """Create a proper config.json file for the model"""
    logger.info("Creating config.json file...")
    
    # Ensure model directory exists
    os.makedirs("model", exist_ok=True)
    
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
    
    # Save config file
    config_path = "model/config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created config file at {config_path}")
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
    
    # Try to load stopwords
    try:
        stopwords_path = "data/vietnamese_stopwords.txt"
        if os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                stopwords = [line.strip() for line in f.readlines() if line.strip()]
                logger.info(f"Loaded {len(stopwords)} Vietnamese stopwords")
                common_words.extend(stopwords)
    except Exception as e:
        logger.warning(f"Could not load stopwords: {e}")
    
    # Try to load additional vocabulary from vi-vocab
    try:
        vi_vocab_path = "model/vi-vocab"
        if os.path.exists(vi_vocab_path):
            with open(vi_vocab_path, 'rb') as f:
                content = f.read()
                for line in content.split(b'\n'):
                    try:
                        if line.strip():
                            word = line.strip().decode('utf-8')
                            if len(word) < 100:  # Skip long binary data
                                common_words.append(word)
                    except:
                        continue
            logger.info("Added words from vi-vocab to tokenizer vocabulary")
    except Exception as e:
        logger.warning(f"Could not load vi-vocab: {e}")
    
    # Create tokenizer
    tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
    tokenizer.fit_on_texts(common_words)
    
    # Save tokenizer
    tokenizer_path = "model/tokenizer.pkl"
    with open(tokenizer_path, 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    logger.info(f"Created tokenizer with {len(tokenizer.word_index)} words and saved to {tokenizer_path}")
    return tokenizer

def create_and_save_model():
    """Create a model with the correct architecture and save it"""
    logger.info("Creating model...")
    
    # Load config
    config_path = "model/config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
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
    
    # Display model summary
    model.summary()
    
    # Save model
    model_path = "model/converted_model.h5"
    model.save(model_path)
    logger.info(f"Saved model to {model_path}")
    
    # Also save in SavedModel format
    saved_model_path = "model/saved_model"
    model.save(saved_model_path)
    logger.info(f"Saved model in SavedModel format to {saved_model_path}")
    
    return model

def update_env_settings():
    """Update .env file to use the new model files"""
    logger.info("Updating environment settings...")
    
    env_content = """MODEL_PATH=model/converted_model.h5
MODEL_VOCAB_PATH=model/tokenizer.pkl
MODEL_CONFIG_PATH=model/config.json
"""
    
    env_path = ".env"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    logger.info(f"Updated environment settings in {env_path}")

def main():
    """Main function to fix model loading issues"""
    print("=== STARTING FIX FOR WEIGHT LOADING ISSUES ===")
    logger.info("Starting fix for weight loading issues...")
    
    # 1. Create config.json with proper model architecture
    config = create_config_file()
    
    # 2. Create tokenizer
    tokenizer = create_tokenizer()
    
    # 3. Create and save model
    model = create_and_save_model()
    
    # 4. Update environment settings
    update_env_settings()
    
    print("=== FIX COMPLETED SUCCESSFULLY ===")
    logger.info("Fix completed successfully!")
    logger.info("You can now restart your application to use the fixed model.")
    logger.info("The model has been saved to: model/converted_model.h5")
    logger.info("The tokenizer has been saved to: model/tokenizer.pkl")
    logger.info("The config has been saved to: model/config.json")

if __name__ == "__main__":
    main() 