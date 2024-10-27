from flask import Flask, render_template, request
import requests
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import os
import time
from mail import send_email

app = Flask(__name__)

# Load the trained model once when the app starts
model = load_model('wildfire_model.h5')

# Prediction function using the trained model
def predict_image(image_path,lati,longi):
    img = load_img(image_path, target_size=(32, 32))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    confidence_score = prediction * 100  # Confidence as a percentage
    
    # Determine result and alert status
    if confidence_score > 70:
        result = f"Wildfire ({confidence_score:.2f}%)"
        alert_message = "Alert: High confidence of wildfire detected!"
        send_email( to_email="manit.roy@research.iiit.ac.in",
                    subject="Wildfire Alert",
                    message=f"Selected location ({lati},{longi}) has a high confidence of wildfire detected!")
    else:
        result = f"No Wildfire ({(100 - confidence_score):.2f}%)"
        alert_message = None  # No alert if below threshold

    return result, alert_message

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    alert_message = None
    duration = None
    longitude = "-122.1017"  # Default value
    latitude = "40.9234"     # Default value

    if request.method == "POST":
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")

        # Record the start time
        start_time = time.time()
        
        # Generate the Mapbox image URL
        image_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{longitude},{latitude},15,0/350x350?access_token=pk.eyJ1IjoibWFuaXRyb3kiLCJhIjoiY20ycWd2dXdtMHZ4MTJrc2JybHd3cGUwcSJ9.yx0nRq4aBYh1Imo2vCiz7Q"
        
        # Download the image
        if "run_demo" in request.form:
            image_path = "static/demo.jpg"
        else:
            image_path = "test.jpg"
            response = requests.get(image_url)
            with open(image_path, "wb") as file:
                file.write(response.content)
        
        # Run prediction on the downloaded image and get the alert message
        result, alert_message = predict_image(image_path,latitude,longitude)

        # Calculate the duration
        duration = time.time() - start_time

        # Optionally delete the image after prediction to free up space
        if "run_demo" not in request.form:
            os.remove(image_path)

    return render_template("index.html", result=result, duration=duration, alert_message=alert_message, longitude=longitude, latitude=latitude)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
