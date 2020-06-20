
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import imagenet_utils
from PIL import Image
import numpy as np
from flask import Flask,json,jsonify,request
import io
from google.cloud import storage
import os

# initialize our Flask application and the Keras model
model = None
storage_client = None
app = Flask(__name__)

def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    model = ResNet50(weights="imagenet")


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

    print(blob.public_url)


@app.route("/predict", methods=['POST'])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if request.method == "POST":
        if request.files.get("image"):
            # read the image in PIL format
            print(request.form)
            image_file = request.files["image"]
            image = image_file.read()
            upload_to_gcs(image, image_file.filename, image_file.content_type)

            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(224, 224))

            # classify the input image and then initialize the list
            # of predictions to return to the client
            preds = model.predict(image)
            results = imagenet_utils.decode_predictions(preds)
            data["predictions"] = []

            # loop over the results and add them to the list of
            # returned predictions
            for (imagenetID, label, prob) in results[0]:
                r = {"label": label, "probability": float(prob)}
                data["predictions"].append(r)

            # indicate that the request was a success
            data["success"] = True

    # return the data dictionary as a JSON response
    return jsonify(data)

@app.route("/")
def welcome():
    return "Welcome to Robin Huang's Image Classifier Project"

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
        "please wait until server has fully started"))
    load_model()
    app.run(host='0.0.0.0', debug=True,port=int(os.environ.get('PORT', 8080))) # TODO remove debug when deploying