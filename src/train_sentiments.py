# @title ML de validación de sentimiento
import tensorflow as tf
import joblib
import numpy as np
import logging
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta absoluta al modelo
modelo_path = os.path.join(BASE_DIR, "..", "train1", "sentiemiento_tensorflow.h5")
modelo_path = os.path.normpath(modelo_path)


# Ruta absoluta al modelo
label_encoder = os.path.join(BASE_DIR, "..", "train1", "label_encoder_sentimientos.pkl")
label_encoder = os.path.normpath(label_encoder)


# Debug print
print("Cargando modelo desde:", )



# Modelo
model_sent = tf.keras.models.load_model(modelo_path)
# LabelEncoder
le_sent = joblib.load(label_encoder)


# Volver a definir el modelo de embeddings
from langchain.embeddings import HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Función de predicción
def predict_sentiment(text):
    vec = embedding_model.embed_documents([text])
    vec = np.array(vec, dtype=np.float32)
    probs = model_sent.predict(vec)
    idx = np.argmax(probs, axis=1)[0]
    sentiment = le_sent.inverse_transform([idx])[0]
    confidence = float(probs[0, idx])
    return sentiment, confidence

logging.getLogger('absl').setLevel(logging.ERROR)
