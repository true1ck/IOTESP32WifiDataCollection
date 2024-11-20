from flask import Flask, request, jsonify
import numpy as np
import joblib

app = Flask(__name__)

# Load the saved Random Forest model
try:
    rf_model = joblib.load("random_forest_model.pkl")
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Model file not found. Ensure 'random_forest_model.pkl' exists in the current directory.")
    exit()

# Load the saved StandardScaler
try:
    scaler = joblib.load("scaler.pkl")
    print("Scaler loaded successfully.")
except FileNotFoundError:
    print("Scaler file not found. Ensure 'scaler.pkl' exists in the current directory.")
    exit()

# Load the saved LabelEncoder
try:
    label_encoder = joblib.load("label_encoder.pkl")
    print("Label encoder loaded successfully.")
except FileNotFoundError:
    print("Label encoder file not found. Ensure 'label_encoder.pkl' exists in the current directory.")
    exit()

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to make predictions with the trained model.
    Accepts JSON input with RSSI values and returns the top 3 predictions.
    """
    try:
        # Get JSON data from request
        data = request.json
        if not data or 'rssi_values' not in data:
            return jsonify({"error": "Invalid input. Provide 'rssi_values' in JSON."}), 400

        # Extract RSSI values
        rssi_values = np.array(data['rssi_values']).reshape(1, -1)

        # Scale the RSSI values
        scaled_rssi_values = scaler.transform(rssi_values)

        # Predict probabilities for each class
        probabilities = rf_model.predict_proba(scaled_rssi_values)[0]

        # Get the top 3 predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_classes = label_encoder.inverse_transform(top_indices)
        top_probabilities = probabilities[top_indices]

        # Prepare the response
        predictions = [{"location": loc, "probability": float(prob)} for loc, prob in zip(top_classes, top_probabilities)]
        return jsonify({"predictions": predictions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change the port to 8080 or any other available port

