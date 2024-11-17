#include <WiFi.h>
#include <HTTPClient.h>

// List of specified APs you want to track
String targetAPs[] = {"CSG518-1", "CSG518-2", "CSG518-3", "CSG518-4", "CSG518-5", "CSG518-6", "CSG518-7", "CSG518-8"};
int numAPs = sizeof(targetAPs) / sizeof(targetAPs[0]);

// Your Wi-Fi network credentials
const char* ssid = "G";           // Replace with your Wi-Fi SSID
const char* password = "55555333";  // Replace with your Wi-Fi password

// Server URL (replace <SERVER_IP> with the actual IP address of your Flask server)
const char* serverURL = "http://192.168.146.112:5000/post-rssi";

int entryCount = 0;  // Track number of entries

void setup() {
    Serial.begin(115200);
    
    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to Wi-Fi...");
    }
    Serial.println("Connected to Wi-Fi");

    // Initialize Wi-Fi in station mode for scanning
    WiFi.mode(WIFI_STA);
    delay(100);  // Small delay to ensure setup is complete

    Serial.println("Starting scan...");
}

void loop() {
    int n = WiFi.scanNetworks();  // Start Wi-Fi scan
    Serial.println("Scan complete!");

    if (n == 0) {
        Serial.println("No networks found");
    } else {
        Serial.printf("%d networks found:\n", n);
        
        // Initialize an array to store RSSI values for each target AP
        int rssiValues[numAPs] = {-100, -100, -100, -100, -100, -100, -100, -100};

        // Iterate through the list of networks found
        for (int i = 0; i < n; ++i) {
            String ssid = WiFi.SSID(i);  // Get SSID of current network

            // Check if the SSID is one of the target APs
            for (int j = 0; j < numAPs; ++j) {
                if (ssid == targetAPs[j]) {
                    rssiValues[j] = WiFi.RSSI(i);  // Store RSSI value for the corresponding target AP
                }
            }
        }

        // Send RSSI data to server if any target APs were found
        sendRSSIToServer(rssiValues);

        // Check if we have collected 100 entries and stop the program
        entryCount++;
        if (entryCount >= 100) {
            Serial.println("Collected 100 entries, stopping...");
            while (true);  // Stop execution
        }
    }

    // Wait a bit before the next scan (adjust as needed)
    delay(2000);  // 2-second delay before scanning again
}

void sendRSSIToServer(int rssiValues[]) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverURL);  // Specify the server URL
        http.addHeader("Content-Type", "application/json");  // Specify content-type header

        // Create JSON payload
        String jsonPayload = "{\"rssi\":[";

        // Add RSSI values for all target APs
        for (int i = 0; i < numAPs; i++) {
            jsonPayload += String(rssiValues[i]);
            if (i < numAPs - 1) {
                jsonPayload += ",";
            }
        }

        jsonPayload += "]}";

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
