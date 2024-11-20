import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

# Load the dataset
data = pd.read_csv("wifi_signal_data.csv")  # Replace with your CSV file name
features = data.iloc[:, 1:].values  # RSSI values (1, 2, 3, ...)
labels = data.iloc[:, 0].values  # Location (A00, A01, ...)

# Encode location labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Split the data into training and testing sets (80-20 split)
X_train, X_test, y_train, y_test = train_test_split(features, encoded_labels, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the Random Forest Classifier (for evaluation)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the trained Random Forest model
joblib.dump(rf_model, "random_forest_model.pkl")
print("Model saved as 'random_forest_model.pkl'")

# Make predictions with Random Forest
y_pred_rf = rf_model.predict(X_test)

# Confusion Matrix and Classification Report for Random Forest
cm_rf = confusion_matrix(y_test, y_pred_rf)
report_rf = classification_report(y_test, y_pred_rf, target_names=label_encoder.classes_)

print("Random Forest Classification Report:\n", report_rf)

# Plot the confusion matrix for Random Forest
plt.figure(figsize=(10, 8))
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix - Random Forest')
plt.show()

# Load the saved Random Forest model (for validation or later use)
loaded_rf_model = joblib.load("random_forest_model.pkl")
print("Model loaded successfully.")

# Use the loaded model to make predictions
y_pred_loaded_rf = loaded_rf_model.predict(X_test)

# Confirm the loaded model's predictions match the original model
if np.array_equal(y_pred_rf, y_pred_loaded_rf):
    print("Loaded model predictions match the original model.")
else:
    print("Loaded model predictions do not match the original model.")
