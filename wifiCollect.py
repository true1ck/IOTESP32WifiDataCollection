from flask import Flask, request, jsonify
import os
import csv

app = Flask(__name__)

# Create directories for data if they don't exist
if not os.path.exists('rssi_data'):
    os.makedirs('rssi_data')

# Path for CSV file
csv_file_path = os.path.abspath('rssi_data/rssi_data.csv')  # Use absolute path
print(f"CSV File Path: {csv_file_path}")

# Initialize an entry counter
entry_count = 0
entry_limit = 5  # Limit to 100 entries

# In-memory buffer for data
data_buffer = []

# Ensure CSV file is ready
if not os.path.exists(csv_file_path):
    # Create CSV file with headers
    try:
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Network1', 'RSSI1', 'Network2', 'RSSI2', 'Network3', 'RSSI3',
                                'Network4', 'RSSI4', 'Network5', 'RSSI5', 'Network6', 'RSSI6',
                                'Network7', 'RSSI7', 'Network8', 'RSSI8', 'Output'])  # Add column headers
    except Exception as e:
        print(f"Error initializing CSV file: {e}")

@app.route('/')
def index():
    return "RSSI Data Collection Server is running"

@app.route('/post-rssi', methods=['POST'])
def post_rssi():
    global entry_count, data_buffer

    try:
        # Get JSON data from POST request
        data = request.get_json()
        print(f"Received data: {data}")  # Debugging output

        # Validate data (expecting 8 networks with their RSSI values)
        if not data or len(data) != 8:
            return jsonify({"error": "Invalid data format, expecting 8 networks with RSSI values"}), 400

        # Flatten data into a single row for CSV
        row = []
        for network, rssi in data.items():
            row.extend([network, rssi])

        # Add the hardcoded output value to the row
        row.append('g11')
        data_buffer.append(row)

        # Increment entry counter
        entry_count += 1

        # Write to CSV file immediately for testing
        with open(csv_file_path, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row)  # Write the current row
            print(f"Row written to CSV: {row}")

        # Stop after 100 entries
        if entry_count >= entry_limit:
            print("Data collection limit reached.")
            return jsonify({"message": "100 entries collected. Stopping data collection."}), 200

        return jsonify({"message": "Data received and stored", "entry_count": entry_count}), 200

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
