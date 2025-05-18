"""
Fix model loading issues by:
1. Analyzing the existing safetensors model
2. Creating a proper tokenizer
3. Updating the model configuration
4. Generating a converted model in TensorFlow format
"""
import os
import sys
import logging
import json
import shutil
import subprocess
import pickle
import numpy as np
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fix_model_loading")

# Check Python packages
required_packages = [
    "tensorflow",
    "safetensors",
    "pandas",
    "numpy"
]

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_missing_packages():
    """Install missing packages"""
    missing_packages = [pkg for pkg in required_packages if not check_package(pkg)]
    if missing_packages:
        logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
        for pkg in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                logger.info(f"Successfully installed {pkg}")
            except subprocess.CalledProcessError:
                logger.error(f"Failed to install {pkg}")
    else:
        logger.info("All required packages are already installed")

def create_tokenizer():
    """Create a proper tokenizer for the Vietnamese model"""
    logger.info("Creating tokenizer...")
    
    from tensorflow.keras.preprocessing.text import Tokenizer
    
    # Load stopwords from file
    stopwords = []
    try:
        with open("data/vietnamese_stopwords.txt", 'r', encoding='utf-8') as f:
            stopwords = [line.strip() for line in f.readlines() if line.strip()]
        logger.info(f"Loaded {len(stopwords)} Vietnamese stopwords")
    except Exception as e:
        logger.warning(f"Could not load stopwords: {e}")
    
    # Try to find the training data
    try:
        import pandas as pd
        
        train_data_path = "model/balanced_train.csv"
        if os.path.exists(train_data_path):
            logger.info(f"Loading training data from {train_data_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(train_data_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None:
                # Try to find text column
                text_columns = [col for col in df.columns if col.lower() in ['text', 'comment', 'content', 'văn bản']]
                if text_columns:
                    text_col = text_columns[0]
                    logger.info(f"Found text column: {text_col}")
                    
                    # Extract texts for tokenizer
                    texts = df[text_col].astype(str).values
                    logger.info(f"Extracted {len(texts)} texts for tokenizer")
                    
                    # Create tokenizer
                    tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
                    tokenizer.fit_on_texts(texts)
                    
                    # Save tokenizer
                    with open("model/tokenizer.pkl", 'wb') as f:
                        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
                    
                    logger.info(f"Created tokenizer with {len(tokenizer.word_index)} words")
                    return tokenizer
                else:
                    logger.warning("Could not find text column in training data")
            else:
                logger.warning(f"Could not load training data with available encodings")
    except Exception as e:
        logger.warning(f"Error processing training data: {e}")
    
    # Create basic tokenizer if training data approach failed
    logger.info("Creating basic tokenizer with Vietnamese vocabulary")
    
    # Combine Vietnamese vocabulary from different sources
    vocab_strings = []
    
    # Load vocabulary from vi-vocab file if available
    vi_vocab_path = "model/vi-vocab"
    if os.path.exists(vi_vocab_path):
        try:
            # Try to decode tokens from binary format properly
            vietnamese_words = []
            with open(vi_vocab_path, 'rb') as f:
                content = f.read()
                try:
                    # Try to decode as utf-8
                    for line in content.split(b'\n'):
                        try:
                            if line.strip():
                                word = line.strip().decode('utf-8')
                                if len(word) < 100:  # Skip long lines
                                    vietnamese_words.append(word)
                        except UnicodeDecodeError:
                            pass
                except Exception:
                    logger.warning("Could not decode vi-vocab as UTF-8")
            
            vocab_strings.extend(vietnamese_words)
            logger.info(f"Loaded {len(vietnamese_words)} words from vi-vocab")
        except Exception as e:
            logger.warning(f"Could not load vi-vocab: {e}")
    
    # Add offensive words
    try:
        with open("data/vietnamese_offensive_words.txt", 'r', encoding='utf-8') as f:
            offensive_words = [line.strip() for line in f.readlines() if line.strip()]
            vocab_strings.extend(offensive_words)
        logger.info(f"Added {len(offensive_words)} offensive words to vocabulary")
    except Exception as e:
        logger.warning(f"Could not load offensive words: {e}")
    
    # Add common Vietnamese words
    common_words = [
        "xin chào", "cảm ơn", "không", "có", "tốt", "xấu", "thích", "ghét",
        "vui", "buồn", "giận dữ", "bình thường", "tuyệt vời", "tệ", "ngôn từ",
        "tiếng việt", "ngôn ngữ", "học máy", "trí tuệ nhân tạo", "mô hình",
        "xúc phạm", "thù ghét", "độc hại", "bình luận", "mạng xã hội",
        "facebook", "youtube", "twitter", "instagram", "tiktok",
        "spam", "quảng cáo", "tin nhắn", "email", "tin tức",
        "chính trị", "kinh tế", "xã hội", "văn hóa", "thể thao"
    ]
    vocab_strings.extend(common_words)
    
    # Create tokenizer
    tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
    tokenizer.fit_on_texts(vocab_strings)
    
    # Save tokenizer
    with open("model/tokenizer.pkl", 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    logger.info(f"Created basic tokenizer with {len(tokenizer.word_index)} words")
    return tokenizer

def analyze_safetensors_model():
    """Analyze the safetensors model to identify weight names and shapes"""
    logger.info("Analyzing safetensors model...")
    
    try:
        from safetensors import safe_open
        
        model_path = "model/model.safetensors"
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return {}
        
        # Extract weight names and shapes
        weights_info = {}
        
        with safe_open(model_path, framework="tensorflow") as f:
            for key in f.keys():
                tensor = f.get_tensor(key)
                weights_info[key] = {
                    "shape": tuple(tensor.shape),
                    "dtype": str(tensor.dtype)
                }
        
        logger.info(f"Found {len(weights_info)} weights in the model")
        
        # Group weights by layer
        layer_weights = {}
        for key in weights_info:
            if "." in key:
                layer_name = key.split(".")[0]
            else:
                layer_name = key
                
            if layer_name not in layer_weights:
                layer_weights[layer_name] = []
                
            layer_weights[layer_name].append(key)
        
        logger.info(f"Identified {len(layer_weights)} layers: {list(layer_weights.keys())}")
        
        # Save weights info to file for inspection
        with open("model/weights_info.json", 'w', encoding='utf-8') as f:
            # Convert shapes to strings for JSON serialization
            for key, value in weights_info.items():
                value["shape"] = str(value["shape"])
            json.dump(weights_info, f, indent=2)
        
        logger.info("Saved weights info to model/weights_info.json")
        
        return layer_weights
    
    except Exception as e:
        logger.error(f"Error analyzing safetensors model: {e}")
        return {}

def update_config_file(layer_weights):
    """Update the config.json file with the correct model architecture"""
    logger.info("Updating config.json file...")
    
    try:
        # Load existing config
        config_path = "model/config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Add layer names to config
        config["layer_names"] = list(layer_weights.keys())
        
        # Map layer names to model structure
        layer_mapping = {}
        for layer_name in layer_weights:
            if "embedding" in layer_name.lower():
                layer_mapping["embedding"] = layer_name
            elif "lstm" in layer_name.lower():
                layer_mapping["lstm"] = layer_name
            elif "dense" in layer_name.lower() or "linear" in layer_name.lower() or "fc" in layer_name.lower():
                if "dense" not in layer_mapping:
                    layer_mapping["dense"] = layer_name
                elif "dense_output" not in layer_mapping or "dense_1" not in layer_mapping:
                    layer_mapping["dense_1"] = layer_name
        
        config["layer_mapping"] = layer_mapping
        
        # Add layer-to-weight-keys mapping
        config["layer_to_weight_keys"] = {
            layer_type: layer_weights[layer_name]
            for layer_type, layer_name in layer_mapping.items()
        }
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Updated config file at {config_path}")
        return config
    
    except Exception as e:
        logger.error(f"Error updating config file: {e}")
        return None

def update_model_adapter():
    """Update the model adapter code to properly handle safetensors weights"""
    logger.info("Updating model adapter code...")
    
    try:
        # Create backup of the original file
        adapter_path = "backend/services/model_adapter.py"
        backup_path = adapter_path + ".bak"
        
        if not os.path.exists(backup_path):
            shutil.copy2(adapter_path, backup_path)
            logger.info(f"Created backup of model adapter at {backup_path}")
        
        # Read the current config
        with open("model/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Get layer mappings
        layer_mapping = config.get("layer_mapping", {})
        
        # Read the model adapter file
        with open(adapter_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Update the _create_compatible_tf_model method to use the right layer names
        new_code = code.replace(
            "# Tạo model với kiến trúc tương thích - sử dụng tên layer chính xác",
            "# Tạo model với kiến trúc tương thích - sử dụng tên layer chính xác từ config"
        )
        
        # Add code to load layer mapping from config
        load_mapping_code = """
        # Load layer mappings from config if available
        config_path = os.path.join(os.path.dirname(model_path), "config.json")
        layer_mapping = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                layer_mapping = config_data.get("layer_mapping", {})
                logger.info(f"Loaded layer mappings from config: {layer_mapping}")
            except Exception as e:
                logger.warning(f"Error loading layer mappings from config: {e}")
        """
        
        new_code = new_code.replace(
            "# Tải weights từ file safetensors",
            load_mapping_code + "\n        # Tải weights từ file safetensors"
        )
        
        # Update the _apply_tf_weights method
        updated_apply_weights = """
    @staticmethod
    def _apply_tf_weights(model, weights_dict):
        \"\"\"
        Áp dụng weights từ safetensors vào model TensorFlow
        
        Args:
            model: Model TensorFlow
            weights_dict: Dictionary chứa tensor weights
        \"\"\"
        import tensorflow as tf
        
        # Load config to get layer mappings
        config_path = "model/config.json"
        layer_to_weight_keys = {}
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                layer_to_weight_keys = config.get("layer_to_weight_keys", {})
        except Exception as e:
            logger.warning(f"Could not load layer mappings from config: {e}")
        
        # If we don't have mappings from config, create default mappings
        if not layer_to_weight_keys:
            logger.info("Using default weight key mappings")
            layer_to_weight_keys = {
                'embedding': ['embedding.weight'],
                'lstm': ['lstm.weight_ih_l0', 'lstm.weight_hh_l0', 'lstm.bias_ih_l0', 'lstm.bias_hh_l0'],
                'dense': ['dense.weight', 'dense.bias'],
                'dense_1': ['dense_1.weight', 'dense_1.bias']
            }
        
        # Lấy danh sách layer name từ model
        layer_names = [layer.name for layer in model.layers]
        logger.info(f"Model layers: {layer_names}")
        
        # Lấy danh sách key từ weights_dict
        weight_keys = list(weights_dict.keys())
        logger.info(f"Available weight keys: {weight_keys[:5]}... (total {len(weight_keys)} keys)")
        
        # Áp dụng weights cho từng layer
        for layer in model.layers:
            layer_name = layer.name
            
            # Skip layer nếu không có weights hoặc không cần áp dụng (như Input layer)
            if layer_name not in layer_to_weight_keys or not layer.get_weights():
                continue
                
            weight_keys = layer_to_weight_keys[layer_name]
            if not all(key in weights_dict for key in weight_keys):
                logger.warning(f"Không tìm thấy weights cho {layer_name} trong safetensors")
                # Check if we have any keys at all
                available_keys = [key for key in weight_keys if key in weights_dict]
                if not available_keys:
                    continue
                logger.info(f"Using available keys for {layer_name}: {available_keys}")
            
            try:
                if layer_name == 'embedding':
                    # Chỉ có weight, không có bias
                    embedding_key = next((k for k in weight_keys if "weight" in k), None)
                    if embedding_key and embedding_key in weights_dict:
                        embedding_weight = weights_dict[embedding_key]
                        layer.set_weights([embedding_weight])
                        logger.info(f"Đã áp dụng weights cho layer {layer_name} từ {embedding_key}")
                    
                elif layer_name == 'lstm':
                    # LSTM có 3 weights: kernel, recurrent_kernel, bias
                    # Trong PyTorch/safetensors: weight_ih_l0, weight_hh_l0, bias_ih_l0 + bias_hh_l0
                    
                    # Find the weight keys
                    weight_ih_key = next((k for k in weight_keys if "weight_ih" in k), None)
                    weight_hh_key = next((k for k in weight_keys if "weight_hh" in k), None)
                    bias_ih_key = next((k for k in weight_keys if "bias_ih" in k), None)
                    bias_hh_key = next((k for k in weight_keys if "bias_hh" in k), None)
                    
                    if all([weight_ih_key, weight_hh_key, bias_ih_key, bias_hh_key]) and all(k in weights_dict for k in [weight_ih_key, weight_hh_key, bias_ih_key, bias_hh_key]):
                        # Lấy weights từ safetensors
                        weight_ih = weights_dict[weight_ih_key]  # Input-hidden weights
                        weight_hh = weights_dict[weight_hh_key]  # Hidden-hidden weights
                        bias_ih = weights_dict[bias_ih_key]      # Input-hidden bias
                        bias_hh = weights_dict[bias_hh_key]      # Hidden-hidden bias
                        
                        # Convert từ định dạng PyTorch sang TensorFlow
                        # PyTorch: (4*hidden_size, input_size) -> TF: (input_size, 4*hidden_size)
                        weight_ih_tf = tf.transpose(weight_ih, [1, 0])
                        
                        # PyTorch: (4*hidden_size, hidden_size) -> TF: (hidden_size, 4*hidden_size)
                        weight_hh_tf = tf.transpose(weight_hh, [1, 0])
                        
                        # Ghép bias_ih và bias_hh
                        bias_tf = bias_ih + bias_hh
                        
                        # Áp dụng weights
                        layer.set_weights([weight_ih_tf.numpy(), weight_hh_tf.numpy(), bias_tf.numpy()])
                        logger.info(f"Đã áp dụng weights cho layer {layer_name}")
                    
                elif layer_name in ['dense', 'dense_1']:
                    # Dense layer có weight và bias
                    weight_key = next((k for k in weight_keys if "weight" in k), None)
                    bias_key = next((k for k in weight_keys if "bias" in k), None)
                    
                    if weight_key and bias_key and weight_key in weights_dict and bias_key in weights_dict:
                        # Lấy weights từ safetensors
                        weight = weights_dict[weight_key]
                        bias = weights_dict[bias_key]
                        
                        # Convert từ định dạng PyTorch sang TensorFlow (transpose)
                        weight_tf = tf.transpose(weight, [1, 0])
                        
                        # Áp dụng weights
                        layer.set_weights([weight_tf.numpy(), bias.numpy()])
                        logger.info(f"Đã áp dụng weights cho layer {layer_name}")
            
            except Exception as e:
                logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")
                continue
"""
        
        # Replace the _apply_tf_weights method
        import re
        pattern = r"@staticmethod\s+def _apply_tf_weights\(model, weights_dict\):.*?def "
        new_code = re.sub(pattern, updated_apply_weights + "\n    def ", new_code, flags=re.DOTALL)
        
        # Save updated code
        with open(adapter_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        logger.info(f"Updated model adapter at {adapter_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating model adapter: {e}")
        return False

def create_converted_model():
    """Create a converted model in TensorFlow format"""
    logger.info("Creating converted model in TensorFlow format...")
    
    try:
        import tensorflow as tf
        from safetensors import safe_open
        
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
        inputs = tf.keras.Input(shape=(max_length,), name='input')
        
        # Embedding layer
        x = tf.keras.layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            input_length=max_length,
            name='embedding'
        )(inputs)
        
        # LSTM layer
        x = tf.keras.layers.LSTM(lstm_units, name='lstm')(x)
        
        # Dense layer
        x = tf.keras.layers.Dense(hidden_layer_size, activation='relu', name='dense')(x)
        x = tf.keras.layers.Dropout(dropout_rate, name='dropout')(x)
        
        # Output layer
        outputs = tf.keras.layers.Dense(num_classes, activation='softmax', name='dense_1')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs, name='vietnamese_hate_speech_model')
        
        # Load weights from safetensors
        model_path = "model/model.safetensors"
        layer_to_weight_keys = config.get("layer_to_weight_keys", {})
        
        with safe_open(model_path, framework="tensorflow") as f:
            # Get all keys
            weights_dict = {key: f.get_tensor(key) for key in f.keys()}
        
        # Helper to convert LSTM weights
        def convert_lstm_weights(
            input_hidden_weights,
            hidden_hidden_weights,
            input_hidden_bias,
            hidden_hidden_bias
        ):
            # Transpose weights
            kernel = np.transpose(input_hidden_weights, [1, 0])
            recurrent_kernel = np.transpose(hidden_hidden_weights, [1, 0])
            
            # Combine biases
            bias = input_hidden_bias + hidden_hidden_bias
            
            return kernel, recurrent_kernel, bias
        
        # Helper to convert Dense weights
        def convert_dense_weights(weights, bias):
            kernel = np.transpose(weights, [1, 0])
            return kernel, bias
        
        # Apply weights to model
        for layer in model.layers:
            if layer.name == "embedding" and "embedding" in layer_to_weight_keys:
                # Find embedding weight
                embedding_key = next((k for k in layer_to_weight_keys["embedding"] if "weight" in k), None)
                if embedding_key and embedding_key in weights_dict:
                    embedding_weight = weights_dict[embedding_key]
                    layer.set_weights([embedding_weight])
                    logger.info(f"Applied embedding weights from {embedding_key}")
            
            elif layer.name == "lstm" and "lstm" in layer_to_weight_keys:
                # Find LSTM weights
                weight_ih_key = next((k for k in layer_to_weight_keys["lstm"] if "weight_ih" in k), None)
                weight_hh_key = next((k for k in layer_to_weight_keys["lstm"] if "weight_hh" in k), None)
                bias_ih_key = next((k for k in layer_to_weight_keys["lstm"] if "bias_ih" in k), None)
                bias_hh_key = next((k for k in layer_to_weight_keys["lstm"] if "bias_hh" in k), None)
                
                if all([weight_ih_key, weight_hh_key, bias_ih_key, bias_hh_key]) and all(k in weights_dict for k in [weight_ih_key, weight_hh_key, bias_ih_key, bias_hh_key]):
                    # Convert LSTM weights
                    kernel, recurrent_kernel, bias = convert_lstm_weights(
                        weights_dict[weight_ih_key],
                        weights_dict[weight_hh_key],
                        weights_dict[bias_ih_key],
                        weights_dict[bias_hh_key]
                    )
                    layer.set_weights([kernel, recurrent_kernel, bias])
                    logger.info(f"Applied LSTM weights")
            
            elif layer.name == "dense" and "dense" in layer_to_weight_keys:
                # Find Dense weights
                weight_key = next((k for k in layer_to_weight_keys["dense"] if "weight" in k), None)
                bias_key = next((k for k in layer_to_weight_keys["dense"] if "bias" in k), None)
                
                if weight_key and bias_key and weight_key in weights_dict and bias_key in weights_dict:
                    # Convert Dense weights
                    kernel, bias = convert_dense_weights(
                        weights_dict[weight_key],
                        weights_dict[bias_key]
                    )
                    layer.set_weights([kernel, bias])
                    logger.info(f"Applied Dense weights")
            
            elif layer.name == "dense_1" and "dense_1" in layer_to_weight_keys:
                # Find Dense weights
                weight_key = next((k for k in layer_to_weight_keys["dense_1"] if "weight" in k), None)
                bias_key = next((k for k in layer_to_weight_keys["dense_1"] if "bias" in k), None)
                
                if weight_key and bias_key and weight_key in weights_dict and bias_key in weights_dict:
                    # Convert Dense weights
                    kernel, bias = convert_dense_weights(
                        weights_dict[weight_key],
                        weights_dict[bias_key]
                    )
                    layer.set_weights([kernel, bias])
                    logger.info(f"Applied Dense_1 weights")
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Save converted model
        model.save("model/converted_model.h5")
        logger.info("Saved converted model to model/converted_model.h5")
        
        # Save model in TensorFlow SavedModel format for easy loading
        model.save("model/saved_model")
        logger.info("Saved model in SavedModel format to model/saved_model")
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating converted model: {e}")
        return False

def main():
    """Main function to fix model loading issues"""
    logger.info("Starting model loading fix process...")
    
    # Check required directories
    os.makedirs("model", exist_ok=True)
    
    # Install missing packages
    install_missing_packages()
    
    # 1. Create tokenizer
    tokenizer = create_tokenizer()
    
    # 2. Analyze safetensors model
    layer_weights = analyze_safetensors_model()
    
    # 3. Update config.json
    if layer_weights:
        config = update_config_file(layer_weights)
    
    # 4. Update model adapter
    updated = update_model_adapter()
    
    # 5. Create converted model
    converted = create_converted_model()
    
    # Summary
    logger.info("\n--- Model loading fix summary ---")
    logger.info(f"Tokenizer created: {'Yes' if tokenizer else 'No'}")
    logger.info(f"Model analysis completed: {'Yes' if layer_weights else 'No'}")
    logger.info(f"Config updated: {'Yes' if 'config' in locals() and config else 'No'}")
    logger.info(f"Model adapter updated: {'Yes' if updated else 'No'}")
    logger.info(f"Converted model created: {'Yes' if converted else 'No'}")
    
    if all([tokenizer, layer_weights, 'config' in locals() and config, updated, converted]):
        logger.info("All fixes completed successfully!")
    else:
        logger.warning("Some fixes were not completed. Check the logs for details.")
    
    logger.info("\nNext steps:")
    logger.info("1. Use the new 'model/tokenizer.pkl' for tokenization")
    logger.info("2. Try loading the model using the fixed model adapter")
    logger.info("3. If issues persist, use the 'model/converted_model.h5' file directly")

if __name__ == "__main__":
    main() 