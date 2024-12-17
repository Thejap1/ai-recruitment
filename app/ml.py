import joblib
import os
import re
import tensorflow as tf
import numpy as np

# Load the trained Naive Bayes and TensorFlow models
def load_ml_model():
    # Paths to the saved models and vectorizer
    nb_model_path = 'resume_classifier_nb.pkl'
    nn_model_path = 'resume_classifier_nn.h5'
    tfidf_path = 'tfidf_vectorizer.pkl'
    label_encoder_path = 'label_encoder.pkl'

    # Load Naive Bayes model
    if not os.path.exists(nb_model_path):
        raise FileNotFoundError(f"Naive Bayes model file {nb_model_path} not found.")
    nb_model = joblib.load(nb_model_path)

    # Load TensorFlow neural network model
    if not os.path.exists(nn_model_path):
        raise FileNotFoundError(f"TensorFlow model file {nn_model_path} not found.")
    nn_model = tf.keras.models.load_model(nn_model_path)

    # Load TF-IDF vectorizer
    if not os.path.exists(tfidf_path):
        raise FileNotFoundError(f"TF-IDF vectorizer file {tfidf_path} not found.")
    tfidf = joblib.load(tfidf_path)

    # Load label encoder
    if not os.path.exists(label_encoder_path):
        raise FileNotFoundError(f"Label encoder file {label_encoder_path} not found.")
    label_encoder = joblib.load(label_encoder_path)

    return nb_model, nn_model, tfidf, label_encoder

# Preprocess the resume text
def preprocess_resume(filepath):
    # Convert resume file content to text
    with open(filepath, 'r') as file:
        content = file.read()

    content = re.sub(r'\s+', ' ', content)
    return content

# Run AI/ML predictions using both models
def run_ai_ml_predictions(nb_model, nn_model, tfidf, label_encoder, preprocessed_resume):
    # Vectorize the preprocessed resume
    resume_vectorized = tfidf.transform([preprocessed_resume])

    # Naive Bayes Prediction
    nb_prediction = nb_model.predict(resume_vectorized)[0]
    nb_label = label_encoder.inverse_transform([nb_prediction])[0]

    # Neural Network Prediction
    nn_prediction = nn_model.predict(resume_vectorized.toarray())
    nn_label = label_encoder.inverse_transform([np.argmax(nn_prediction)])[0]

    return {
        "Naive Bayes Prediction": nb_label,
        "Neural Network Prediction": nn_label
    }

# Example usage
def predict_resume(filepath):
    # Load models and preprocess resume
    nb_model, nn_model, tfidf, label_encoder = load_ml_model()
    preprocessed_resume = preprocess_resume(filepath)
    
    # Get predictions
    predictions = run_ai_ml_predictions(nb_model, nn_model, tfidf, label_encoder, preprocessed_resume)
    return predictions
