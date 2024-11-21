#include <WiFi.h>
#include <HTTPClient.h>

// List of specified APs you want to track
String targetAPs[] = {"CSG518-1", "CSG518-2", "CSG518-3", "CSG518-4", 
                      "CSG518-5", "CSG518-6", "CSG518-7", "CSG518-8"};
int numAPs = sizeof(targetAPs) / sizeof(targetAPs[0]);

// Your Wi-Fi network credentials
const char* ssid = "My";           // Replace with your Wi-Fi SSID
const char* password = "1029384756";  // Replace with your Wi-Fi password

// Server URL for the showLoc API (use the external IP of the machine running Flask)
const char* serverURL = "http://192.168.87.54:5001/showLoc";  // Replace X with your machine's IP

void setup() {
    Serial.begin(9600);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(100);
        Serial.println("Connecting to Wi-Fi...");
    }
    Serial.println("Connected to Wi-Fi");

    // Initialize Wi-Fi in station mode for scanning
    WiFi.mode(WIFI_STA);
    delay(100);  // Small delay to ensure setup is complete

    Serial.println("Starting scan...");
}

void loop() {
    // Use faster scan with reduced timeout per channel
    int n = WiFi.scanNetworks(false, false, false, 120);  // 120ms timeout per channel
    Serial.println("Scan complete!");

    // Create a map to track found APs
    int foundRSSI[numAPs];
    for (int i = 0; i < numAPs; ++i) {
        foundRSSI[i] = -999;  // Initialize to a value unlikely for RSSI
    }

    if (n == 0) {
        Serial.println("No networks found");
    } else {
        Serial.printf("%d networks found:\n", n);

        // Iterate through the list of networks found
        for (int i = 0; i < n; ++i) {
            String ssid = WiFi.SSID(i);  // Get SSID of current network

            // Check if the SSID is one of the target APs
            for (int j = 0; j < numAPs; ++j) {
                if (ssid == targetAPs[j]) {
                    foundRSSI[j] = WiFi.RSSI(i);  // Save RSSI value
                    break;
                }
            }
        }
    }

    // Check if all target APs are found
    bool allFound = true;
    for (int i = 0; i < numAPs; ++i) {
        if (foundRSSI[i] == -999) {
            allFound = false;  // At least one AP is missing
            break;
        }
    }

    if (allFound) {
        // Build JSON payload
        String jsonPayload;
        jsonPayload.reserve(256);  // Preallocate memory for performance
        jsonPayload = "{ \"rssi_values\": [";
        for (int i = 0; i < numAPs; ++i) {
            if (i > 0) {
                jsonPayload += ", ";
            }
            jsonPayload += foundRSSI[i];
        }
        jsonPayload += "]}";  // Close the array for RSSI values

        // Send the JSON payload to the server
        sendRSSIToServer(jsonPayload);
    } else {
        Serial.println("Not all target networks found, skipping data upload.");
    }

    // Delay 2 seconds before the next scan
    delay(3000);
}

void sendRSSIToServer(String jsonPayload) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverURL);  // Specify the server URL
        http.addHeader("Content-Type", "application/json");  // Specify content-type header

        // Send HTTP POST request
        int httpResponseCode = http.POST(jsonPayload);

        // Check HTTP response code
        if (httpResponseCode > 0) {
            String response = http.getString();  // Get the response from the server
            Serial.printf("HTTP Response code: %d\n", httpResponseCode);
            Serial.println(response);
        } else {
            Serial.printf("Error in HTTP request: %s\n", http.errorToString(httpResponseCode).c_str());
        }

        http.end();  // End the HTTP request
    } else {
        Serial.println("Wi-Fi is not connected");
    }
}
