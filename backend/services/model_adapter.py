# """
# Model Adapter - Lớp trung gian xử lý model safetensors
# """
# import os
# import tensorflow as tf
# import logging

# logger = logging.getLogger(__name__)

# class ModelAdapter:
#     """Adapter class để tải model từ định dạng .safetensors"""
    
#     @staticmethod
#     def load_model(model_path):
#         """
#         Tải model từ đường dẫn, tự động phát hiện định dạng
        
#         Args:
#             model_path: Đường dẫn đến file model
            
#         Returns:
#             tf.keras.Model: Model đã tải
#         """
#         if model_path.endswith('.safetensors'):
#             return ModelAdapter._load_from_safetensors(model_path)
#         else:
#             # Mặc định cho .h5 và các định dạng khác
#             return tf.keras.models.load_model(model_path)
    
#     @staticmethod
#     def _load_from_safetensors(model_path):
#         """
#         Tải model từ định dạng .safetensors
        
#         Args:
#             model_path: Đường dẫn đến file model .safetensors
            
#         Returns:
#             tf.keras.Model: Model đã tải
#         """
#         try:
#             from safetensors.tensorflow import load_file
            
#             # Tải weights từ file safetensors
#             weights_dict = load_file(model_path)
            
#             # Tạo model với kiến trúc tương tự model ban đầu
#             model = ModelAdapter._create_compatible_model()
            
#             # Áp dụng weights
#             ModelAdapter._apply_weights(model, weights_dict)
            
#             # Compile model
#             model.compile(
#                 optimizer='adam',
#                 loss='categorical_crossentropy',
#                 metrics=['accuracy']
#             )
            
#             return model
            
#         except Exception as e:
#             logger.error(f"Lỗi khi tải model safetensors: {str(e)}")
#             # Fallback về model .h5 nếu có
#             h5_path = model_path.replace('.safetensors', '.h5')
#             if os.path.exists(h5_path):
#                 logger.info(f"Fallback sang model .h5: {h5_path}")
#                 return tf.keras.models.load_model(h5_path)
#             raise RuntimeError(f"Không thể tải model: {str(e)}")
    
#     @staticmethod
#     def _create_compatible_model():
#         """
#         Tạo model tương thích với kiến trúc của model ban đầu
        
#         Returns:
#             tf.keras.Model: Model tương thích
#         """
#         # Tạo model với kiến trúc giống model ban đầu
#         inputs = tf.keras.Input(shape=(100,))
#         x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128)(inputs)
#         x = tf.keras.layers.LSTM(128)(x)
#         x = tf.keras.layers.Dense(64, activation='relu')(x)
#         x = tf.keras.layers.Dropout(0.2)(x)
#         outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
        
#         model = tf.keras.Model(inputs=inputs, outputs=outputs)
#         return model
    
#     @staticmethod
#     def _apply_weights(model, weights_dict):
#         """
#         Áp dụng weights từ safetensors vào model TensorFlow
        
#         Args:
#             model: Model TensorFlow
#             weights_dict: Dictionary chứa tensor weights
#         """
#         # Áp dụng weights cho từng layer
#         for layer in model.layers:
#             layer_name = layer.name
#             weights = layer.get_weights()
            
#             # Skip layer nếu không có weights
#             if not weights:
#                 continue
                
#             # Tìm tensor tương ứng cho mỗi weight
#             new_weights = []
#             for i, old_weight in enumerate(weights):
#                 # Thông thường, i=0 là kernel, i=1 là bias
#                 weight_type = "kernel" if i == 0 else "bias"
                
#                 # Các key name khả dĩ
#                 possible_keys = [
#                     f"{layer_name}.{weight_type}",
#                     f"{layer_name}/{weight_type}",
#                     layer_name if i == 0 else f"{layer_name}_bias"
#                 ]
                
#                 # Tìm key trong weights_dict
#                 tensor_key = None
#                 for key in possible_keys:
#                     if key in weights_dict:
#                         tensor = weights_dict[key]
#                         if tensor.shape == old_weight.shape:
#                             new_weights.append(tensor)
#                             break
#                 else:
#                     # Nếu không tìm thấy, giữ nguyên weight cũ
#                     new_weights.append(old_weight)
            
