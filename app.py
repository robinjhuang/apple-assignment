
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import imagenet_utils
from PIL import Image
import numpy as np
from flask import Flask,json,jsonify,request, render_template
import io
from google.cloud import storage
import os
import datetime
import psycopg2
import json
from tensorflow.keras.models import load_model

# initialize our Flask application and load the Keras model
app = Flask(__name__, template_folder='templates')
model = load_model('resnet.h5', compile=False)

def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image

def upload_to_gcs(image_data, filename, content_type):
    bucket_name = 'image-classifier-apple'
    gcs = storage.Client()
    
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_data, content_type=content_type)

    return blob.public_url

def upload_to_sql(image_name, gcs_url, classification_json):
    
    print("Uploading image results to postgres " + image_name)
    conn = None

    try:
        conn = psycopg2.connect(dbname='prediction', user='postgres', host='127.0.0.1', port=5432, password='images')
        milliseconds_since_epoch = int(datetime.datetime.now().timestamp())
        cursor = conn.cursor()
        json_str = json.dumps(classification_json)
        cursor.execute("INSERT INTO image_classification (id, image_name, gcs_url, create_at, classification_results) VALUES(DEFAULT, %s, %s, %s, %s);", (image_name, gcs_url, milliseconds_since_epoch, json_str))
        conn.commit()
        print("Successfully uploaded to postgres")
    except Exception as e:
        print ("I am unable to connect to the database")
        print (e)


@app.route("/predict", methods=['POST'])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if request.method == "POST":
        if request.files.get("image"):
            # read the image in PIL format
            try:
                image_file = request.files["image"]
                print("Classifying image " + image_file.filename)
                image = image_file.read()

                gcs_url = ''
                try:
                    gcs_url = upload_to_gcs(image, image_file.filename, image_file.content_type)
                except Exception as e:
                    print("Could not upload to GCS")
                    print(e)
                    raise e
                
                image = Image.open(io.BytesIO(image))

                # preprocess the image and prepare it for classification
                image = prepare_image(image, target=(224, 224))

                # classify the input image
                preds = model.predict(image)
                results = imagenet_utils.decode_predictions(preds)
                data["predictions"] = []

                # loop over the results and build predictions
                for (imagenetID, label, prob) in results[0]:
                    r = {"label": label, "probability": float(prob)}
                    data["predictions"].append(r)

                # indicate that the request was a success
                data["success"] = True
                upload_to_sql(image_file.filename, gcs_url, data["predictions"])
            except Exception as e:
                print("Error occured")
                print(e)

    # return the data dictionary as a JSON response
    return jsonify(data)

@app.route("/history", methods=['GET'])
def get_history():
    if request.method == "GET":
        conn = None
        data = None

        # offset params
        offset = 0
        limit = 20
        for param, val in request.args.items():
            if param == "offset":
                offset = val
            elif param == "limit":
                limit = val

        try:
            conn = psycopg2.connect(dbname='prediction', user='postgres', host='127.0.0.1', port=5432, password='images')
            cursor = conn.cursor()
            cursor.execute("SELECT * from image_classification ORDER BY create_at DESC OFFSET %s LIMIT %s;", (offset, limit))
            data = cursor.fetchall()
        except Exception as e:
            print ("I am unable to connect to the database")
            print (e)
            return jsonify(e)

        results = []
        
        for res in data:
            results.append({
                "id": res[0], 
                "name": res[1], 
                "url": res[2], 
                "time": datetime.datetime.fromtimestamp(res[3]).strftime("%A, %B %d, %Y %I:%M:%S"), 
                "predictions": res[4]
            })

        return render_template('result.html', results=results)


@app.route("/")
def welcome():
    return "Welcome to Robin Huang's Image Classifier Service"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=int(os.environ.get('PORT', 8080))) # TODO remove debug when deploying
    