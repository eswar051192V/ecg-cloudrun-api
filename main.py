from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import heartpy as hp
import os
import uvicorn

app = FastAPI()

class ECGData(BaseModel):
    ecg_values: List[float]
    sample_rate: float

@app.post("/analyze-ecg")
def analyze_ecg(data: ECGData):
    try:
        wd, m = hp.process(data.ecg_values, sample_rate=data.sample_rate)

        def format_val(key, unit="", precision=2, percentage=False):
            val = m.get(key)
            if val is None:
                return "N/A"
            if percentage:
                return f"{round(val, precision)}%"
            return f"{round(val, precision)} {unit}".strip()

        # --- Simple AFib logic based on HRV markers ---
        def detect_afib(m):
            try:
                bpm = m.get('bpm', 0)
                rmssd = m.get('rmssd', 0)
                sdnn = m.get('sdnn', 0)
                pnn50 = m.get('pnn50', 0)

                # Simple rules (tunable thresholds based on literature)
                if bpm > 100 and rmssd > 50 and sdnn > 50 and pnn50 > 10:
                    return True
            except:
                pass
            return False

        afib_detected = detect_afib(m)

        return {
            "bpm": format_val('bpm', "BPM"),
            "ibi": format_val('ibi', "ms"),
            "rmssd": format_val('rmssd', "ms"),
            "sdnn": format_val('sdnn', "ms"),
            "pnn20": format_val('pnn20', "%", precision=1, percentage=True),
            "pnn50": format_val('pnn50', "%", precision=1, percentage=True),
            "afib": afib_detected,
            "summary": {
                "heart_rate": format_val('bpm', "BPM"),
                "variability": f"SDNN: {format_val('sdnn', 'ms')}, RMSSD: {format_val('rmssd', 'ms')}",
                "pnn": f"pNN20: {format_val('pnn20', '%', percentage=True)}, pNN50: {format_val('pnn50', '%', percentage=True)}",
                "afib_status": "Possible AFib detected" if afib_detected else "Normal rhythm"
            },
            "success": True
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing ECG: {str(e)}")

# --- Cloud Run compatibility ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
