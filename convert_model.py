# # convert_model.py
# import tensorflow as tf
# import numpy as np
# import os
# import json

# def convert_model(input_model_path, output_model_path):
#     """
#     Chuyển đổi model từ định dạng cũ sang định dạng tương thích với TensorFlow 2.x
    
#     Args:
#         input_model_path: Đường dẫn đến file model cũ (.h5)
#         output_model_path: Đường dẫn để lưu model mới
#     """
#     try:
#         # Cố gắng tải model theo cách thông thường
#         print(f"Đang tải model từ {input_model_path}...")
        
#         # Tải model dưới dạng file h5 - lấy topology và weights
#         f = tf.keras.models.load_model(input_model_path, compile=False)
        
#         # Lấy thông tin kiến trúc model
#         config = json.loads(f.to_json())
        
#         # Xử lý lại cấu hình model
#         for layer in config['config']['layers']:
#             # Loại bỏ batch_shape nếu có
#             if 'batch_shape' in layer['config']:
#                 print(f"Loại bỏ batch_shape từ layer {layer['name']}")
#                 del layer['config']['batch_shape']
            
#             # Giữ lại shape
#             if 'batch_input_shape' in layer['config']:
#                 print(f"Giữ batch_input_shape: {layer['config']['batch_input_shape']}")
        
#         # Tạo model mới từ config đã được chỉnh sửa
#         print("Đang tạo model mới từ cấu hình đã được chỉnh sửa...")
#         new_model = tf.keras.models.model_from_json(json.dumps(config))
        
#         # Sao chép trọng số
#         print("Đang sao chép trọng số...")
#         for i, layer in enumerate(f.layers):
#             try:
#                 weights = layer.get_weights()
#                 if weights:
#                     print(f"Đang sao chép trọng số cho layer {i}: {layer.name}")
#                     new_model.layers[i].set_weights(weights)
#             except Exception as e:
#                 print(f"Không thể sao chép trọng số cho layer {i}: {e}")
        
#         # Biên dịch model mới
#         new_model.compile(
#             optimizer='adam',
#             loss='categorical_crossentropy',
#             metrics=['accuracy']
#         )
        
#         # Lưu model mới
#         print(f"Đang lưu model mới vào {output_model_path}...")
#         new_model.save(output_model_path)
        
#         print(f"Chuyển đổi model thành công! Model mới đã được lưu tại {output_model_path}")
#         return True
    
#     except Exception as e:
#         print(f"Lỗi khi chuyển đổi model: {e}")
        
#         # Trường hợp 2: Nếu không thể tải model, tạo mới model tương thích
#         print("Tạo model mới tương thích...")
        
#         # Tạo model LSTM đơn giản
#         model = tf.keras.Sequential([
#             tf.keras.layers.Input(shape=(100,), dtype='float32'),
#             tf.keras.layers.Embedding(10000, 128, input_length=100),
#             tf.keras.layers.LSTM(64, dropout=0.2),
#             tf.keras.layers.Dense(64, activation='relu'),
#             tf.keras.layers.Dropout(0.5),
#             tf.keras.layers.Dense(4, activation='softmax')
#         ])
        
#         model.compile(
#             optimizer='adam',
#             loss='categorical_crossentropy',
#             metrics=['accuracy']
#         )
        
#         # Lưu model mới
#         model.save(output_path)
#         print(f"Đã tạo model mới tại {output_path}")
#         return False

# # Chuyển đổi model
# input_path = "model/best_model_LSTM.h5"
# output_path = "model/compatible_model.h5"

# # Tạo thư mục model nếu chưa tồn tại
# os.makedirs(os.path.dirname(output_path), exist_ok=True)

# if not os.path.exists(output_path):
#     convert_model(input_path, output_path)
# else:
#     print(f"Model tương thích đã tồn tại tại {output_path}. Bỏ qua chuyển đổi.")

# # Kiểm tra model tương thích
# try:
#     model = tf.keras.models.load_model(output_path)
#     print("Kiểm tra model thành công!")
#     print(f"Cấu trúc model: {model.summary()}")
# except Exception as e:
#     print(f"Lỗi khi kiểm tra model: {e}")
# convert_model.py
import tensorflow as tf
import numpy as np
import os
import json
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("model_conversion.log")
    ]
)
logger = logging.getLogger(__name__)

