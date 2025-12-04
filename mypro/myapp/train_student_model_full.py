import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "student_records_full.csv")
MODEL_FILE = os.path.join(BASE_DIR, "student_model_full.pkl")

# Load CSV
data = pd.read_csv(CSV_FILE)

# Features for prediction
FEATURES = ["study_hours","math_marks","english_marks","science_marks","urdu_marks",
            "biology_marks","computer_marks","arts_marks"]
TARGET = "final_percentage"

X = data[FEATURES]
y = data[TARGET]

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, MODEL_FILE)
print(f"Model saved successfully at {MODEL_FILE}")
