#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Công cụ nén model safetensors bằng PCA để giảm kích thước lưu trữ
Sử dụng: python compress_model.py input_model.safetensors output_model.safetensors
"""

import os
import sys
import numpy as np
import tensorflow as tf
from sklearn.decomposition import PCA
import logging
import argparse
import time
import traceback

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hàm tính kích thước (nbytes) an toàn cho cả numpy array và tensorflow tensor
def get_size_in_bytes(tensor):
    """Tính kích thước của tensor theo bytes một cách an toàn"""
    try:
        # Trường hợp numpy array
        if isinstance(tensor, np.ndarray):
            return tensor.nbytes
        # Trường hợp tensorflow tensor
        elif hasattr(tensor, 'numpy'):
            return tensor.numpy().nbytes
        else:
            # Ước tính kích thước dựa trên shape và dtype
            shape = tensor.shape
            if hasattr(tensor, 'dtype'):
                dtype = tensor.dtype
            else:
                dtype = np.float32  # Giả định là float32 nếu không biết
                
            # Tính kích thước dựa trên shape và dtype
            if hasattr(dtype, 'itemsize'):
                return np.prod(shape) * dtype.itemsize
            else:
                return np.prod(shape) * 4  # Giả định 4 bytes cho mỗi phần tử
    except Exception as e:
        logger.warning(f"Không thể tính kích thước chính xác: {e}")
        return sys.getsizeof(tensor)  # Fallback sử dụng getsizeof của Python

def ensure_tensor_format(tensor):
    """Đảm bảo tensor ở định dạng phù hợp với safetensors"""
    if isinstance(tensor, np.ndarray):
        # Đã là numpy array, chuyển về tensor TensorFlow
        return tf.convert_to_tensor(tensor)
    elif isinstance(tensor, tf.Tensor):
        # Đã là TensorFlow tensor
        return tensor
    else:
        # Trường hợp khác, thử chuyển về tensor
        return tf.convert_to_tensor(tensor)

def compress_model_with_pca(input_path, output_path, variance_ratio=0.9):
    """
    Nén model bằng PCA với tỷ lệ giữ nguyên variance cho trước
    
    Args:
        input_path: Đường dẫn đến file model gốc (.safetensors)
        output_path: Đường dẫn để lưu model đã nén
        variance_ratio: Tỷ lệ variance cần giữ lại (0.0 - 1.0)
    """
    try:
        # Kiểm tra nếu safetensors được cài đặt
        try:
            from safetensors import safe_open
            from safetensors.tensorflow import save_file
        except ImportError:
            logger.error("Thư viện safetensors chưa được cài đặt. Vui lòng cài đặt: pip install safetensors")
            return False
        
        logger.info(f"Bắt đầu nén model từ {input_path}")
        start_time = time.time()
        
        # Đọc model safetensors
        with safe_open(input_path, framework="tf") as f:
            tensor_names = f.keys()
            weights_dict = {}
            total_tensors = len(tensor_names)
            
            logger.info(f"Đã tìm thấy {total_tensors} tensors trong model")
            
            for i, name in enumerate(tensor_names):
                weights_dict[name] = f.get_tensor(name)
                if (i+1) % 10 == 0 or (i+1) == total_tensors:
                    logger.info(f"Đã đọc {i+1}/{total_tensors} tensors")
        
        # Kiểm tra kích thước model gốc
        original_size = sum(get_size_in_bytes(tensor) for tensor in weights_dict.values())
        logger.info(f"Kích thước model gốc: {original_size / (1024*1024):.2f} MB")
        
        # Áp dụng PCA cho các trọng số lớn
        compressed_weights = {}
        tensors_compressed = 0
        tensors_kept = 0
        
        logger.info(f"Áp dụng PCA với tỷ lệ giữ nguyên variance: {variance_ratio}")
        
        for name, weight in weights_dict.items():
            # Chuyển tensor về numpy array nếu cần
            if hasattr(weight, 'numpy'):
                weight = weight.numpy()
            
            # Chỉ áp dụng PCA cho các tensor lớn có 2 chiều trở lên
            if len(weight.shape) >= 2 and min(weight.shape) > 10 and np.prod(weight.shape) > 10000:
                # Lưu shape gốc
                original_shape = weight.shape
                
                # Reshape tensor thành ma trận 2D
                if len(weight.shape) > 2:
                    reshaped_weight = weight.reshape(weight.shape[0], -1)
                else:
                    reshaped_weight = weight
                
                # Kiểm tra xem tensor có đủ lớn để áp dụng PCA
                if min(reshaped_weight.shape) <= 1:
                    logger.info(f"Tensor {name} có kích thước quá nhỏ để áp dụng PCA: {weight.shape}")
                    compressed_weights[name] = ensure_tensor_format(weight)
                    tensors_kept += 1
                    continue
                
                # Xác định số components tối đa có thể sử dụng
                max_components = min(reshaped_weight.shape)
                n_samples, n_features = reshaped_weight.shape
                
                # Đảm bảo ma trận phù hợp với PCA (n_samples >= n_features)
                perform_transpose = False
                if n_samples < n_features:
                    logger.info(f"Chuyển vị ma trận {name} để tối ưu PCA: từ {reshaped_weight.shape} -> {reshaped_weight.T.shape}")
                    reshaped_weight = reshaped_weight.T
                    perform_transpose = True
                
                try:
                    # Tính số components cần thiết để đạt được variance mong muốn
                    logger.info(f"Đang áp dụng PCA cho tensor {name} với shape {weight.shape}")
                    
                    # Fit PCA để tìm số components tối ưu - Xử lý TruncatedSVD warning
                    n_comps = min(100, max_components)
                    pca = PCA(n_components=n_comps, random_state=42, svd_solver='auto')
                    pca.fit(reshaped_weight)
                    
                    # Tìm số components để đạt được explained_variance_ratio
                    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
                    
                    # Xử lý trường hợp NaN
                    if np.isnan(cumulative_variance).any():
                        logger.warning(f"Có giá trị NaN trong cumulative variance, chọn 1 component cho {name}")
                        n_components = 1
                    else:
                        indices = np.where(cumulative_variance >= variance_ratio)[0]
                        if len(indices) > 0:
                            n_components = indices[0] + 1  # +1 vì index bắt đầu từ 0
                        else:
                            n_components = 1  # Mặc định là 1 nếu không thể tìm được
                    
                    # Giới hạn số components để đảm bảo tiết kiệm dung lượng
                    n_components = min(n_components, max(1, max_components // 2))
                    
                    logger.info(f"Chọn {n_components} components để giữ {variance_ratio*100:.1f}% variance")
                    
                    # Áp dụng PCA với số components tối ưu
                    pca = PCA(n_components=n_components, random_state=42)
                    compressed = pca.fit_transform(reshaped_weight)
                    
                    # Chuyển đổi và lưu vào từ điển theo dạng tensor
                    compressed_weights[f"{name}_data"] = ensure_tensor_format(compressed.astype(np.float32))
                    compressed_weights[f"{name}_components"] = ensure_tensor_format(pca.components_.astype(np.float32))
                    compressed_weights[f"{name}_mean"] = ensure_tensor_format(pca.mean_.astype(np.float32))
                    compressed_weights[f"{name}_shape"] = ensure_tensor_format(np.array(original_shape, dtype=np.int32))
                    compressed_weights[f"{name}_transpose"] = ensure_tensor_format(np.array([perform_transpose], dtype=np.bool_))
                    
                    tensors_compressed += 1
                    
                    # Tính tỷ lệ nén
                    original_bytes = get_size_in_bytes(weight)
                    compressed_bytes = (get_size_in_bytes(compressed) + 
                                        get_size_in_bytes(pca.components_) + 
                                        get_size_in_bytes(pca.mean_) + 16)
                    compression_ratio = compressed_bytes / original_bytes
                    
                    logger.info(f"Tensor {name}: {original_bytes/(1024*1024):.2f} MB -> {compressed_bytes/(1024*1024):.2f} MB ({compression_ratio*100:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng PCA cho tensor {name}: {str(e)}")
                    compressed_weights[name] = ensure_tensor_format(weight)
                    tensors_kept += 1
            else:
                # Giữ nguyên các tensor nhỏ
                compressed_weights[name] = ensure_tensor_format(weight)
                tensors_kept += 1
        
        # Lưu model đã nén
        logger.info(f"Đang lưu model đã nén vào {output_path}")
        
        # Đảm bảo thư mục đích tồn tại
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Kiểm tra từng tensor trước khi lưu
        logger.info("Kiểm tra tensors trước khi lưu...")
        final_weights = {}
        for key, tensor in compressed_weights.items():
            # Đảm bảo tất cả là tensors TensorFlow
            if not isinstance(tensor, tf.Tensor):
                tensor = tf.convert_to_tensor(tensor)
            final_weights[key] = tensor
        
        # Lưu file
        try:
            save_file(final_weights, output_path)
            logger.info("Đã lưu model thành công")
        except Exception as e:
            logger.error(f"Lỗi khi lưu file: {e}")
            
            # Thử phương pháp lưu thay thế
            try:
                logger.info("Thử phương pháp lưu thay thế...")
                # Chuyển đổi lại sang numpy trước khi lưu
                numpy_dict = {k: v.numpy() if hasattr(v, 'numpy') else v for k, v in final_weights.items()}
                
                # Sử dụng phương pháp lưu thông qua pickle để debug
                import pickle
                with open(output_path + ".pkl", "wb") as f:
                    pickle.dump(numpy_dict, f)
                logger.info(f"Đã lưu model tạm thời ở dạng pickle: {output_path}.pkl")
                
                # Thử với safetensors một lần nữa với dict đã chuyển đổi
                from safetensors import numpy as safetensors_numpy
                safetensors_numpy.save_file(numpy_dict, output_path)
                logger.info(f"Lưu thành công với phương pháp thay thế")
            except Exception as e2:
                logger.error(f"Cả hai phương pháp lưu đều thất bại: {e2}")
                raise
        
        # Kiểm tra kích thước model đã nén
        if os.path.exists(output_path):
            compressed_size = os.path.getsize(output_path)
            compression_ratio = compressed_size / original_size
            
            logger.info(f"Kích thước model ban đầu: {original_size / (1024*1024):.2f} MB")
            logger.info(f"Kích thước model đã nén: {compressed_size / (1024*1024):.2f} MB")
            logger.info(f"Tỷ lệ nén: {compression_ratio*100:.1f}%")
            logger.info(f"Đã nén {tensors_compressed} tensors, giữ nguyên {tensors_kept} tensors")
            logger.info(f"Thời gian thực hiện: {time.time() - start_time:.2f} giây")
            
            return True
        else:
            logger.error(f"Không thể lưu file nén tại {output_path}")
            return False
        
    except Exception as e:
        logger.error(f"Lỗi khi nén model: {str(e)}")
        logger.error(traceback.format_exc())  # In traceback đầy đủ
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nén model safetensors bằng PCA")
    parser.add_argument("input_model", help="Đường dẫn đến file model safetensors cần nén")
    parser.add_argument("output_model", help="Đường dẫn lưu model đã nén")
    parser.add_argument("--variance", type=float, default=0.8, help="Tỷ lệ variance cần giữ lại (0.0 - 1.0)")
    parser.add_argument("--min-components", type=int, default=1, help="Số components tối thiểu cho mỗi tensor")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_model):
        logger.error(f"Không tìm thấy file model: {args.input_model}")
        sys.exit(1)
    
    success = compress_model_with_pca(args.input_model, args.output_model, args.variance)
    
    if success:
        logger.info("Nén model thành công!")
        sys.exit(0)
    else:
        logger.error("Nén model thất bại!")
        sys.exit(1)