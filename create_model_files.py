import os
import json
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout

print("Creating model directory...")
os.makedirs("model", exist_ok=True)

print("Creating config.json...")
config = {
    "model_type": "lstm",
    "vocab_size": 20000,
    "embedding_dim": 128,
    "lstm_units": 128,
    "max_length": 100,
    "num_classes": 4,
    "dropout_rate": 0.2,
    "hidden_layer_size": 64,
    "labels": ["clean", "offensive", "hate", "spam"]
}
with open("model/config.json", 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print("Creating tokenizer...")
# Create a basic tokenizer with common Vietnamese words
common_words = [
    "xin chào", "cảm ơn", "không", "có", "tốt", "xấu", "thích", "ghét",
    "vui", "buồn", "giận dữ", "bình thường", "tuyệt vời", "tệ"
]
tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
tokenizer.fit_on_texts(common_words)
with open("model/tokenizer.pkl", 'wb') as f:
    pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

print("Creating model...")
# Create model
inputs = Input(shape=(100,), name='input')
x = Embedding(20000, 128, input_length=100, name='embedding')(inputs)
x = LSTM(128, name='lstm')(x)
x = Dense(64, activation='relu', name='dense')(x)
x = Dropout(0.2, name='dropout')(x)
outputs = Dense(4, activation='softmax', name='dense_1')(x)
model = Model(inputs=inputs, outputs=outputs, name='vietnamese_hate_speech_model')
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Saving model...")
model.save("model/converted_model.h5")

print("Creating .env file...")
with open(".env", 'w', encoding='utf-8') as f:
    f.write("MODEL_PATH=model/converted_model.h5\n")
    f.write("MODEL_VOCAB_PATH=model/tokenizer.pkl\n")
    f.write("MODEL_CONFIG_PATH=model/config.json\n")

print("Done! Files created successfully.") 