import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

# Load dataset
data = pd.read_csv('train_dataset.csv')

# Preprocess the text data
data['combined_text'] = (data['job_requirements'] + " " + data['resume_text']).str.lower()

# Features and labels
X = data['combined_text']  # Using the combined and preprocessed text
y = data['label']

# Encode labels for neural network
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Save the label encoder to decode predictions later
joblib.dump(label_encoder, 'label_encoder.pkl')

# TF-IDF vectorization
tfidf = TfidfVectorizer()
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Save the TF-IDF vectorizer
joblib.dump(tfidf, 'tfidf_vectorizer.pkl')

# === Naive Bayes Model ===
nb_pipeline = Pipeline([
    ('classifier', MultinomialNB())
])

# Train Naive Bayes model
nb_pipeline.fit(X_train_tfidf, y_train)
joblib.dump(nb_pipeline, 'resume_classifier_nb.pkl')

# === TensorFlow Neural Network Model ===

# Define the neural network model
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_tfidf.shape[1],)),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(len(label_encoder.classes_), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Define early stopping for efficient training
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train the model
model.fit(X_train_tfidf.toarray(), y_train, 
          validation_data=(X_test_tfidf.toarray(), y_test), 
          epochs=20, 
          batch_size=32, 
          callbacks=[early_stopping])

# Save the trained TensorFlow model in the new format
model.save('resume_classifier_nn.keras')
print("TensorFlow model saved as 'resume_classifier_nn.keras'.")

# === Prediction function ===
def predict_with_model(text):
    try:
        nb_model = joblib.load('resume_classifier_nb.pkl')
        nn_model = tf.keras.models.load_model('resume_classifier_nn.keras')
        tfidf = joblib.load('tfidf_vectorizer.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
    except FileNotFoundError as e:
        print(f"Error loading model or vectorizer: {e}")
        return None

    # Preprocess and vectorize the input text
    text = text.lower()  # Convert text to lowercase before vectorizing
    text_tfidf = tfidf.transform([text])

    # Naive Bayes Prediction
    nb_prediction = nb_model.predict(text_tfidf)[0]
    nb_label = label_encoder.inverse_transform([nb_prediction])[0]

    # Neural Network Prediction
    nn_prediction = nn_model.predict(text_tfidf.toarray())
    nn_label = label_encoder.inverse_transform([np.argmax(nn_prediction)])[0]

    return {
        "Naive Bayes Prediction": nb_label,
        "Neural Network Prediction": nn_label
    }

# Example usage:
example_text = "Example job requirement and resume text"
predictions = predict_with_model(example_text)
print(f"sample output: {predictions}")
