# Google-TextToSpeech-API-Python

Command on gcloud SDK : 

gcloud auth login
gcloud config set project text-to-speech-400912    
gcloud services enable run.googleapis.com   
gcloud services enable containerregistry.googleapis.com   
gcloud services enable cloudbuild.googleapis.com  
gcloud services enable storage-component.googleapis.com  
gcloud services enable logging.googleapis.com monitoring.googleapis.com  
gcloud auth configure-docker  
docker build -t gcr.io/text-to-speech-400912/text-to-speech-deploy:v1 .  
docker push gcr.io/text-to-speech-400912/text-to-speech-deploy:v1  
gcloud run deploy text-to-speech-deploy --image gcr.io/text-to-speech-400912/text-to-speech-deploy:v1 --region=asia-southeast2 --platform managed --allow-unauthenticated  
