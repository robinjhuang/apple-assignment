# apple-assignment

Deploys the pretrained ResNet image classifier from Keras

## API
POST /predict

Takes a file with name image. Can be in format JPG, PNG, GIF.

GET /history

Query params of limit and offset. Default limit 20 and offset 0.

## Database

Images are stored in GCS (Google Cloud Storage)

PostgresSQL DB

primary_key, image_name (text), gcs_url (text), create_at (integer),  

## Frontend

Paginate 20 images at a time, sorted by order of submission

## Rebuild Container

After code changes:

`gcloud builds submit --tag gcr.io/apple-assignment-280918/image-classif .`

## Deploy to GKE (Google Kubernetes Engine)

`kubectl apply -f deployment.yaml`

`kubectl get deployments`

`kubectl describe services`
