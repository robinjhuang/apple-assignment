# apple-assignment

1. Set up Flask app [done]
1. How to upload an image via API [done]
1. How to run a classifier [done]
1. NoSQL database key value pair to analyze results
1. Frontend for displaying results
1. Dockerize
1. Deploy to GKE

## Database

Images are stored in GCS (Google Cloud Storage)

SQL DB

primary_key, image_name (text), gcs_url (text), create_at (integer),  

## Frontend

Paginate 20 images at a time, sorted by order of prediction

## Rebuild Container

After code changes:

`gcloud builds submit --tag gcr.io/apple-assignment-280918/image-classif .`

## Deploy to GKE (Google Kubernetes Engine)

`kubectl apply -f deployment.yaml`

`kubectl get deployments`

`kubectl describe services`
