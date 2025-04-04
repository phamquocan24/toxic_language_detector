#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tiện ích để tải và sử dụng model đã nén bằng PCA
"""

import os
import numpy as np
import logging
import time
import tensorflow as tf
tf.experimental.numpy.experimental_enable_numpy_behavior()

logger = logging.getLogger(__name__)

def load_compressed_model(model_path):
    """
    Tải model đã nén bằng PCA
    
    Args:
        model_path: Đường dẫn đến file model đã nén
        
    Returns:
        dict: Bộ trọng số đã được phục hồi
    """
    try:
        from safetensors import safe_open
        
        start_time = time.time()
        logger.info(f"Đang tải model nén từ {model_path}")
        
        # Tải model đã nén
        with safe_open(model_path, framework="tf") as f:
            tensor_names = f.keys()
            compressed_dict = {}
            
            for name in tensor_names:
                compressed_dict[name] = f.get_tensor(name)
        
        # Phục hồi các trọng số gốc
        original_weights = {}
        tensors_reconstructed = 0
        tensors_kept = 0
        
        # Danh sách các hậu tố metadata của tensors đã nén
        compression_suffixes = ["_data", "_components", "_mean", "_shape", "_transpose"]
        
        # Tìm các tensor đã nén (có hậu tố _data)
        compressed_tensors = [name[:-5] for name in compressed_dict.keys() if name.endswith("_data")]
        logger.info(f"Tìm thấy {len(compressed_tensors)} tensors đã nén")
        
        # Phục hồi các tensor đã nén
        for base_name in compressed_tensors:
            try:
                # Lấy thông tin để phục hồi
                compressed_data = compressed_dict[f"{base_name}_data"]
                components = compressed_dict[f"{base_name}_components"]
                mean = compressed_dict[f"{base_name}_mean"]
                original_shape = tuple(compressed_dict[f"{base_name}_shape"].tolist())
                perform_transpose = compressed_dict.get(f"{base_name}_transpose", np.array([False]))[0]
                
                # Phục hồi dữ liệu gần đúng
                reconstructed = np.dot(compressed_data, components) + mean
                
                # Chuyển vị lại nếu cần
                if perform_transpose:
                    reconstructed = reconstructed.T
                
                # Reshape về kích thước ban đầu
                if len(original_shape) > 2:
                    reconstructed = reconstructed.reshape(original_shape)
                
                # Lưu vào từ điển trọng số gốc
                original_weights[base_name] = reconstructed
                tensors_reconstructed += 1
                
            except Exception as e:
                logger.error(f"Lỗi khi phục hồi tensor {base_name}: {str(e)}")
                # Nếu có lỗi, thử sử dụng tensor gốc nếu có
                if base_name in compressed_dict:
                    original_weights[base_name] = compressed_dict[base_name]
        
        # Thêm các tensor không nén
        for name in compressed_dict.keys():
            # Kiểm tra xem đây có phải là tensor đã nén hoặc metadata không
            is_compressed_data = False
            for suffix in compression_suffixes:
                if name.endswith(suffix):
                    is_compressed_data = True
                    break
            
            # Nếu không phải là tensor đã nén hoặc metadata, thêm vào kết quả
            if not is_compressed_data:
                original_weights[name] = compressed_dict[name]
                tensors_kept += 1
        
        logger.info(f"Đã phục hồi {tensors_reconstructed} tensors, sử dụng nguyên {tensors_kept} tensors")
        logger.info(f"Thời gian tải và giải nén: {time.time() - start_time:.2f} giây")
        
        return original_weights
        
    except Exception as e:
        logger.error(f"Lỗi khi tải model đã nén: {str(e)}")
        return None

def load_model_weights(model, weights_dict):
    """
    Áp dụng trọng số đã tải vào model
    
    Args:
        model: Model TensorFlow/Keras cần áp dụng trọng số
        weights_dict: Từ điển trọng số đã tải
        
    Returns:
        model: Model đã được áp dụng trọng số
    """
    try:
        import tensorflow as tf
        
        logger.info("Đang áp dụng trọng số vào model")
        start_time = time.time()
        
        # Ánh xạ từ tên layer sang layer object
        layer_dict = {layer.name: layer for layer in model.layers}
        
        # Đếm số layer đã cập nhật
        layers_updated = 0
        
        # Áp dụng trọng số cho từng layer
        for layer_name, layer in layer_dict.items():
            # Tìm các trọng số tương ứng với layer
            layer_weights = []
            for w_name in [f"{layer_name}/kernel", f"{layer_name}/bias", layer_name]:
                if w_name in weights_dict:
                    layer_weights.append(weights_dict[w_name])
            
            # Nếu tìm thấy trọng số và số lượng khớp với layer, áp dụng
            if layer_weights and len(layer_weights) == len(layer.get_weights()):
                try:
                    layer.set_weights(layer_weights)
                    layers_updated += 1
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng trọng số cho layer {layer_name}: {str(e)}")
        
        logger.info(f"Đã cập nhật {layers_updated}/{len(layer_dict)} layers")
        logger.info(f"Thời gian áp dụng trọng số: {time.time() - start_time:.2f} giây")
        
        return model
        
    except Exception as e:
        logger.error(f"Lỗi khi áp dụng trọng số: {str(e)}")
        return model