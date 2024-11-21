#include <WiFi.h>
#include <HTTPClient.h>

// List of specified APs you want to track
const String targetAPs[] = {"CSG518-1", "CSG518-2", "CSG518-3", "CSG518-4", 
                            "CSG518-5", "CSG518-6", "CSG518-7", "CSG518-8"};
const int numAPs = sizeof(targetAPs) / sizeof(targetAPs[0]);

// Your Wi-Fi network credentials
const char* ssid = "My123";              // Replace with your Wi-Fi SSID
const char* password = "1029384756";  // Replace with your Wi-Fi password

// Server URL
const char* serverURL = "http://192.168.54.12:5000/post-rssi";  // Replace with your Flask server IP

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

    Serial.println("Setup complete. Starting real-time RSSI monitoring...");
}

void loop() {
    // Perform a Wi-Fi scan
    int n = WiFi.scanNetworks(false, false, false, 120);  // 120ms timeout per channel
    Serial.println("Scan complete!");

    // Create an array to store RSSI values for the target APs
    int rssiValues[numAPs];
    for (int i = 0; i < numAPs; ++i) {
        rssiValues[i] = -999;  // Initialize to a value unlikely for RSSI
    }

    // Process scan results
    if (n > 0) {
        for (int i = 0; i < n; ++i) {
            String ssid = WiFi.SSID(i);  // Get SSID of the current network

            // Check if the SSID is one of the target APs
            for (int j = 0; j < numAPs; ++j) {
                if (ssid == targetAPs[j]) {
                    rssiValues[j] = WiFi.RSSI(i);  // Store RSSI value
                    break;  // Stop checking after finding a match
                }
            }
        }
    }

    // Construct JSON payload
    String jsonPayload = "{";
    int foundCount = 0;
    for (int i = 0; i < numAPs; ++i) {
        if (rssiValues[i] != -999) {  // Only include found APs
            if (foundCount > 0) {
                jsonPayload += ", ";
            }
            jsonPayload += "\"" + targetAPs[i] + "\": " + String(rssiValues[i]);
            foundCount++;
        }
    }
    jsonPayload += "}";

    if (foundCount > 0) {  // Send data if any target APs are found
        sendRSSIToServer(jsonPayload);
    } else {
        Serial.println("No target networks found, skipping data upload.");
    }

    // Delay before the next scan
    delay(200);  // Adjust as needed for faster updates
}

void sendRSSIToServer(const String& jsonPayload) {
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
