import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "student_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "student_model.pkl")

# Load CSV
df = pd.read_csv(CSV_PATH)

# Features aur target
features = ["study_hours","math_marks","english_marks","science_marks","urdu_marks",
            "biology_marks","computer_marks","arts_marks"]
target = "final_percentage"

X = df[features]
y = df[target]

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, MODEL_PATH)
print("Model trained and saved at:", MODEL_PATH)
