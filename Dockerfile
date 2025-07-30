FROM python:3.10-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cloud Run expects the app to listen on port 8080
EXPOSE 8080

# Entrypoint for Cloud Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
