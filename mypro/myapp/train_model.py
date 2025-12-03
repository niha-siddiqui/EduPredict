import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import joblib

# Load updated CSV
df = pd.read_csv("student_data.csv")

# Features & Target
X = df.drop("final_score", axis=1)
y = df["final_score"]

categorical_cols = ["interest", "strength_subject", "weak_subject"]
numeric_cols = [
    "study_hours", "math_marks", "english_marks", "science_marks", "urdu_marks",
    "biology_marks", "computer_marks", "arts_marks", "previous_percentage"
]

# Preprocessing pipeline
preprocessor = ColumnTransformer([
    ("num", "passthrough", numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

model = Pipeline([
    ("preprocess", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=300, random_state=42))
])

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "student_models.pkl")
print("MODEL TRAINED & SAVED SUCCESSFULLY")
