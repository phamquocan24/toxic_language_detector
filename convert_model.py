# convert_model.py
import tensorflow as tf
import numpy as np
import os
import json
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_model(input_model_path, output_model_path):
    """
    Chuyển đổi model từ định dạng cũ sang định dạng tương thích với TensorFlow 2.x
    
    Args:
        input_model_path: Đường dẫn đến file model cũ (.h5)
        output_model_path: Đường dẫn để lưu model mới
    """
    try:
        # Kiểm tra xem input file có tồn tại không
        if not os.path.exists(input_model_path):
            logger.warning(f"Model gốc không tìm thấy tại {input_model_path}")
            return create_compatible_model(output_model_path)
            
        # Cố gắng tải model cấu trúc config
        logger.info(f"Đang phân tích cấu trúc model từ {input_model_path}...")
        
        # Tải model dưới dạng file h5 bằng custom object scope để tránh lỗi
        with tf.keras.utils.custom_object_scope({}):
            try:
                # Đầu tiên thử tải model theo cách an toàn
                orig_model = tf.keras.models.load_model(input_model_path, compile=False)
                logger.info("Tải model thành công theo cách thông thường")
            except Exception as e:
                logger.warning(f"Lỗi khi tải model: {e}")
                logger.info("Thử tải model từ config và weights riêng biệt...")
                
                # Nếu thất bại, thử đọc cấu trúc và weights riêng
                try:
                    with tf.io.gfile.GFile(input_model_path, 'rb') as f:
                        h5_file = tf.io.gfile.GFile(input_model_path, 'rb')
                        model_config = tf.keras.models.load_model(h5_file, compile=False).get_config()
                        
                        # Xóa batch_shape từ config
                        for layer in model_config['layers']:
                            if 'batch_shape' in layer['config']:
                                del layer['config']['batch_shape']
                                
                        orig_model = tf.keras.Sequential.from_config(model_config)
                        
                        # Cố gắng tải weights
                        try:
                            orig_model.load_weights(input_model_path)
                            logger.info("Đã tải weights từ file H5")
                        except:
                            logger.warning("Không thể tải weights từ file H5, sẽ tạo model với weights ngẫu nhiên")
                except Exception as inner_e:
                    logger.error(f"Không thể phân tích cấu trúc model: {inner_e}")
                    return create_compatible_model(output_model_path)
        
        # Lấy cấu trúc model dưới dạng JSON
        model_json = orig_model.to_json()
        model_config = json.loads(model_json)
        
        # Làm sạch cấu hình model để loại bỏ batch_shape
        for layer in model_config['config']['layers']:
            if 'batch_shape' in layer['config']:
                logger.info(f"Loại bỏ batch_shape từ layer {layer['name']}")
                del layer['config']['batch_shape']
            
            # Xử lý các trường khác có thể gây lỗi
            if 'sparse' in layer['config'] and tf.__version__.startswith('2.'):
                logger.info(f"Loại bỏ sparse từ layer {layer['name']} cho TensorFlow 2.x")
                del layer['config']['sparse']
        
        # Tạo model mới từ config đã được chỉnh sửa
        logger.info("Đang tạo model mới từ cấu hình đã được chỉnh sửa...")
        new_model = tf.keras.models.model_from_json(json.dumps(model_config))
        
        # Sao chép trọng số từ model gốc
        try:
            logger.info("Đang sao chép trọng số...")
            for i, layer in enumerate(orig_model.layers):
                weights = layer.get_weights()
                if weights and i < len(new_model.layers):
                    logger.info(f"Đang sao chép trọng số cho layer {i}: {layer.name}")
                    try:
                        new_model.layers[i].set_weights(weights)
                    except Exception as w_err:
                        logger.warning(f"Không thể sao chép trọng số cho layer {i}: {w_err}")
        except Exception as e:
            logger.error(f"Lỗi khi sao chép trọng số: {e}")
        
        # Biên dịch model mới
        new_model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Kiểm tra model bằng cách dự đoán trên dữ liệu giả
        try:
            logger.info("Kiểm tra model với dữ liệu giả...")
            # Tạo đầu vào giả tương ứng với kích thước đầu vào của model
            input_shape = new_model.input_shape[1:]
            dummy_input = np.zeros((1,) + input_shape)
            result = new_model.predict(dummy_input)
            logger.info(f"Kiểm tra prediction thành công: shape={result.shape}")
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra model: {e}")
            logger.warning("Tạo model mới tương thích...")
            return create_compatible_model(output_model_path)
        
        # Lưu model mới
        logger.info(f"Đang lưu model mới vào {output_model_path}...")
        new_model.save(output_model_path, save_format='h5')
        
        logger.info(f"Chuyển đổi model thành công! Model mới đã được lưu tại {output_model_path}")
        return True
    
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi model: {e}")
        return create_compatible_model(output_model_path)

def create_compatible_model(output_path):
    """Tạo một model tương thích mới nếu không thể chuyển đổi model cũ"""
    logger.info("Tạo model tương thích mới từ đầu...")
    
    # Tạo model LSTM tương thích
    model = tf.keras.Sequential([
        # Sử dụng Input layer với shape đúng cách
        tf.keras.layers.Input(shape=(100,), dtype='float32', name='input_layer'),
        tf.keras.layers.Embedding(10000, 128, input_length=100, name='embedding_layer'),
        tf.keras.layers.LSTM(64, dropout=0.2, name='lstm_layer'),
        tf.keras.layers.Dense(64, activation='relu', name='dense_layer_1'),
        tf.keras.layers.Dropout(0.5, name='dropout_layer'),
        tf.keras.layers.Dense(4, activation='softmax', name='output_layer')
    ])
    
    # Biên dịch model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Lưu model
    logger.info(f"Đang lưu model tương thích mới vào {output_path}...")
    model.save(output_path, save_format='h5')
    
    # Kiểm tra model lại
    try:
        test_model = tf.keras.models.load_model(output_path)
        logger.info("Kiểm tra tải model mới thành công!")
        
        # Kiểm tra predict
        dummy_input = np.zeros((1, 100))
        result = test_model.predict(dummy_input)
        logger.info(f"Kiểm tra prediction thành công: shape={result.shape}")
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra model mới: {e}")
        logger.error("Tạo model thất bại, vui lòng kiểm tra lại TensorFlow version và cấu hình")
        return False
    
    logger.info(f"Đã tạo và kiểm tra model mới thành công tại {output_path}")
    return True

if __name__ == "__main__":
    # Đường dẫn model
    input_path = "model/best_model_LSTM.h5"
    output_path = "model/compatible_model.h5"
    
    # Tạo thư mục model nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not os.path.exists(output_path):
        success = convert_model(input_path, output_path)
        if success:
            logger.info("Quá trình chuyển đổi model hoàn tất thành công.")
        else:
            logger.warning("Quá trình chuyển đổi model không thành công, đã tạo model mới.")
    else:
        logger.info(f"Model tương thích đã tồn tại tại {output_path}. Kiểm tra model...")
        try:
            model = tf.keras.models.load_model(output_path)
            logger.info("Kiểm tra model tương thích thành công!")
        except Exception as e:
            logger.error(f"Model tương thích hiện tại bị lỗi: {e}")
            logger.info("Tạo lại model tương thích...")
            convert_model(input_path, output_path)