import numpy as np
import joblib

# Define the test data
test_data = np.array([[-100,-62,-74,-100,-70,-100,-80,-89]])

# Load the saved model
try:
    rf_model = joblib.load("random_forest_model.pkl")
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Model file not found. Ensure 'random_forest_model.pkl' exists in the current directory.")
    exit()

# Load the saved StandardScaler
try:
    scaler = joblib.load("scaler.pkl")  # Save the scaler during training and load it here
    print("Scaler loaded successfully.")
except FileNotFoundError:
    print("Scaler file not found. Ensure 'scaler.pkl' exists in the current directory.")
    exit()

# Scale the test data
scaled_test_data = scaler.transform(test_data)

# Make a prediction
predicted_label_encoded = rf_model.predict(scaled_test_data)

# Decode the predicted label
try:
    label_encoder = joblib.load("label_encoder.pkl")  # Save the label encoder during training and load it here
    predicted_label = label_encoder.inverse_transform(predicted_label_encoded)
    print("Prediction:", predicted_label[0])
except FileNotFoundError:
    print("Label encoder file not found. Ensure 'label_encoder.pkl' exists in the current directory.")
