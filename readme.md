
# Wildfire Detection and Alert System

This project is a web application that predicts the likelihood of a wildfire based on satellite imagery from a selected location. Users input latitude and longitude coordinates, which are used to fetch satellite images from Mapbox. The application then processes the image through a deep learning model trained to detect wildfire risks. If the confidence score exceeds 70%, an alert email is automatically sent to a specified address. It also curates top 5 locations in your neighbourhood where you can seek help in case of such emergencies caused by natural disaster. Besides that it also generates a heatmap signifying the risk percentage surronding the selected area and shows a pathway to reach a comparatively safe place bearing lesser risks.

## Features

- **Location Selection**: Users can enter latitude and longitude manually or use their current location to find the most accurate satellite imagery for a specific area. This feature enables easy monitoring of locations, including remote and high-risk zones.

- **Mapbox Integration**: Integrated with Mapbox, the application fetches high-resolution satellite images based on user-selected coordinates. These images serve as input to the predictive model, ensuring precise risk assessments based on real-time data.

- **Wildfire Prediction Model**: A deep learning model, trained on diverse datasets of wildfire-prone regions, classifies each image to predict wildfire risks. The model outputs a confidence score, indicating the probability of wildfire occurrence, enabling users to act on credible information.

- **Automated Email Alerts**: For any prediction that shows a wildfire confidence level above 70%, the application triggers an automated alert email to a pre-specified recipient. This early warning system ensures that users and relevant authorities are informed promptly for emergency response.

- **Neighborhood Safety Recommendations**: The application curates a list of the top five nearby locations that can serve as emergency shelters or safe points in case of a wildfire or natural disaster. These locations are selected based on proximity, accessibility, and safety from potential wildfire zones.

- **Risk Heatmap Visualization**: The system generates a detailed heatmap for the selected area, representing the wildfire risk percentage in surrounding regions. This visual cue allows users to gauge risk levels in their vicinity and make informed decisions about travel and evacuation.

- **Safe Pathway Navigation**: Users are provided with a suggested pathway leading to a nearby, comparatively safer area, with a lower risk level. This feature is especially useful for directing people to safer zones when immediate evacuation is necessary.

- **Execution Time Display**: To enhance user experience, the application displays the time taken for each prediction, ensuring transparency and helping users gauge the processing speed. This feature is beneficial for monitoring system performance, especially during critical situations when prompt responses are essential. 


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
