#!/bin/bash

PROJECT_ID="your-firebase-or-gcp-project-id"
SERVICE_NAME="ecg-api"
REGION="us-central1"

echo "🔧 Submitting Cloud Build..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "✅ Deployment complete!"
