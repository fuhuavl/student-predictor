import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.linear_model import LinearRegression

app = FastAPI(title="Student Performance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate dataset
np.random.seed(42)
N = 200

study_hours = np.random.uniform(1, 10, N)
attendance  = np.random.uniform(50, 100, N)

score = (
    6.0 * study_hours
    + 0.5 * attendance
    + np.random.normal(0, 5, N)
).clip(0, 100)

df = pd.DataFrame({
    "student_id":  [f"S{str(i+1).zfill(3)}" for i in range(N)],
    "study_hours": study_hours.round(1),
    "attendance":  attendance.round(1),
    "score":       score.round(1),
})
df["pass_fail"] = df["score"].apply(lambda s: "Pass" if s >= 70 else "Fail")

# Train model
X = df[["study_hours", "attendance"]].values
y = df["score"].values

model = LinearRegression()
model.fit(X, y)

print(f"Model trained. R2 = {model.score(X, y):.3f}")

class PredictRequest(BaseModel):
    study_hours: float
    attendance:  float

class PredictResponse(BaseModel):
    predicted_score: float
    result:          str
    confidence:      str

# Endpoints
@app.get("/health")
def health():
    return {"status": "ok", "model": "LinearRegression", "records": len(df)}

@app.get("/data")
def get_data(min_hours: float = 1, max_hours: float = 10):
    result = df[
        (df["study_hours"] >= min_hours) &
        (df["study_hours"] <= max_hours)
    ]
    return result.to_dict(orient="records")

@app.get("/summary")
def get_summary():
    print(df["pass_fail"].value_counts())
    return {
        "total_students": len(df),
        "avg_score":      round(df["score"].mean(), 1),
        "pass_rate":      round((df["pass_fail"] == "Pass").mean() * 100, 1),
        "avg_study_hrs":  round(df["study_hours"].mean(), 1),
        "avg_attendance": round(df["attendance"].mean(), 1),
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    X_input = np.array([[req.study_hours, req.attendance]])
    raw = float(model.predict(X_input)[0])
    predicted = round(max(0, min(100, raw)), 1)
    result = "Pass" if predicted >= 70 else "Fail"

    if predicted >= 80:
        confidence = "High"
    elif predicted >= 60:
        confidence = "Medium"
    else:
        confidence = "Low"

    return PredictResponse(
        predicted_score=predicted,
        result=result,
        confidence=confidence,
    )