from flask import Flask, request, jsonify, render_template_string
import os
import csv

app = Flask(__name__)

# Directory and CSV file setup
data_dir = 'rssi_data'
os.makedirs(data_dir, exist_ok=True)
csv_file_path = os.path.abspath(f'{data_dir}/rssi_data.csv')
print(f"CSV File Path: {csv_file_path}")

# Server state
entry_count = 0
entry_limit = 25  # Default entries per batch
data_collection_active = False
current_output = "g11"

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Network1', 'RSSI1', 'Network2', 'RSSI2', 'Network3', 'RSSI3',
                            'Network4', 'RSSI4', 'Network5', 'RSSI5', 'Network6', 'RSSI6',
                            'Network7', 'RSSI7', 'Network8', 'RSSI8', 'Output'])

# HTML template for the webpage
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>RSSI Data Collection</title>
</head>
<body>
    <h1>RSSI Data Collection</h1>
    <form action="/set-output" method="POST">
        <label for="output">Output Value:</label>
        <input type="text" id="output" name="output" value="{{ current_output }}">
        <button type="submit">Set Output</button>
    </form>
    <br>
    <form action="/set-entry-limit" method="POST">
        <label for="entry_limit">Set Entry Limit:</label>
        <input type="number" id="entry_limit" name="entry_limit" value="{{ entry_limit }}">
        <button type="submit">Set Limit</button>
    </form>
    <br>
    <form action="/toggle-collection" method="POST">
        {% if data_collection_active %}
            <button type="submit">Stop Data Collection</button>
        {% else %}
            <button type="submit">Start Data Collection</button>
        {% endif %}
    </form>
    <p>Current Status: {{ "Active" if data_collection_active else "Inactive" }}</p>
    <p>Entries in Current Batch: {{ entry_count }} / {{ entry_limit }}</p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template, current_output=current_output,
                                  data_collection_active=data_collection_active,
                                  entry_count=entry_count, entry_limit=entry_limit)

@app.route('/set-output', methods=['POST'])
def set_output():
    global current_output
    current_output = request.form.get('output', 'g11')
    return render_template_string(html_template, current_output=current_output,
                                  data_collection_active=data_collection_active,
                                  entry_count=entry_count, entry_limit=entry_limit)

@app.route('/set-entry-limit', methods=['POST'])
def set_entry_limit():
    global entry_limit
    try:
        new_limit = int(request.form.get('entry_limit', entry_limit))
        if new_limit > 0:
            entry_limit = new_limit
        return render_template_string(html_template, current_output=current_output,
                                      data_collection_active=data_collection_active,
                                      entry_count=entry_count, entry_limit=entry_limit)
    except ValueError:
        return jsonify({"error": "Invalid entry limit"}), 400

@app.route('/toggle-collection', methods=['POST'])
def toggle_collection():
    global data_collection_active, entry_count
    data_collection_active = not data_collection_active
    if data_collection_active:
        entry_count = 0
    return render_template_string(html_template, current_output=current_output,
                                  data_collection_active=data_collection_active,
                                  entry_count=entry_count, entry_limit=entry_limit)

@app.route('/post-rssi', methods=['POST'])
def post_rssi():
    global entry_count, data_collection_active

    if not data_collection_active:
        return jsonify({"message": "Data collection is not active."}), 400

    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        # Ensure data for 8 networks with default RSSI value for missing networks
        expected_networks = [f"CSG518-{i}" for i in range(1, 9)]
        row = []
        default_rssi = -100  # Placeholder for missing values
        for network in expected_networks:
            rssi = data.get(network, default_rssi)
            row.extend([network, rssi])

        # Append the output value
        row.append(current_output)

        # Write to CSV
        with open(csv_file_path, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row)

        entry_count += 1
        if entry_count >= entry_limit:
            data_collection_active = False
            return jsonify({"message": "Entry limit reached. Data collection stopped.",
                            "entry_count": entry_count}), 200

        return jsonify({"message": "Data received and stored", "entry_count": entry_count}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
