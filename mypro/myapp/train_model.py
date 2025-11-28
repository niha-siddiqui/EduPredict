import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv("student_data.csv")

# Features
X = df.drop("final_score", axis=1)
y = df["final_score"]

# Columns
categorical_cols = ["interest", "strength_subject", "weak_subject"]
numeric_cols = ["study_hours", "math_marks", "english_marks", "science_marks", "urdu_marks"]

# Preprocessor
preprocessor = ColumnTransformer([
    ("num", "passthrough", numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

# Model
model = Pipeline([
    ("preprocess", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=300, random_state=42))
])

# Train
model.fit(X, y)

# Save Model
joblib.dump(model, "student_model.pkl")