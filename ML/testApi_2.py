import time
import threading
from flask import Flask, request, jsonify, render_template, Response
import numpy as np
import joblib
import json
import csv
from threading import Lock
from pykalman import KalmanFilter  # Kalman filter library

app = Flask(__name__)

# Load model, scaler, and label encoder
try:
    rf_model = joblib.load("random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    print("Model, scaler, and label encoder loaded successfully.")
except FileNotFoundError as e:
    print(str(e))
    exit()

# Global variables for predictions and positions
latest_predictions = None
position_history = [None] * 20  # Initialize with 20 slots (None values initially)
predictions_lock = Lock()

# Kalman filter for position smoothing
kf = KalmanFilter(initial_state_mean=0, n_dim_obs=1)
kf = kf.em(np.zeros((10, 1)), n_iter=5)

# Function to write data to a CSV file periodically, keeping only the last 20 entries
def log_positions_to_file():
    while True:
        time.sleep(5)  # Every 5 seconds

        # Open CSV file in write mode to overwrite the file with the latest 20 positions
        with predictions_lock:
            with open("landmark_details.csv", mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["timestamp", "location", "probability"])

                # Write the header if file is empty (only the first time)
                if file.tell() == 0:
                    writer.writeheader()

                # Write the last 20 entries to the file
                for position in position_history:
                    if position:  # Avoid writing None values
                        writer.writerow(position)

# Start the logging thread
threading.Thread(target=log_positions_to_file, daemon=True).start()

@app.route('/', methods=['GET'])
def index():
    grid = generate_grid()
    return render_template('index.html', grid=grid)

@app.route('/showLoc', methods=['POST'])
def show_loc():
    global latest_predictions

    try:
        # Get JSON data from the request
        data = request.json
        if not data or 'rssi_values' not in data:
            return jsonify({"error": "Invalid input. Provide 'rssi_values' in JSON."}), 400

        rssi_values = np.array(data['rssi_values']).reshape(1, -1)
        scaled_rssi_values = scaler.transform(rssi_values)

        # Predict probabilities for each class
        probabilities = rf_model.predict_proba(scaled_rssi_values)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_classes = label_encoder.inverse_transform(top_indices)
        top_probabilities = probabilities[top_indices]

        # Update the global predictions variable
        with predictions_lock:
            latest_predictions = [
                {"location": loc, "probability": float(prob)}
                for loc, prob in zip(top_classes, top_probabilities)
            ]
            # Insert the new prediction at the front and remove the oldest entry to maintain a list of 20
            position_history.insert(0, {
                "timestamp": time.time(),
                "location": top_classes[0],
                "probability": top_probabilities[0]
            })

            # Remove the last element to maintain a fixed size of 20 entries
            if len(position_history) > 20:
                position_history.pop()

            # Debugging: Print updated position history
            print(f"Updated position history: {position_history}")

        return jsonify({"predictions": latest_predictions}), 200

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    def event_stream():
        previous_predictions = None
        while True:
            with predictions_lock:
                if latest_predictions != previous_predictions:
                    previous_predictions = latest_predictions
                    yield f"data: {json.dumps(latest_predictions)}\n\n"
            time.sleep(1)  # Throttle updates to the client

    return Response(event_stream(), content_type="text/event-stream")
@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    try:
        # Get data from the request
        data = request.json
        if not data or 'destination' not in data:
            return jsonify({"error": "Invalid input. Provide 'destination' in JSON."}), 400

        destination = data['destination']
        with predictions_lock:
            # Ensure we have a current location
            if latest_predictions is None or len(latest_predictions) == 0:
                return jsonify({"error": "No current location available."}), 400
            current_location = latest_predictions[0]["location"]

        # Parse the grid coordinates
        def parse_location(location):
            row = ord(location[0].upper()) - ord('A')  # Convert 'A' -> 0, 'B' -> 1, etc.
            col = int(location[1:]) - 11              # Adjust column index (11 -> 0, 12 -> 1, etc.)
            return row, col

        try:
            current_row, current_col = parse_location(current_location)
            dest_row, dest_col = parse_location(destination)
        except Exception as e:
            return jsonify({"error": f"Invalid location format: {e}"}), 400

        # Calculate the route
        route = []
        while current_row != dest_row or current_col != dest_col:
            if current_row < dest_row:
                route.append("down")
                current_row += 1
            elif current_row > dest_row:
                route.append("up")
                current_row -= 1
            elif current_col < dest_col:
                route.append("right")
                current_col += 1
            elif current_col > dest_col:
                route.append("left")
                current_col -= 1

        # Print the calculated route to the terminal for debugging
        print(f"Calculated Route: {route}")

        return jsonify({"route": route}), 200

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


def generate_grid():
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    cols = [str(i).zfill(2) for i in range(11, 20)]  # 11 to 18
    grid = [[f"{row}{col}" for col in cols] for row in rows]
    return grid

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
