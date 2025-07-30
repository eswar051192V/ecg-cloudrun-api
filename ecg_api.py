from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ECGInput(BaseModel):
    ecg_values: list[float]

@app.post("/process-ecg")
def process_ecg(data: ECGInput):
    # Replace this with actual ECG logic using HeartPy or your model
    avg_hr = sum(data.ecg_values) / len(data.ecg_values)
    afib_warning = avg_hr > 100  # placeholder logic
    return {"heart_rate": avg_hr, "afib_warning": afib_warning}
