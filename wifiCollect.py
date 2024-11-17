from flask import Flask, request, jsonify, render_template
import os
import csv

app = Flask(__name__)

# Create a folder to store data if it doesn't exist
if not os.path.exists('rssi_data'):
    os.makedirs('rssi_data')

# CSV file path
csv_file = 'rssi_data/rssi_data.csv'

# Column headers for CSV
columns = ["CSG518-1", "CSG518-2", "CSG518-3", "CSG518-4", "CSG518-5", "CSG518-6", "CSG518-7", "CSG518-8", "output"]

# Initialize CSV file with headers
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

@app.route('/')
def index():
    # Read the CSV file and display its content
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    return render_template('index.html', rows=rows)

@app.route('/post-rssi', methods=['POST'])
def post_rssi():
    try:
        # Get data from POST request
        data = request.get_json()
        print(f"Received data: {data}")  # Print the received data for debugging

        # Ensure data contains 'rssi'
        if not data or 'rssi' not in data:
            return jsonify({"error": "Invalid data format, missing 'rssi'"}), 400

        # Extract RSSI values from the JSON data
        rssi_values = data.get('rssi')

        # Add an 'output' column with a placeholder (empty value)
        row = rssi_values + [""]

        # Save the data to a CSV file
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return jsonify({"message": "Data received and stored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/update-output', methods=['POST'])
def update_output():
    try:
        data = request.get_json()

        # Validate data
        if 'index' not in data or 'output' not in data:
            return jsonify({"error": "Invalid data format, missing 'index' or 'output'"}), 400

        index = data['index']
        output = data['output']

        # Read the existing CSV data
        with open(csv_file, 'r') as f:
            rows = list(csv.reader(f))

        # Update the output column for the specified row
        if 0 < index < len(rows):
            rows[index][8] = output  # Update the 'output' column (index 8)

        # Write updated data back to CSV
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return jsonify({"message": "Output updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
