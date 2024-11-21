#include <WiFi.h>
#include <HTTPClient.h>

// List of specified APs you want to track
String targetAPs[] = {"CSG518-1", "CSG518-2", "CSG518-3", "CSG518-4", 
                      "CSG518-5", "CSG518-6", "CSG518-7", "CSG518-8"};
int numAPs = sizeof(targetAPs) / sizeof(targetAPs[0]);

// Your Wi-Fi network credentials
const char* ssid = "Nobal";           // Replace with your Wi-Fi SSID
const char* password = "1234567878";  // Replace with your Wi-Fi password

// Server URL (replace <SERVER_IP> with the actual IP address of your Flask server)
const char* serverURL = "http://192.168.231.54:5000/post-rssi";  // Replace with your Flask server IP

void setup() {
    Serial.begin(9600);

    // Connect to Wi-FiH
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

    if (n == 0) {
        Serial.println("No networks found");
    } else {
        Serial.printf("%d networks found:\n", n);

        // JSON payload to hold RSSI values for target APs
        String jsonPayload;
        jsonPayload.reserve(256);  // Preallocate memory for performance
        jsonPayload = "{";
        int foundCount = 0;

        // Iterate through the list of networks found
        for (int i = 0; i < n; ++i) {
            String ssid = WiFi.SSID(i);  // Get SSID of current network

            // Check if the SSID is one of the target APs
            for (int j = 0; j < numAPs; ++j) {
                if (ssid == targetAPs[j]) {
                    // Append the RSSI value to JSON payload
                    if (foundCount > 0) {
                        jsonPayload += ", ";
                    }
                    jsonPayload += "\"" + ssid + "\": " + WiFi.RSSI(i);
                    foundCount++;
                }
            }
        }

        jsonPayload += "}";

        if (foundCount > 0) {  // Send data even if not all APs are found
            sendRSSIToServer(jsonPayload);
        } else {
            Serial.println("No target networks found, skipping data upload.");
        }  
    }

    // Reduce delay between scans to make data collection faster
    delay(100);  // Small delay to prevent overloading the system
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
