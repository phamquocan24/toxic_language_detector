"""
Model Adapter - Lớp trung gian xử lý model safetensors với cải tiến
"""
import os
import tensorflow as tf
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

class ModelAdapter:
    """Adapter class để tải model từ định dạng .safetensors"""
    
    @staticmethod
    def load_model(model_path, config_path=None):
        """
        Tải model từ đường dẫn, tự động phát hiện định dạng
        
        Args:
            model_path: Đường dẫn đến file model
            config_path: Đường dẫn đến file config (tùy chọn)
            
        Returns:
            tf.keras.Model: Model đã tải
        """
        try:
            if model_path.endswith('.safetensors'):
                logger.info(f"Tải model từ safetensors: {model_path}")
                return ModelAdapter._load_from_safetensors(model_path, config_path)
            else:
                # Xử lý an toàn hơn cho files .h5
                logger.info(f"Tải model từ định dạng thông thường: {model_path}")
                return ModelAdapter._load_h5_safely(model_path)
        except Exception as e:
            logger.error(f"Lỗi khi tải model từ {model_path}: {str(e)}")
            logger.info("Fallback về model dự phòng")
            return ModelAdapter._create_fallback_model()
    
    @staticmethod
    def _load_h5_safely(model_path):
        """
        Tải model h5 với xử lý lỗi tốt hơn
        
        Args:
            model_path: Đường dẫn đến file model h5
            
        Returns:
            tf.keras.Model: Model đã tải
        """
        try:
            # Thử tải model thông thường
            with tf.keras.utils.custom_object_scope({}):
                model = tf.keras.models.load_model(model_path, compile=False)
                
                # Biên dịch model
                model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                # Kiểm tra model hoạt động
                dummy_input = np.zeros((1,) + tuple(model.input_shape[1:]))
                _ = model.predict(dummy_input, verbose=0)
                
                return model
        except Exception as e:
            logger.warning(f"Không thể tải model theo cách thông thường: {e}")
            
            try:
                # Thử sửa lỗi cấu trúc trước khi tải
                logger.info("Thử tải từ config đã sửa đổi")
                
                # Tạo một model tạm thời để lấy config
                temp_model = tf.keras.models.load_model(model_path, compile=False)
                config = temp_model.get_config()
                
                # Sửa đổi config để tránh các tham số gây lỗi
                if isinstance(config, dict) and 'layers' in config:
                    layers = config['layers']
                    for layer in layers:
                        if 'config' in layer:
                            if 'batch_shape' in layer['config']:
                                del layer['config']['batch_shape']
                            if 'sparse' in layer['config']:
                                del layer['config']['sparse']
                
                # Tạo model mới từ config đã sửa
                if hasattr(temp_model, 'from_config'):
                    model = temp_model.__class__.from_config(config)
                else:
                    model = tf.keras.Sequential.from_config(config)
                
                # Cố gắng sao chép weights
                model.load_weights(model_path)
                
                # Biên dịch model
                model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                return model
            except Exception as inner_e:
                logger.error(f"Không thể sửa lỗi cấu trúc model: {inner_e}")
                raise RuntimeError(f"Không thể tải model h5: {str(e)} -> {str(inner_e)}")
    
    @staticmethod
    def _load_from_safetensors(model_path, config_path=None):
        """
        Tải model từ định dạng .safetensors
        
        Args:
            model_path: Đường dẫn đến file model .safetensors
            config_path: Đường dẫn đến file config (tùy chọn)
            
        Returns:
            tf.keras.Model: Model đã tải
        """
        try:
            # Kiểm tra safetensors module
            try:
                from safetensors.tensorflow import load_file
            except ImportError:
                logger.error("Module safetensors không được cài đặt")
                logger.info("Thử cài đặt module safetensors")
                
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "safetensors"])
                
                from safetensors.tensorflow import load_file
            
            # Đọc config nếu có
            if config_path and os.path.exists(config_path):
                logger.info(f"Đọc config từ: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                model = ModelAdapter._create_model_from_config(config_data)
            else:
                logger.info("Không tìm thấy config, tạo model với kiến trúc mặc định")
                model = ModelAdapter._create_compatible_model()
            
            # Tải weights
            weights_dict = load_file(model_path)
            logger.info(f"Đã tải weights, số lượng tensor: {len(weights_dict)}")
            
            # Log thông tin weights để debug
            if logger.isEnabledFor(logging.DEBUG):
                for key, value in weights_dict.items():
                    logger.debug(f"Weight: {key}, shape: {value.shape}")
            
            # Áp dụng weights với log chi tiết
            ModelAdapter._apply_weights(model, weights_dict)
            
            # Compile model
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Kiểm tra model hoạt động
            input_shape = model.input_shape[1:]
            dummy_input = np.zeros((1,) + input_shape)
            result = model.predict(dummy_input, verbose=0)
            logger.info(f"Model safetensors đã tải thành công, output shape: {result.shape}")
            
            return model
            
        except Exception as e:
            logger.error(f"Lỗi khi tải model safetensors: {str(e)}")
            
            # Thử h5 backup nếu có
            h5_path = model_path.replace('.safetensors', '.h5')
            if os.path.exists(h5_path):
                logger.info(f"Fallback sang model .h5: {h5_path}")
                return ModelAdapter._load_h5_safely(h5_path)
            
            logger.warning("Không tìm thấy model backup h5, tạo model dự phòng")
            return ModelAdapter._create_fallback_model()
    
    @staticmethod
    def _create_model_from_config(config):
        """
        Tạo model từ config JSON
        
        Args:
            config: Dữ liệu config của model
            
        Returns:
            tf.keras.Model: Model được tạo
        """
        try:
            # Tạo model từ config
            if isinstance(config, dict):
                if 'config' in config:
                    # Xử lý config phiên bản mới
                    # Sửa config nếu cần
                    if 'layers' in config['config']:
                        for layer in config['config']['layers']:
                            if 'batch_shape' in layer['config']:
                                del layer['config']['batch_shape']
                            if 'sparse' in layer['config']:
                                del layer['config']['sparse']
                    
                    # Tạo model từ config
                    model = tf.keras.models.model_from_json(json.dumps(config))
                    return model
            
            # Nếu định dạng không phù hợp, tạo model mặc định
            logger.warning("Config không phù hợp, sử dụng model mặc định")
            return ModelAdapter._create_compatible_model()
        except Exception as e:
            logger.error(f"Lỗi khi tạo model từ config: {str(e)}")
            return ModelAdapter._create_compatible_model()
    
    @staticmethod
    def _create_compatible_model():
        """
        Tạo model tương thích với kiến trúc của model ban đầu
        
        Returns:
            tf.keras.Model: Model tương thích
        """
        # Tạo model với kiến trúc giống model ban đầu
        inputs = tf.keras.Input(shape=(100,), name='input_layer')
        x = tf.keras.layers.Embedding(input_dim=20000, output_dim=128, name='embedding_layer')(inputs)
        x = tf.keras.layers.LSTM(128, name='lstm_layer')(x)
        x = tf.keras.layers.Dense(64, activation='relu', name='dense_layer')(x)
        x = tf.keras.layers.Dropout(0.2, name='dropout_layer')(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax', name='output_layer')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model
    
    @staticmethod
    def _create_fallback_model():
        """
        Tạo model dự phòng đơn giản khi không thể tải model chính
        """
        logger.warning("Tạo model dự phòng đơn giản")
        
        # Tạo model đơn giản
        inputs = tf.keras.Input(shape=(10000,), name='input_features')
        x = tf.keras.layers.Dense(128, activation='relu', name='dense_1')(inputs)
        x = tf.keras.layers.Dropout(0.3, name='dropout')(x)
        outputs = tf.keras.layers.Dense(4, activation='softmax', name='output')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    @staticmethod
    def _apply_weights(model, weights_dict):
        """
        Áp dụng weights từ safetensors vào model TensorFlow
        
        Args:
            model: Model TensorFlow
            weights_dict: Dictionary chứa tensor weights
        """
        # Tạo mapping từ tên layers
        layer_dict = {layer.name: layer for layer in model.layers}
        
        # Áp dụng weights cho từng layer
        for layer_name, layer in layer_dict.items():
            weights = layer.get_weights()
            
            # Skip layer nếu không có weights
            if not weights:
                logger.debug(f"Layer {layer_name} không có weights, bỏ qua")
                continue
                
            # Tìm tensor tương ứng cho mỗi weight
            new_weights = []
            weights_updated = False
            
            for i, old_weight in enumerate(weights):
                # Thông thường, i=0 là kernel, i=1 là bias
                weight_type = "kernel" if i == 0 else "bias"
                
                # Tạo danh sách các key name khả dĩ từ nhiều patterns khác nhau
                possible_keys = [
                    # Các dạng thông thường
                    f"{layer_name}.{weight_type}",
                    f"{layer_name}/{weight_type}",
                    f"{layer_name}.weight" if i == 0 else f"{layer_name}.bias",
                    f"{layer_name}_weight" if i == 0 else f"{layer_name}_bias",
                    layer_name if i == 0 else f"{layer_name}_bias",
                    
                    # Thêm các dạng phức tạp hơn
                    f"{layer_name}.{i}",
                    f"{layer_name}/weights/{i}",
                    f"{layer_name}/weights/{weight_type}",
                    f"layer.{layer_name}.{weight_type}"
                ]
                
                # Thêm các dạng đơn giản nếu là LSTM
                if isinstance(layer, tf.keras.layers.LSTM):
                    lstm_keys = [
                        f"{layer_name}.kernel",
                        f"{layer_name}.recurrent_kernel",
                        f"{layer_name}.bias"
                    ]
                    possible_keys.extend(lstm_keys)
                
                # Tìm key trong weights_dict
                found_key = None
                for key in possible_keys:
                    if key in weights_dict:
                        tensor = weights_dict[key]
                        if tensor.shape == old_weight.shape:
                            logger.debug(f"Tìm thấy weight khớp cho {layer_name}: {key}, shape: {tensor.shape}")
                            new_weights.append(tensor)
                            found_key = key
                            weights_updated = True
                            break
                
                if found_key is None:
                    # Không tìm thấy exact match, thử tìm tensor có thể reshape
                    for key, tensor in weights_dict.items():
                        if layer_name in key and tensor.size == old_weight.size:
                            try:
                                reshaped_tensor = np.reshape(tensor, old_weight.shape)
                                logger.info(f"Reshape tensor từ {key} cho {layer_name}, từ {tensor.shape} thành {old_weight.shape}")
                                new_weights.append(reshaped_tensor)
                                weights_updated = True
                                break
                            except Exception as e:
                                logger.debug(f"Không thể reshape {key}: {e}")
                    else:
                        # Nếu không tìm được tensor nào phù hợp, giữ nguyên weight cũ
                        logger.debug(f"Không tìm thấy weight cho {layer_name}.{weight_type}, giữ nguyên weight cũ")
                        new_weights.append(old_weight)
            
            # Áp dụng weights mới nếu đã tìm thấy
            if len(new_weights) == len(weights):
                try:
                    if weights_updated:
                        logger.info(f"Áp dụng weights mới cho layer {layer_name}")
                        layer.set_weights(new_weights)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng weights cho layer {layer_name}: {str(e)}")
            else:
                logger.warning(f"Số lượng weights không khớp cho layer {layer_name}: {len(new_weights)} vs {len(weights)}")
    
    @staticmethod
    def save_model(model, save_path, save_format='h5'):
        """
        Lưu model với xử lý lỗi
        
        Args:
            model: Model cần lưu
            save_path: Đường dẫn lưu model
            save_format: Định dạng lưu (h5, tf, keras)
        """
        try:
            logger.info(f"Lưu model vào {save_path} với định dạng {save_format}")
            
            # Tạo thư mục chứa nếu chưa tồn tại
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            
            # Lưu model
            model.save(save_path, save_format=save_format)
            logger.info(f"Đã lưu model thành công")
            
            # Kiểm tra model đã lưu
            try:
                logger.info(f"Kiểm tra model đã lưu")
                loaded_model = tf.keras.models.load_model(save_path)
                logger.info(f"Tải lại model thành công")
                return True
            except Exception as e:
                logger.warning(f"Không thể tải lại model đã lưu: {e}")
                return False
        except Exception as e:
            logger.error(f"Lỗi khi lưu model: {str(e)}")
            return False
    
    @staticmethod
    def save_as_safetensors(model, save_path):
        """
        Lưu model sang định dạng safetensors
        
        Args:
            model: Model cần lưu
            save_path: Đường dẫn lưu model
        """
        try:
            from safetensors import safe_open
            from safetensors.tensorflow import save_file
            
            logger.info(f"Lưu model sang định dạng safetensors: {save_path}")
            
            # Tạo thư mục chứa nếu chưa tồn tại
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            
            # Tạo dict chứa tất cả weights
            weights_dict = {}
            
            for layer in model.layers:
                weights = layer.get_weights()
                if not weights:
                    continue
                
                for i, weight in enumerate(weights):
                    weight_type = "kernel" if i == 0 else "bias"
                    key = f"{layer.name}.{weight_type}"
                    weights_dict[key] = weight
            
            # Lưu weights vào file safetensors
            save_file(weights_dict, save_path)
            
            # Lưu config riêng
            config_path = save_path.replace('.safetensors', '.config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(json.loads(model.to_json()), f, indent=2)
            
            logger.info(f"Đã lưu model vào {save_path} và config vào {config_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu model sang safetensors: {str(e)}")
            return False
    
    @staticmethod
    def convert_h5_to_safetensors(h5_path, safetensors_path=None):
        """
        Chuyển đổi model từ h5 sang safetensors
        
        Args:
            h5_path: Đường dẫn file h5
            safetensors_path: Đường dẫn file safetensors đầu ra (tùy chọn)
        """
        if safetensors_path is None:
            safetensors_path = h5_path.replace('.h5', '.safetensors')
        
        try:
            # Tải model từ h5
            model = ModelAdapter._load_h5_safely(h5_path)
            
            # Lưu sang safetensors
            success = ModelAdapter.save_as_safetensors(model, safetensors_path)
            
            if success:
                logger.info(f"Đã chuyển đổi thành công từ {h5_path} sang {safetensors_path}")
                return safetensors_path
            else:
                logger.error("Không thể chuyển đổi model")
                return None
        except Exception as e:
            logger.error(f"Lỗi khi chuyển đổi model: {str(e)}")
            return None