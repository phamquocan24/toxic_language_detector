"""
Script to help convert between PyTorch and TensorFlow model weights
"""
import os
import json
import logging
import numpy as np
from typing import Dict, Any, Tuple, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("model_converter")

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load model configuration from JSON file
    
    Args:
        config_path: Path to config.json file
        
    Returns:
        Dict containing model configuration
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Loaded model config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def convert_lstm_weights(
    input_hidden_weights: np.ndarray,
    hidden_hidden_weights: np.ndarray,
    input_hidden_bias: np.ndarray,
    hidden_hidden_bias: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert LSTM weights from PyTorch format to TensorFlow format
    
    Args:
        input_hidden_weights: PyTorch input-hidden weights (weight_ih_l0)
        hidden_hidden_weights: PyTorch hidden-hidden weights (weight_hh_l0)
        input_hidden_bias: PyTorch input-hidden bias (bias_ih_l0)
        hidden_hidden_bias: PyTorch hidden-hidden bias (bias_hh_l0)
        
    Returns:
        Tuple of TensorFlow weights (kernel, recurrent_kernel, bias)
    """
    try:
        # PyTorch LSTM weights order: (input_size, 4*hidden_size)
        # TensorFlow LSTM weights order: (4*hidden_size, input_size)
        # Need to transpose
        kernel = np.transpose(input_hidden_weights, [1, 0])
        recurrent_kernel = np.transpose(hidden_hidden_weights, [1, 0])
        
        # For bias, TensorFlow concatenates input_hidden_bias and hidden_hidden_bias
        bias = input_hidden_bias + hidden_hidden_bias
        
        # LSTM gate order is different between PyTorch and TensorFlow
        # PyTorch: (input, forget, cell, output)
        # TensorFlow: (input, cell, forget, output)
        # Need to reorder the weights
        
        # Function to reorder gates
        def reorder_gates(weights, hidden_size):
            # Split along the last dimension into 4 gates
            weights_split = np.split(weights, 4, axis=-1)
            
            # Reorder gates: input, forget, cell, output -> input, cell, forget, output
            reordered = [
                weights_split[0],  # input (i) - stays the same
                weights_split[2],  # cell (c) - was at index 2
                weights_split[1],  # forget (f) - was at index 1
                weights_split[3],  # output (o) - stays the same
            ]
            
            # Concatenate back
            return np.concatenate(reordered, axis=-1)
        
        # Get hidden size
        hidden_size = input_hidden_bias.shape[0] // 4
        
        # Reorder gate weights
        kernel = reorder_gates(kernel, hidden_size)
        recurrent_kernel = reorder_gates(recurrent_kernel, hidden_size)
        bias = reorder_gates(bias, hidden_size)
        
        return kernel, recurrent_kernel, bias
    
    except Exception as e:
        logger.error(f"Error converting LSTM weights: {e}")
        raise

def convert_dense_weights(
    weights: np.ndarray,
    bias: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert Dense layer weights from PyTorch format to TensorFlow format
    
    Args:
        weights: PyTorch weights
        bias: PyTorch bias
        
    Returns:
        Tuple of TensorFlow weights (kernel, bias)
    """
    try:
        # PyTorch Dense weights order: (out_features, in_features)
        # TensorFlow Dense weights order: (in_features, out_features)
        # Need to transpose
        kernel = np.transpose(weights, [1, 0])
        
        # Bias stays the same
        return kernel, bias
    
    except Exception as e:
        logger.error(f"Error converting Dense weights: {e}")
        raise

def generate_key_mapping() -> Dict[str, str]:
    """
    Generate mapping between PyTorch and TensorFlow weight keys
    
    Returns:
        Dict mapping PyTorch keys to TensorFlow keys
    """
    mapping = {
        # Embedding layer
        "embedding.weight": "embedding/embeddings",
        
        # LSTM layer
        "lstm.weight_ih_l0": "lstm/kernel",
        "lstm.weight_hh_l0": "lstm/recurrent_kernel",
        "lstm.bias_ih_l0": "lstm/bias (part 1)",
        "lstm.bias_hh_l0": "lstm/bias (part 2)",
        
        # Dense layers
        "dense.weight": "dense/kernel",
        "dense.bias": "dense/bias",
        "dense_1.weight": "dense_1/kernel",
        "dense_1.bias": "dense_1/bias"
    }
    
    return mapping

def update_model_adapter(
    layer_weights: Dict[str, List[str]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update model adapter code with correct weight mappings
    
    Args:
        layer_weights: Dict mapping layer names to weight keys
        config: Model configuration
        
    Returns:
        Dict containing updated model adapter code
    """
    # Define the layer-to-weight-keys mappings
    layer_to_weight_keys = {}
    
    # Map layer names to weight keys based on actual weights in safetensors file
    for layer_name, weight_keys in layer_weights.items():
        # Clean up the layer name to match TensorFlow conventions
        clean_name = layer_name.replace(".", "_").lower()
        if "embedding" in clean_name:
            layer_to_weight_keys["embedding"] = weight_keys
        elif "lstm" in clean_name:
            layer_to_weight_keys["lstm"] = weight_keys
        elif "dense" in clean_name or "linear" in clean_name or "fc" in clean_name:
            if "dense" not in layer_to_weight_keys:
                layer_to_weight_keys["dense"] = weight_keys
            else:
                layer_to_weight_keys["dense_1"] = weight_keys
    
    # Add layer mapping to config
    config["layer_to_weight_keys"] = layer_to_weight_keys
    
    # Save updated config
    config_path = "model/config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Updated model config with layer-to-weight-keys mappings at {config_path}")
    
    return config

def create_weight_conversion_script(
    config: Dict[str, Any],
    output_path: str = "model/convert_weights.py"
) -> None:
    """
    Create a Python script to convert weights between formats
    
    Args:
        config: Model configuration
        output_path: Path to save the conversion script
    """
    try:
        script_content = """
# Script to convert weights between PyTorch and TensorFlow formats
import os
import json
import numpy as np
from safetensors import safe_open
from safetensors.tensorflow import save_file
import tensorflow as tf

# Load config
with open("model/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Load original weights
model_path = "model/model.safetensors"
with safe_open(model_path, framework="tensorflow") as f:
    # Get all keys
    weights_dict = {key: f.get_tensor(key) for key in f.keys()}

# Create TensorFlow-compatible model
def create_model():
    vocab_size = config.get("vocab_size", 20000)
    embedding_dim = config.get("embedding_dim", 128)
    lstm_units = config.get("lstm_units", 128)
    max_length = config.get("max_length", 100)
    num_classes = config.get("num_classes", 4)
    hidden_layer_size = config.get("hidden_layer_size", 64)
    dropout_rate = config.get("dropout_rate", 0.2)
    
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
    return model

# Create model
model = create_model()

# Print model summary
model.summary()

# Convert PyTorch weights to TensorFlow format
tf_weights = {}

# Print available keys
print("Available weight keys:", list(weights_dict.keys()))

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

# Convert weights based on layer mapping
layer_to_weight_keys = config.get("layer_to_weight_keys", {})

# Try to apply weights to model
for layer in model.layers:
    if layer.name == "embedding" and "embedding" in layer_to_weight_keys:
        # Find embedding weight
        embedding_key = next((k for k in layer_to_weight_keys["embedding"] if "weight" in k), None)
        if embedding_key:
            embedding_weight = weights_dict[embedding_key]
            layer.set_weights([embedding_weight])
            print(f"Applied embedding weights from {embedding_key}")
    
    elif layer.name == "lstm" and "lstm" in layer_to_weight_keys:
        # Find LSTM weights
        weight_ih_key = next((k for k in layer_to_weight_keys["lstm"] if "weight_ih" in k), None)
        weight_hh_key = next((k for k in layer_to_weight_keys["lstm"] if "weight_hh" in k), None)
        bias_ih_key = next((k for k in layer_to_weight_keys["lstm"] if "bias_ih" in k), None)
        bias_hh_key = next((k for k in layer_to_weight_keys["lstm"] if "bias_hh" in k), None)
        
        if all([weight_ih_key, weight_hh_key, bias_ih_key, bias_hh_key]):
            # Convert LSTM weights
            kernel, recurrent_kernel, bias = convert_lstm_weights(
                weights_dict[weight_ih_key],
                weights_dict[weight_hh_key],
                weights_dict[bias_ih_key],
                weights_dict[bias_hh_key]
            )
            layer.set_weights([kernel, recurrent_kernel, bias])
            print(f"Applied LSTM weights from {weight_ih_key}, {weight_hh_key}, {bias_ih_key}, {bias_hh_key}")
    
    elif layer.name == "dense" and "dense" in layer_to_weight_keys:
        # Find Dense weights
        weight_key = next((k for k in layer_to_weight_keys["dense"] if "weight" in k), None)
        bias_key = next((k for k in layer_to_weight_keys["dense"] if "bias" in k), None)
        
        if weight_key and bias_key:
            # Convert Dense weights
            kernel, bias = convert_dense_weights(
                weights_dict[weight_key],
                weights_dict[bias_key]
            )
            layer.set_weights([kernel, bias])
            print(f"Applied Dense weights from {weight_key}, {bias_key}")
    
    elif layer.name == "dense_1" and "dense_1" in layer_to_weight_keys:
        # Find Dense weights
        weight_key = next((k for k in layer_to_weight_keys["dense_1"] if "weight" in k), None)
        bias_key = next((k for k in layer_to_weight_keys["dense_1"] if "bias" in k), None)
        
        if weight_key and bias_key:
            # Convert Dense weights
            kernel, bias = convert_dense_weights(
                weights_dict[weight_key],
                weights_dict[bias_key]
            )
            layer.set_weights([kernel, bias])
            print(f"Applied Dense_1 weights from {weight_key}, {bias_key}")

# Compile model
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Save model in TensorFlow format
model.save("model/converted_model.h5")
print("Model saved to model/converted_model.h5")

# Save model in TensorFlow SavedModel format
model.save("model/saved_model")
print("Model saved to model/saved_model")

# Test the model
print("Testing model with sample input...")
sample_input = np.zeros((1, config.get("max_length", 100)))
sample_input[0, 0] = 1  # Set first token to 1
prediction = model.predict(sample_input)
print("Sample prediction:", prediction)
"""
        
        # Write script to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Created weight conversion script at {output_path}")
    
    except Exception as e:
        logger.error(f"Error creating weight conversion script: {e}")

if __name__ == "__main__":
    # Load config
    config_path = "model/config.json"
    config = load_config(config_path)
    
    # Create extract_weights.py script if it doesn't exist
    extract_weights_path = "backend/services/extract_weights.py"
    if not os.path.exists(extract_weights_path):
        logger.error(f"extract_weights.py script not found at {extract_weights_path}")
        logger.info("Please create and run extract_weights.py first")
    
    # Run extract_weights.py script if needed
    model_path = "model/model.safetensors"
    try:
        from backend.services.extract_weights import extract_weight_names
        layer_weights = extract_weight_names(model_path)
        if layer_weights:
            # Update model adapter
            updated_config = update_model_adapter(layer_weights, config)
            
            # Create weight conversion script
            create_weight_conversion_script(updated_config)
    except ImportError:
        logger.error("Could not import extract_weights module")
        logger.info("Please run extract_weights.py first") 