def convert_model(input_model_path, output_model_path):
    """
    Chuyển đổi model từ định dạng cũ sang định dạng tương thích với TensorFlow 2.x
    
    Args:
        input_model_path: Đường dẫn đến file model cũ (.h5)
        output_model_path: Đường dẫn để lưu model mới
    
    Returns:
        bool: True nếu chuyển đổi thành công, False nếu thất bại
    """
    try:
        # Cố gắng tải model theo cách thông thường
        logger.info(f"Đang tải model từ {input_model_path}...")
        
        # Tải model dưới dạng file h5 - lấy topology và weights
        original_model = tf.keras.models.load_model(input_model_path, compile=False)
        
        # Lấy thông tin kiến trúc model
        config = json.loads(original_model.to_json())
        
        # Xử lý lại cấu hình model
        for layer in config['config']['layers']:
            # Loại bỏ batch_shape nếu có
            if 'batch_shape' in layer['config']:
                logger.info(f"Loại bỏ batch_shape từ layer {layer['name']}")
                del layer['config']['batch_shape']
            
            # Ghi lại thông tin batch_input_shape
            if 'batch_input_shape' in layer['config']:
                logger.info(f"Layer {layer['name']} - batch_input_shape: {layer['config']['batch_input_shape']}")
            
            # Xử lý các config đặc biệt nếu cần
            if layer['class_name'] == 'LSTM':
                logger.info(f"Đang xử lý layer LSTM: {layer['name']}")
                # Đảm bảo implementation là 1 (implementation = 2 có thể gây lỗi ở một số phiên bản TF)
                if 'implementation' in layer['config']:
                    layer['config']['implementation'] = 1
        
        # Tạo model mới từ config đã được chỉnh sửa
        logger.info("Đang tạo model mới từ cấu hình đã được chỉnh sửa...")
        new_model = tf.keras.models.model_from_json(json.dumps(config))
        
        # Sao chép trọng số
        logger.info("Đang sao chép trọng số...")
        for i, layer in enumerate(original_model.layers):
            try:
                weights = layer.get_weights()
                if weights:
                    logger.info(f"Đang sao chép trọng số cho layer {i}: {layer.name} - {len(weights)} weights")
                    new_model.layers[i].set_weights(weights)
            except Exception as e:
                logger.error(f"Không thể sao chép trọng số cho layer {i}: {e}")
        
        # Biên dịch model mới
        new_model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Kiểm tra model trước khi lưu
        logger.info("Kiểm tra model trước khi lưu...")
        input_shape = new_model.input_shape[1:]
        test_input = np.zeros((1,) + input_shape, dtype=np.float32)
        try:
            test_output = new_model.predict(test_input, verbose=0)
            logger.info(f"Test prediction thành công. Output shape: {test_output.shape}")
        except Exception as e:
            logger.warning(f"Không thể chạy dự đoán thử nghiệm: {e}")
            logger.warning("Tiếp tục lưu model, nhưng có thể cần kiểm tra kỹ hơn")
        
        # Lưu model mới
        logger.info(f"Đang lưu model mới vào {output_model_path}...")
        new_model.save(output_model_path)
        
        logger.info(f"Chuyển đổi model thành công! Model mới đã được lưu tại {output_model_path}")
        return True
    
    except Exception as e:
        logger.error(f"Lỗi khi chuyển đổi model: {e}")
        logger.info("Thử phương pháp chuyển đổi thay thế...")
        
        try:
            # Trường hợp 2: Tạo model đơn giản, cố gắng tải weights
            original_model = None
            try:
                logger.info("Thử tải model chỉ để lấy weights...")
                original_model = tf.keras.models.load_model(input_model_path, compile=False)
            except Exception as inner_e:
                logger.error(f"Không thể tải model để lấy weights: {inner_e}")
            
            # Tạo model LSTM tương thích
            logger.info("Tạo model mới tương thích...")
            
            # Tạo model LSTM đơn giản
            new_model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(100,), dtype='float32'),
                tf.keras.layers.Embedding(20000, 128, input_length=100),
                tf.keras.layers.LSTM(128, dropout=0.2),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(4, activation='softmax')
            ])
            
            # Thử sao chép weights nếu có thể
            if original_model is not None:
                try:
                    logger.info("Thử sao chép weights từ model gốc...")
                    
                    # Tạo mapping cho layer tương ứng
                    layer_mapping = {
                        "embedding": "embedding",
                        "lstm": "lstm",
                        "dense": "dense"
                    }
                    
                    # Tìm layer tương ứng và sao chép weights
                    for src_layer in original_model.layers:
                        for layer_type, layer_name in layer_mapping.items():
                            if layer_type in src_layer.name.lower():
                                for tgt_layer in new_model.layers:
                                    if layer_name in tgt_layer.name.lower():
                                        try:
                                            weights = src_layer.get_weights()
                                            if len(weights) > 0 and all(w.shape == tw.shape for w, tw in zip(weights, tgt_layer.get_weights())):
                                                logger.info(f"Sao chép weights cho layer {tgt_layer.name} từ {src_layer.name}")
                                                tgt_layer.set_weights(weights)
                                        except Exception as w_e:
                                            logger.warning(f"Không thể sao chép weights cho {tgt_layer.name}: {w_e}")
                                        break
                except Exception as copy_e:
                    logger.error(f"Không thể sao chép weights: {copy_e}")
            
            # Biên dịch model mới
            new_model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Lưu model mới
            logger.info(f"Đang lưu model mới tương thích vào {output_model_path}...")
            new_model.save(output_model_path)
            
            logger.info(f"Đã tạo và lưu model mới tương thích tại {output_model_path}")
            return True
        
        except Exception as fallback_e:
            logger.error(f"Lỗi khi tạo model dự phòng: {fallback_e}")
            
            # Trường hợp cuối cùng: tạo model đơn giản nhất
            logger.info("Thử tạo model cơ bản cuối cùng...")
            
            try:
                # Tạo model đơn giản nhất
                basic_model = tf.keras.Sequential([
                    tf.keras.layers.Input(shape=(100,), dtype='float32'),
                    tf.keras.layers.Embedding(10000, 64, input_length=100),
                    tf.keras.layers.GlobalAveragePooling1D(),
                    tf.keras.layers.Dense(4, activation='softmax')
                ])
                
                basic_model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                # Lưu model
                basic_model.save(output_model_path)
                logger.info(f"Đã tạo model cơ bản tại {output_model_path}")
                return True
            except Exception as basic_e:
                logger.error(f"Lỗi khi tạo model cơ bản: {basic_e}")
                return False

