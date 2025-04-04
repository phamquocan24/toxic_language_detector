#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive Utility Module for Model Compression and Weight Management
Features:
- PCA-based model compression and decompression
- Flexible model weight loading
- Detailed logging and error handling
- Support for various deep learning model formats
"""

import os
import sys
import json
import logging
import time
import numpy as np
import tensorflow as tf
import h5py

# Ensure NumPy-like behavior for TensorFlow
tf.experimental.numpy.experimental_enable_numpy_behavior()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pca_model_utils.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ModelCompressionUtils:
    """
    Comprehensive utility class for model compression and weight management
    """
    
    @staticmethod
    def validate_model_path(model_path):
        """
        Validate the existence and type of model file
        
        Args:
            model_path (str): Path to the model file
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
        
        _, ext = os.path.splitext(model_path)
        valid_extensions = ['.h5', '.keras', '.safetensors', '.pt', '.pth']
        
        if ext.lower() not in valid_extensions:
            logger.warning(f"Unsupported model file extension: {ext}")
            return False
        
        return True
    
    @staticmethod
    def load_compressed_model(model_path, compression_info_path=None):
        """
        Load a compressed model with advanced handling
        
        Args:
            model_path (str): Path to compressed model file
            compression_info_path (str, optional): Path to compression metadata
        
        Returns:
            dict: Reconstructed model weights
        """
        if not ModelCompressionUtils.validate_model_path(model_path):
            return None
        
        try:
            start_time = time.time()
            logger.info(f"Attempting to load compressed model from {model_path}")
            
            # Compression metadata handling
            compression_metadata = {}
            if compression_info_path and os.path.exists(compression_info_path):
                try:
                    with open(compression_info_path, 'r') as f:
                        compression_metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load compression metadata: {e}")
            
            # Determine loading method based on file extension
            file_ext = os.path.splitext(model_path)[1].lower()
            weights = None
            
            if file_ext == '.safetensors':
                # SafeTensors handling
                from safetensors import safe_open
                weights = ModelCompressionUtils._load_safetensors(model_path)
            
            elif file_ext in ['.h5', '.keras']:
                # HDF5 handling
                weights = ModelCompressionUtils._load_hdf5(model_path)
            
            elif file_ext in ['.pt', '.pth']:
                # PyTorch model handling
                weights = ModelCompressionUtils._load_pytorch(model_path)
            
            # Apply compression metadata if available
            if weights and compression_metadata:
                weights = ModelCompressionUtils._apply_compression_metadata(
                    weights, compression_metadata
                )
            
            logger.info(f"Model load completed in {time.time() - start_time:.2f} seconds")
            return weights
        
        except Exception as e:
            logger.error(f"Error loading compressed model: {e}")
            return None
    
    @staticmethod
    def _load_safetensors(model_path):
        """
        Load weights from SafeTensors file
        """
        from safetensors import safe_open
        
        with safe_open(model_path, framework="tf", device="cpu") as f:
            tensor_names = f.keys()
            weights = {}
            
            for name in tensor_names:
                tensor = f.get_tensor(name)
                weights[name] = tensor.numpy() if hasattr(tensor, 'numpy') else tensor
        
        return weights
    
    @staticmethod
    def _load_hdf5(model_path):
        """
        Load weights from HDF5 file
        """
        with h5py.File(model_path, 'r') as f:
            weights = {}
            ModelCompressionUtils._recursively_load_hdf5(f, weights)
        
        return weights
    
    @staticmethod
    def _recursively_load_hdf5(h5_group, weights, prefix=''):
        """
        Recursively load weights from HDF5 group
        """
        for key, item in h5_group.items():
            current_name = f'{prefix}/{key}' if prefix else key
            
            if isinstance(item, h5py.Group):
                ModelCompressionUtils._recursively_load_hdf5(item, weights, current_name)
            else:
                weights[current_name] = item[()]
    
    @staticmethod
    def _load_pytorch(model_path):
        """
        Load weights from PyTorch model file
        """
        import torch
        
        checkpoint = torch.load(model_path, map_location='cpu')
        if 'state_dict' in checkpoint:
            weights = checkpoint['state_dict']
        else:
            weights = checkpoint
        
        # Convert weights to numpy
        numpy_weights = {}
        for key, value in weights.items():
            numpy_weights[key] = value.numpy() if torch.is_tensor(value) else value
        
        return numpy_weights
    
    @staticmethod
    def _apply_compression_metadata(weights, metadata):
        """
        Apply additional processing based on compression metadata
        """
        # Example of potential metadata processing
        if 'pca_params' in metadata:
            for tensor_name, pca_info in metadata['pca_params'].items():
                if tensor_name in weights:
                    # Reconstruct tensor using PCA parameters
                    compressed_data = weights.get(f'{tensor_name}_data')
                    components = weights.get(f'{tensor_name}_components')
                    mean = weights.get(f'{tensor_name}_mean')
                    
                    if all([compressed_data is not None, components is not None, mean is not None]):
                        reconstructed = np.dot(compressed_data, components) + mean
                        weights[tensor_name] = reconstructed
        
        return weights
    
    @staticmethod
    def load_model_weights(model, weights_dict, verbose=True, strict=False):
        """
        Load weights into a TensorFlow/Keras model with advanced matching
        
        Args:
            model: Keras model to load weights into
            weights_dict (dict): Dictionary of weights
            verbose (bool): Whether to print detailed loading info
            strict (bool): Raise error if weights cannot be fully loaded
        
        Returns:
            Loaded model
        """
        try:
            start_time = time.time()
            
            # Create layer name to weight mapping with various naming conventions
            layer_weights_map = {}
            for layer in model.layers:
                # Try multiple possible weight naming patterns
                possible_names = [
                    layer.name,
                    f"{layer.name}/kernel",
                    f"{layer.name}/bias",
                    f"{layer.name}.weight",
                    f"{layer.name}_weight"
                ]
                
                layer_weights_map[layer.name] = {
                    'layer': layer,
                    'possible_names': possible_names
                }
            
            # Track loading statistics
            stats = {
                'total_layers': len(layer_weights_map),
                'layers_updated': 0,
                'layers_skipped': 0
            }
            
            # Attempt to load weights for each layer
            for layer_name, layer_info in layer_weights_map.items():
                layer = layer_info['layer']
                possible_names = layer_info['possible_names']
                
                # Find matching weights
                matching_weights = []
                matched_source_names = []
                
                for name in possible_names:
                    if name in weights_dict:
                        matching_weights.append(weights_dict[name])
                        matched_source_names.append(name)
                
                # Check if weights can be applied
                if matching_weights and len(matching_weights) == len(layer.get_weights()):
                    try:
                        layer.set_weights(matching_weights)
                        stats['layers_updated'] += 1
                        
                        if verbose:
                            logger.info(f"Updated layer {layer_name} from {matched_source_names}")
                    except Exception as e:
                        logger.error(f"Error applying weights to {layer_name}: {e}")
                        if strict:
                            raise
                else:
                    stats['layers_skipped'] += 1
                    if verbose:
                        logger.warning(f"Skipped layer {layer_name}: No matching weights")
            
            # Log final statistics
            logger.info(f"Weight loading completed in {time.time() - start_time:.2f} seconds")
            logger.info(f"Layers updated: {stats['layers_updated']}/{stats['total_layers']}")
            logger.info(f"Layers skipped: {stats['layers_skipped']}")
            
            return model
        
        except Exception as e:
            logger.error(f"Critical error in weight loading: {e}")
            if strict:
                raise
            return model
    
    @staticmethod
    def perform_pca_compression(weights, variance_threshold=0.95):
        """
        Perform PCA compression on model weights
        
        Args:
            weights (np.ndarray): Input weight tensor
            variance_threshold (float): Percentage of variance to retain
        
        Returns:
            dict: Compressed weight representation
        """
        # Flatten and center the weights
        flat_weights = weights.reshape(weights.shape[0], -1)
        mean_weights = np.mean(flat_weights, axis=0)
        centered_weights = flat_weights - mean_weights
        
        # Perform SVD (more numerically stable than traditional PCA)
        U, S, Vt = np.linalg.svd(centered_weights, full_matrices=False)
        
        # Compute cumulative explained variance
        explained_variance_ratio = (S**2) / np.sum(S**2)
        cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
        
        # Determine number of components to retain
        n_components = np.argmax(cumulative_variance_ratio >= variance_threshold) + 1
        
        # Compress weights
        compressed_data = U[:, :n_components]
        components = Vt[:n_components, :]
        
        return {
            'data': compressed_data,
            'components': components,
            'mean': mean_weights,
            'original_shape': weights.shape,
            'variance_retained': cumulative_variance_ratio[n_components-1],
            'n_components': n_components
        }
    
    @staticmethod
    def save_model_with_compression_info(model, output_path, compression_metadata=None):
        """
        Save model with optional compression metadata
        
        Args:
            model: Keras model to save
            output_path (str): Path to save the model
            compression_metadata (dict, optional): Compression-related metadata
        """
        try:
            # Save model weights
            model.save(output_path)
            
            # Save compression metadata if provided
            if compression_metadata:
                metadata_path = os.path.splitext(output_path)[0] + '_compression_info.json'
                with open(metadata_path, 'w') as f:
                    json.dump(compression_metadata, f, indent=4)
                
                logger.info(f"Saved compression metadata to {metadata_path}")
        
        except Exception as e:
            logger.error(f"Error saving model: {e}")

def get_model_summary(model):
    """
    Get a detailed summary of the model's architecture
    
    Args:
        model: Keras model
    
    Returns:
        str: Detailed model summary
    """
    import io
    
    # Capture model summary in a string buffer
    summary_buffer = io.StringIO()
    model.summary(print_fn=lambda x: summary_buffer.write(x + '\n'))
    
    return summary_buffer.getvalue()

# Compatibility functions for direct module usage
def load_compressed_model(model_path, compression_info_path=None):
    """
    Convenience function for direct module usage
    """
    return ModelCompressionUtils.load_compressed_model(model_path, compression_info_path)

def load_model_weights(model, weights_dict, verbose=True, strict=False):
    """
    Convenience function for direct module usage
    """
    return ModelCompressionUtils.load_model_weights(model, weights_dict, verbose, strict)

def compress_model_weights(weights, variance_threshold=0.95):
    """
    Convenience function for PCA compression
    """
    return ModelCompressionUtils.perform_pca_compression(weights, variance_threshold)

# Main execution for testing
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logger.info("PCA Model Compression Utilities loaded successfully")