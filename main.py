from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import heartpy as hp
import numpy as np
import os
import uvicorn

app = FastAPI()

class ECGData(BaseModel):
    ecg_values: List[float]
    sample_rate: float

@app.get("/")
def root():
    return {"status": "ECG API running"}

@app.post("/analyze-ecg")
def analyze_ecg(data: ECGData):
    try:
        ecg_array = np.array(data.ecg_values)
        wd, m = hp.process(ecg_array, sample_rate=data.sample_rate)

        def format_val(key, unit="", precision=2, percentage=False):
            val = m.get(key)
            if val is None:
                return "N/A"
            if percentage:
                return f"{round(val, precision)}%"
            return f"{round(val, precision)} {unit}".strip()

        def detect_afib(m):
            try:
                bpm = m.get("bpm", 0)
                rmssd = m.get("rmssd", 0)
                sdnn = m.get("sdnn", 0)
                pnn50 = m.get("pnn50", 0)
                if bpm > 100 and rmssd > 50 and sdnn > 50 and pnn50 > 10:
                    return True
            except:
                pass
            return False

        def classify_rhythm_status(m, afib):
            if afib:
                return "Possible AFib"
            rmssd = m.get("rmssd", 0)
            sdnn = m.get("sdnn", 0)
            if rmssd < 15 and sdnn < 20:
                return "Low Variability"
            elif rmssd > 100 or sdnn > 100:
                return "Irregular Rhythm"
            return "Normal Rhythm"

        afib_detected = detect_afib(m)
        rhythm_status = classify_rhythm_status(m, afib_detected)

        return {
            "bpm": format_val("bpm", "BPM"),
            "ibi": format_val("ibi", "ms"),
            "rmssd": format_val("rmssd", "ms"),
            "sdnn": format_val("sdnn", "ms"),
            "pnn20": format_val("pnn20", "%", precision=1, percentage=True),
            "pnn50": format_val("pnn50", "%", precision=1, percentage=True),
            "afib": afib_detected,
            "rhythm_status": rhythm_status,
            "summary": {
                "heart_rate": format_val("bpm", "BPM"),
                "variability": f"SDNN: {format_val('sdnn', 'ms')}, RMSSD: {format_val('rmssd', 'ms')}",
                "pnn": f"pNN20: {format_val('pnn20', '%', percentage=True)}, pNN50: {format_val('pnn50', '%', percentage=True)}",
                "afib_status": "Possible AFib detected" if afib_detected else "Normal rhythm",
                "rhythm_status": rhythm_status
            },
            "success": True,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing ECG: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
