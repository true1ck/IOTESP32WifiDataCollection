from flask import Flask, request, jsonify, render_template, Response
import numpy as np
import joblib
import json
from threading import Lock

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

# Global variable to store the latest predictions
latest_predictions = None
predictions_lock = Lock()


def generate_grid():
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    cols = [str(i).zfill(2) for i in range(11, 20)]  # 11 to 18
    grid = [[f"{row}{col}" for col in cols] for row in rows]
    return grid


@app.route('/', methods=['GET'])
def index():
    """
    Render the grid on the web interface.
    """
    grid = generate_grid()
    return render_template('index.html', grid=grid)

@app.route('/showLoc', methods=['POST'])
def show_loc():
    """
    Handle the POST request and update the global predictions variable.
    """
    global latest_predictions

    try:
        # Log the raw request payload for debugging
        print("Raw Request Data:", request.data.decode('utf-8'))

        # Get JSON data from the request
        data = request.json
        print("Parsed JSON Data:", data)  # Print parsed JSON for debugging

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

        # Update the global predictions variable
        with predictions_lock:
            latest_predictions = [{"location": loc, "probability": float(prob)} for loc, prob in zip(top_classes, top_probabilities)]

        # Print the formatted JSON predictions in the terminal
        print("Predictions (JSON):", json.dumps({"predictions": latest_predictions}, indent=4))

        # Return the predictions as JSON
        return jsonify({"predictions": latest_predictions}), 200

    except Exception as e:
        # Log the error message in the terminal
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/stream')
def stream():
    """
    Stream updates to the client using Server-Sent Events (SSE).
    """
    def event_stream():
        previous_predictions = None
        while True:
            with predictions_lock:
                if latest_predictions != previous_predictions:
                    # Send new predictions only if they have changed
                    previous_predictions = latest_predictions
                    yield f"data: {json.dumps(latest_predictions)}\n\n"

    return Response(event_stream(), content_type="text/event-stream")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Running on port 5001
