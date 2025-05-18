"""
Script to extract layer names and weights from safetensors file
"""
import os
import json
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("extract_weights")

def extract_weight_names(model_path: str) -> Dict[str, List[str]]:
    """
    Extract weight names from safetensors file
    
    Args:
        model_path: Path to the safetensors file
        
    Returns:
        Dict mapping layer types to weight names
    """
    try:
        # Import safetensors
        try:
            from safetensors import safe_open
        except ImportError:
            logger.error("safetensors package not installed. Please install with: pip install safetensors")
            return {}
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return {}
        
        # Extract weight names
        with safe_open(model_path, framework="tensorflow") as f:
            weight_names = f.keys()
        
        logger.info(f"Extracted {len(weight_names)} weight names from {model_path}")
        
        # Group weight names by layer type
        layer_weights = {}
        
        for name in weight_names:
            # Extract layer name from weight name
            if "." in name:
                layer_name = name.split(".")[0]
            else:
                layer_name = name
                
            if layer_name not in layer_weights:
                layer_weights[layer_name] = []
            
            layer_weights[layer_name].append(name)
        
        # Log the layer names
        logger.info(f"Found layers: {list(layer_weights.keys())}")
        
        return layer_weights
    
    except Exception as e:
        logger.error(f"Error extracting weight names: {e}")
        return {}

def update_config_file(config_path: str, layer_weights: Dict[str, List[str]]) -> bool:
    """
    Update config.json file with the correct layer names
    
    Args:
        config_path: Path to the config.json file
        layer_weights: Dictionary of layer names and their weights
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load existing config
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
            elif "gru" in layer_name.lower():
                layer_mapping["gru"] = layer_name
            elif "dense" in layer_name.lower() or "fc" in layer_name.lower() or "linear" in layer_name.lower():
                if "dense" not in layer_mapping:
                    layer_mapping["dense"] = layer_name
                elif "dense_output" not in layer_mapping:
                    layer_mapping["dense_output"] = layer_name
        
        config["layer_mapping"] = layer_mapping
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Updated config file at {config_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating config file: {e}")
        return False

def extract_weight_shapes(model_path: str) -> Dict[str, Any]:
    """
    Extract the shapes of weights from safetensors file
    
    Args:
        model_path: Path to the safetensors file
        
    Returns:
        Dict mapping weight names to their shapes
    """
    try:
        from safetensors import safe_open
        import numpy as np
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return {}
        
        # Extract weight shapes
        weight_shapes = {}
        
        with safe_open(model_path, framework="tensorflow") as f:
            for key in f.keys():
                tensor = f.get_tensor(key)
                weight_shapes[key] = tuple(tensor.shape)
        
        logger.info(f"Extracted shapes for {len(weight_shapes)} weights")
        
        # Save shapes to a JSON file for reference
        shapes_path = os.path.join(os.path.dirname(model_path), "weight_shapes.json")
        with open(shapes_path, 'w', encoding='utf-8') as f:
            # Convert shapes to strings for JSON serialization
            shapes_dict = {k: str(v) for k, v in weight_shapes.items()}
            json.dump(shapes_dict, f, indent=2)
        
        logger.info(f"Saved weight shapes to {shapes_path}")
        
        return weight_shapes
    
    except Exception as e:
        logger.error(f"Error extracting weight shapes: {e}")
        return {}

if __name__ == "__main__":
    # Extract weight names from safetensors file
    model_path = "model/model.safetensors"
    config_path = "model/config.json"
    
    layer_weights = extract_weight_names(model_path)
    if layer_weights:
        update_config_file(config_path, layer_weights)
        extract_weight_shapes(model_path) 