#             # Áp dụng weights mới
#             if len(new_weights) == len(weights):
#                 try:
#                     layer.set_weights(new_weights)
#                 except Exception as e:
#                     logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")
"""
Model Adapter - Lớp trung gian xử lý nhiều định dạng model khác nhau
"""
import os
import logging
import numpy as np
import json
from typing import Dict, Any, Optional, Union
from backend.config.settings import settings

# Thiết lập logging
logger = logging.getLogger("services.model_adapter")

class ModelAdapter:
    """Adapter class để tải model từ nhiều định dạng khác nhau"""
    
    @staticmethod
    def load_model(model_path: str, device: str = "cpu"):
        """
        Tải model từ đường dẫn, tự động phát hiện định dạng
        
        Args:
            model_path: Đường dẫn đến file model
            device: Thiết bị để chạy model ('cpu' hoặc 'cuda')
            
        Returns:
            Model: Model đã tải
        """
        model_format = ModelAdapter._detect_model_format(model_path)
        logger.info(f"Đã phát hiện định dạng model: {model_format} cho {model_path}")
        
        if model_format == "safetensors":
            return ModelAdapter._load_from_safetensors(model_path, device)
        elif model_format == "pytorch":
            return ModelAdapter._load_from_pytorch(model_path, device)
        elif model_format == "onnx":
            return ModelAdapter._load_from_onnx(model_path, device)
        elif model_format == "tensorflow":
            return ModelAdapter._load_from_tensorflow(model_path, device)
        elif model_format == "keras":
            return ModelAdapter._load_from_keras(model_path, device)
        else:
            raise ValueError(f"Không hỗ trợ định dạng model: {model_format}")
    
    @staticmethod
    def _detect_model_format(model_path: str) -> str:
        """
        Phát hiện định dạng model dựa trên phần mở rộng của file
        
        Args:
            model_path: Đường dẫn đến file model
            
        Returns:
            str: Định dạng model phát hiện được
        """
        if model_path.endswith(".safetensors"):
            return "safetensors"
        elif model_path.endswith(".pt") or model_path.endswith(".pth"):
            return "pytorch"
        elif model_path.endswith(".onnx"):
            return "onnx"
        elif model_path.endswith(".pb"):
            return "tensorflow"
        elif model_path.endswith(".h5") or model_path.endswith(".keras"):
            return "keras"
        else:
            # Thử đoán định dạng từ cấu trúc thư mục
            if os.path.isdir(model_path):
                if os.path.exists(os.path.join(model_path, "saved_model.pb")):
                    return "tensorflow"
                elif os.path.exists(os.path.join(model_path, "model.safetensors")):
                    return "safetensors"
            
            # Mặc định về Keras nếu không xác định được
            logger.warning(f"Không xác định được định dạng model từ {model_path}, mặc định về Keras")
            return "keras"
    
    @staticmethod
    def _load_from_safetensors(model_path: str, device: str) -> Any:
        """
        Tải model từ định dạng .safetensors
        
        Args:
            model_path: Đường dẫn đến file model .safetensors
            device: Thiết bị để chạy model
            
        Returns:
            Model: Model đã tải
        """
        try:
            from safetensors import safe_open
            
            # Tìm file cấu hình model
            config_path = os.path.join(os.path.dirname(model_path), "config.json")
            if not os.path.exists(config_path):
                config_path = model_path.replace(".safetensors", "_config.json")
            
            model_config = None
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    model_config = json.load(f)
                logger.info(f"Đã tải cấu hình model từ {config_path}")
            
            # Tải model dựa trên framework được cấu hình
            framework = settings.ML_FRAMEWORK.lower() if hasattr(settings, 'ML_FRAMEWORK') else "tensorflow"
            
            if framework == "pytorch":
                try:
                    import torch
                    from safetensors.torch import load_file
                    
                    # Tạo model PyTorch
                    model = ModelAdapter._create_pytorch_model(model_config)
                    
                    # Tải weights
                    weights_dict = load_file(model_path)
                    
                    # Áp dụng weights
                    model.load_state_dict(weights_dict)
                    
                    # Chuyển model sang device
                    device_obj = torch.device(device)
                    model = model.to(device_obj)
                    
                    # Chuyển model sang eval mode
                    model.eval()
                    
                    # Tạo wrapper để prediction API tương thích với Keras
                    model.predict = lambda x: ModelAdapter._pytorch_predict_wrapper(model, x)
                    
                    return model
                    
                except ImportError:
                    logger.warning("PyTorch không được cài đặt, chuyển sang TensorFlow")
                    framework = "tensorflow"
            
            if framework == "tensorflow":
                try:
                    import tensorflow as tf
                    from safetensors.tensorflow import load_file
                    
                    # Tải weights từ file safetensors
                    weights_dict = load_file(model_path)
                    
                    # Tạo model với kiến trúc tương thích
                    model = ModelAdapter._create_compatible_tf_model(model_config)
                    
                    # Áp dụng weights
                    ModelAdapter._apply_tf_weights(model, weights_dict)
                    
                    # Compile model
                    model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    return model
                    
                except ImportError:
                    logger.error("TensorFlow không được cài đặt")
                    raise
            
            raise ValueError(f"Framework không được hỗ trợ: {framework}")
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model safetensors: {str(e)}")
            # Fallback về model .h5 nếu có
            h5_path = model_path.replace('.safetensors', '.h5')
            if os.path.exists(h5_path):
                logger.info(f"Fallback sang model .h5: {h5_path}")
                return ModelAdapter._load_from_keras(h5_path, device)
            raise RuntimeError(f"Không thể tải model: {str(e)}")
    
    @staticmethod
    def _load_from_pytorch(model_path: str, device: str) -> Any:
        """
        Tải model từ định dạng PyTorch
        
        Args:
            model_path: Đường dẫn đến file model PyTorch
            device: Thiết bị để chạy model
            
        Returns:
            Model: Model đã tải
        """
        try:
            import torch
            
            # Tải model
            model = torch.load(model_path, map_location=device)
            
            # Nếu là state_dict, tạo model và load weights
            if isinstance(model, dict):
                # Tìm file cấu hình model
                config_path = os.path.join(os.path.dirname(model_path), "config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        model_config = json.load(f)
                    
                    # Tạo model từ cấu hình
                    model_instance = ModelAdapter._create_pytorch_model(model_config)
                    model_instance.load_state_dict(model)
                    model = model_instance
            
            # Chuyển model sang eval mode
            model.eval()
            
            # Tạo wrapper để prediction API tương thích với Keras
            model.predict = lambda x: ModelAdapter._pytorch_predict_wrapper(model, x)
            
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model PyTorch: {str(e)}")
            raise RuntimeError(f"Không thể tải model PyTorch: {str(e)}")
    
    @staticmethod
    def _load_from_onnx(model_path: str, device: str) -> Any:
        """
        Tải model từ định dạng ONNX
        
        Args:
            model_path: Đường dẫn đến file model ONNX
            device: Thiết bị để chạy model
            
        Returns:
            Model: Model đã tải
        """
        try:
            import onnxruntime as ort
            
            # Thiết lập ONNX Runtime session
            sess_options = ort.SessionOptions()
            providers = ['CPUExecutionProvider']
            if device.lower() == 'cuda' and 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.insert(0, 'CUDAExecutionProvider')
            
            session = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
            
            # Tạo wrapper class cho prediction API
            class ONNXModel:
                def __init__(self, session):
                    self.session = session
                    self.input_name = session.get_inputs()[0].name
                
                def predict(self, x):
                    # Đảm bảo x là numpy array
                    if not isinstance(x, np.ndarray):
                        x = np.array(x)
                    
                    # Thực hiện inference
                    outputs = self.session.run(None, {self.input_name: x})
                    return outputs[0]
            
            return ONNXModel(session)
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model ONNX: {str(e)}")
            raise RuntimeError(f"Không thể tải model ONNX: {str(e)}")
    
    @staticmethod
    def _load_from_tensorflow(model_path: str, device: str) -> Any:
        """
        Tải model từ định dạng TensorFlow SavedModel
        
        Args:
            model_path: Đường dẫn đến thư mục chứa SavedModel
            device: Thiết bị để chạy model
            
        Returns:
            Model: Model đã tải
        """
        try:
            import tensorflow as tf
            
            # Thiết lập device
            if device.lower() == 'cuda':
                # Kiểm tra và thiết lập GPU nếu có
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    try:
                        for gpu in gpus:
                            tf.config.experimental.set_memory_growth(gpu, True)
                    except RuntimeError as e:
                        logger.warning(f"Lỗi khi thiết lập GPU: {str(e)}")
            else:
                # Tắt GPU nếu chỉ định CPU
                tf.config.set_visible_devices([], 'GPU')
            
            # Tải model
            model = tf.saved_model.load(model_path)
            
            # Tạo wrapper nếu cần
            if not hasattr(model, 'predict'):
                class TFModelWrapper:
                    def __init__(self, model):
                        self.model = model
                    
                    def predict(self, x):
                        # Đảm bảo x là tensor
                        if not isinstance(x, tf.Tensor):
                            x = tf.convert_to_tensor(x)
                        
                        # Thực hiện inference
                        result = self.model(x)
                        
                        # Chuyển kết quả về numpy nếu cần
                        if isinstance(result, tf.Tensor):
                            return result.numpy()
                        return result
                
                model = TFModelWrapper(model)
            
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model TensorFlow: {str(e)}")
            raise RuntimeError(f"Không thể tải model TensorFlow: {str(e)}")
    
    @staticmethod
    def _load_from_keras(model_path: str, device: str) -> Any:
        """
        Tải model từ định dạng Keras (.h5 hoặc .keras)
        
        Args:
            model_path: Đường dẫn đến file model Keras
            device: Thiết bị để chạy model
            
        Returns:
            Model: Model đã tải
        """
        try:
            import tensorflow as tf
            
            # Thiết lập device
            if device.lower() == 'cuda':
                # Kiểm tra và thiết lập GPU nếu có
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    try:
                        for gpu in gpus:
                            tf.config.experimental.set_memory_growth(gpu, True)
                    except RuntimeError as e:
                        logger.warning(f"Lỗi khi thiết lập GPU: {str(e)}")
            else:
                # Tắt GPU nếu chỉ định CPU
                tf.config.set_visible_devices([], 'GPU')
            
            # Tải model
            try:
                model = tf.keras.models.load_model(model_path)
            except Exception as e:
                logger.warning(f"Lỗi khi tải model với custom objects mặc định: {str(e)}")
                # Thử tải với custom objects
                model = tf.keras.models.load_model(model_path, compile=False)
                model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model Keras: {str(e)}")
            raise RuntimeError(f"Không thể tải model Keras: {str(e)}")
    
    @staticmethod
    def _create_compatible_tf_model(model_config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Tạo model TensorFlow tương thích với kiến trúc của model ban đầu
        
        Args:
            model_config: Cấu hình model (nếu có)
            
        Returns:
            Model: Model tương thích
        """
        import tensorflow as tf
        
        # Tạo model với kiến trúc mặc định nếu không có cấu hình
        if not model_config:
            max_length = 100
            vocab_size = 20000
            embedding_dim = 128
            lstm_units = 128
            num_classes = len(settings.MODEL_LABELS)
        else:
            # Lấy thông tin từ cấu hình
            max_length = model_config.get('max_length', 100)
            vocab_size = model_config.get('vocab_size', 20000)
            embedding_dim = model_config.get('embedding_dim', 128)
            lstm_units = model_config.get('lstm_units', 128)
            num_classes = model_config.get('num_classes', len(settings.MODEL_LABELS))
        
        # Tạo model với kiến trúc tương thích
        inputs = tf.keras.Input(shape=(max_length,))
        x = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length)(inputs)
        x = tf.keras.layers.LSTM(lstm_units)(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model
    
    @staticmethod
    def _apply_tf_weights(model, weights_dict):
        """
        Áp dụng weights từ safetensors vào model TensorFlow
        
        Args:
            model: Model TensorFlow
            weights_dict: Dictionary chứa tensor weights
        """
        import tensorflow as tf
        
        # Áp dụng weights cho từng layer
        for layer in model.layers:
            layer_name = layer.name
            weights = layer.get_weights()
            
            # Skip layer nếu không có weights
            if not weights:
                continue
                
            # Tìm tensor tương ứng cho mỗi weight
            new_weights = []
            for i, old_weight in enumerate(weights):
                # Thông thường, i=0 là kernel, i=1 là bias
                weight_type = "kernel" if i == 0 else "bias"
                
                # Các key name khả dĩ
                possible_keys = [
                    f"{layer_name}.{weight_type}",
                    f"{layer_name}/{weight_type}",
                    f"{layer_name}.weight" if i == 0 else f"{layer_name}.bias",
                    layer_name if i == 0 else f"{layer_name}_bias"
                ]
                
                # Tìm key trong weights_dict
                found = False
                for key in possible_keys:
                    if key in weights_dict:
                        tensor = weights_dict[key]
                        if tensor.shape == old_weight.shape:
                            new_weights.append(tensor)
                            found = True
                            break
                
                if not found:
                    # Nếu không tìm thấy, giữ nguyên weight cũ
                    logger.warning(f"Không tìm thấy weights cho {layer_name} (index {i})")
                    new_weights.append(old_weight)
            
            # Áp dụng weights mới
            if len(new_weights) == len(weights):
                try:
                    layer.set_weights(new_weights)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")
    
    @staticmethod
    def _create_pytorch_model(model_config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Tạo model PyTorch tương thích với kiến trúc của model ban đầu
        
        Args:
            model_config: Cấu hình model (nếu có)
            
        Returns:
            Model: Model tương thích
        """
        try:
            import torch
            import torch.nn as nn
            
            # Tạo model với kiến trúc mặc định nếu không có cấu hình
            if not model_config:
                max_length = 100
                vocab_size = 20000
                embedding_dim = 128
                lstm_units = 128
                num_classes = len(settings.MODEL_LABELS)
            else:
                # Lấy thông tin từ cấu hình
                max_length = model_config.get('max_length', 100)
                vocab_size = model_config.get('vocab_size', 20000)
                embedding_dim = model_config.get('embedding_dim', 128)
                lstm_units = model_config.get('lstm_units', 128)
                num_classes = model_config.get('num_classes', len(settings.MODEL_LABELS))
            
            # Tạo model PyTorch tương thích
            class LSTMClassifier(nn.Module):
                def __init__(self, vocab_size, embedding_dim, lstm_units, num_classes):
                    super(LSTMClassifier, self).__init__()
                    self.embedding = nn.Embedding(vocab_size, embedding_dim)
                    self.lstm = nn.LSTM(embedding_dim, lstm_units, batch_first=True)
                    self.fc1 = nn.Linear(lstm_units, 64)
                    self.relu = nn.ReLU()
                    self.dropout = nn.Dropout(0.2)
                    self.fc2 = nn.Linear(64, num_classes)
                    self.softmax = nn.Softmax(dim=1)
                
                def forward(self, x):
                    embedded = self.embedding(x)
                    lstm_out, _ = self.lstm(embedded)
                    # Lấy output của token cuối cùng
                    lstm_out = lstm_out[:, -1, :]
                    fc1_out = self.fc1(lstm_out)
                    relu_out = self.relu(fc1_out)
                    dropout_out = self.dropout(relu_out)
                    fc2_out = self.fc2(dropout_out)
                    output = self.softmax(fc2_out)
                    return output
            
            model = LSTMClassifier(vocab_size, embedding_dim, lstm_units, num_classes)
            return model
            
        except ImportError:
            logger.error("PyTorch không được cài đặt")
            raise
    
    @staticmethod
    def _pytorch_predict_wrapper(model, x):
        """
        Wrapper cho phương thức predict của PyTorch để tương thích với Keras
        
        Args:
            model: Model PyTorch
            x: Input data
            
        Returns:
            numpy.ndarray: Prediction
        """
        import torch
        
        # Chuyển x thành tensor nếu cần
        if not isinstance(x, torch.Tensor):
            # Kiểm tra nếu x là numpy array
            if isinstance(x, np.ndarray):
                x = torch.from_numpy(x).long()
            else:
                x = torch.tensor(x, dtype=torch.long)
        
        # Đảm bảo model ở chế độ eval
        model.eval()
        
        # Thực hiện inference với no_grad để tối ưu hóa
        with torch.no_grad():
            output = model(x)
        
        # Chuyển kết quả về numpy
        return output.cpu().numpy()