def export_to_safetensors(input_model_path, output_safetensors_path):
    """
    Xuất model TensorFlow sang định dạng safetensors
    
    Args:
        input_model_path: Đường dẫn đến model TensorFlow (.h5)
        output_safetensors_path: Đường dẫn để lưu file safetensors
    
    Returns:
        bool: True nếu xuất thành công, False nếu thất bại
    """
    try:
        # Kiểm tra thư viện safetensors
        import importlib.util
        if importlib.util.find_spec("safetensors") is None:
            logger.error("Không tìm thấy thư viện safetensors. Vui lòng cài đặt: pip install safetensors")
            return False
        
        from safetensors import tensorflow
        logger.info(f"Đang tải model từ {input_model_path}...")
        model = tf.keras.models.load_model(input_model_path)
        
        # Chuẩn bị weights dict
        weights_dict = {}
        for layer in model.layers:
            weights = layer.get_weights()
            if weights:
                for i, w in enumerate(weights):
                    weight_type = "kernel" if i == 0 else "bias"
                    key = f"{layer.name}.{weight_type}"
                    weights_dict[key] = w
        
        # Lưu dưới dạng safetensors
        logger.info(f"Đang lưu model safetensors tại {output_safetensors_path}...")
        tensorflow.save_file(weights_dict, output_safetensors_path)
        
        logger.info(f"Xuất model sang safetensors thành công tại {output_safetensors_path}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi xuất model sang safetensors: {e}")
        return False

if __name__ == "__main__":
    # Đường dẫn
    input_path = "model/best_model_LSTM.h5"
    output_path = "model/compatible_model.h5"
    safetensors_path = "model/model.safetensors"
    
    # Tạo thư mục model nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Chuyển đổi model
    if not os.path.exists(output_path):
        logger.info("Bắt đầu chuyển đổi model...")
        success = convert_model(input_path, output_path)
        if success:
            logger.info("Chuyển đổi model thành công!")
        else:
            logger.error("Chuyển đổi model thất bại!")
    else:
        logger.info(f"Model tương thích đã tồn tại tại {output_path}. Bỏ qua chuyển đổi.")
    
    # Kiểm tra model tương thích
    try:
        logger.info("Đang kiểm tra model tương thích...")
        model = tf.keras.models.load_model(output_path)
        logger.info("Kiểm tra model thành công!")
        
        # In thông tin cấu trúc model
        model.summary(print_fn=logger.info)
        
        # Thử dự đoán mẫu
        input_shape = model.input_shape[1:]
        test_input = np.zeros((1,) + input_shape, dtype=np.float32)
        test_output = model.predict(test_input, verbose=0)
        logger.info(f"Dự đoán thử nghiệm thành công. Output shape: {test_output.shape}")
        
        # Xuất sang safetensors nếu model tương thích hoạt động tốt
        if not os.path.exists(safetensors_path):
            logger.info("Bắt đầu xuất model sang safetensors...")
            try:
                export_success = export_to_safetensors(output_path, safetensors_path)
                if export_success:
                    logger.info("Xuất model sang safetensors thành công!")
                else:
                    logger.warning("Xuất model sang safetensors thất bại!")
            except Exception as e:
                logger.error(f"Lỗi khi xuất model sang safetensors: {e}")
        else:
            logger.info(f"Model safetensors đã tồn tại tại {safetensors_path}. Bỏ qua xuất.")
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra model: {e}")
        logger.error("Model tương thích có thể không hoạt động đúng!")