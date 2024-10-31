
# Wildfire Detection and Alert System

This project is a web application that predicts the likelihood of a wildfire based on satellite imagery from a selected location. Users input latitude and longitude coordinates, which are used to fetch satellite images from Mapbox. The application then processes the image through a deep learning model trained to detect wildfire risks. If the confidence score exceeds 70%, an alert email is automatically sent to a specified address.

## Features

- **Location Selection**: Users can enter latitude and longitude manually or use their current location.
- **Mapbox Integration**: Satellite images are fetched from Mapbox based on user-selected coordinates.
- **Wildfire Prediction**: A trained neural network model classifies whether the image indicates a wildfire risk.
- **Email Alert**: If the wildfire confidence exceeds 70%, an alert email is sent to the recipient.
- **Execution Time Display**: Displays the time taken to process the prediction.

## Requirements

- Python 3.6 or higher
- TensorFlow
- Flask
- Requests
- Mapbox API Key
- Gmail account with App Password enabled

## Setup Instructions

### Step 1: Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/manit2004/wildfire-detection.git
cd wildfire-detection
```
### Step 2: MapBox API Key and Google App password

Put the mapbox api key in the appropiate places of index.html and app.py and put the Google App password in the mail.py

### Step 3: Run the web app

```bash
python app.py
```
