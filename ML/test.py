import numpy as np
import  joblib

# Load the saved Random Forest model
rf_model = joblib.load("random_forest_model.pkl")
print("Model loaded successfully.")

# Load the scaler used during training
scaler = joblib.load("scaler.pkl")
print("Scaler loaded successfully.")

# Load the label encoder
label_encoder = joblib.load("label_encoder.pkl")
print("Label Encoder loaded successfully.")

# Test data point (replace with your values)
test_point = np.array([[-69,-73,-60,-90,-70,-80,-58,-92]])  # Ensure it's 2D for scaling

# Scale the test point
scaled_test_point = scaler.transform(test_point)

# Get class probabilities
probabilities = rf_model.predict_proba(scaled_test_point)[0]

# Get indices of the top 3 probable classes
top_3_indices = np.argsort(probabilities)[-3:][::-1]  # Sort and get top 3 in descending order

# Decode the top 3 predictions
top_3_labels = label_encoder.inverse_transform(top_3_indices)
top_3_probs = probabilities[top_3_indices]

# Output the top 3 predictions with probabilities
print("Top 3 Predicted Locations:")
for label, prob in zip(top_3_labels, top_3_probs):
    print(f"{label}: {prob * 100:.2f}%")
