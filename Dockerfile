FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Cloud Run expects the app to listen on port 8080
EXPOSE 8080

# Ensure uvicorn binds to 0.0.0.0 and uses $PORT
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
