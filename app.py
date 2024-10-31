from flask import Flask, render_template, request
import requests
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import os
import time
from mail import send_email
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from location_info import get_location_info

app = Flask(__name__)
mapbox_api_key= "pk.eyJ1IjoibWFuaXRyb3kiLCJhIjoiY20ycWd2dXdtMHZ4MTJrc2JybHd3cGUwcSJ9.yx0nRq4aBYh1Imo2vCiz7Q"

# Load the trained model once when the app starts
model = load_model('wildfire_model.h5')
# Function to generate a grid of coordinates around a central point
def generate_grid(center_lat, center_lon, lat_step=0.0036, lon_step=0.0064, grid_size=3):
    # Calculate the start of the grid by shifting half the total distance from the center
    start_lat = center_lat - (lat_step * (grid_size // 2))
    start_lon = center_lon - (lon_step * (grid_size // 2))

    # Create a 2D array to store the coordinates
    grid = []

    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            lat = start_lat + (i * lat_step)
            lon = start_lon + (j * lon_step)
            row.append((lat, lon))
        grid.append(row)

    return np.array(grid)

def generate_heatmap(grid_matrix):
    result_grid = []

# Prediction function using the trained model
def predict_image(image_path,lati,longi, ALERT=True):
    img = load_img(image_path, target_size=(32, 32))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    confidence_score = prediction * 100  # Confidence as a percentage
    
    # Determine result and alert status
    if confidence_score > 70:
        result = f"Wildfire ({confidence_score:.2f}%)"
        alert_message=None
        if ALERT:
            alert_message = "Alert: High confidence of wildfire detected!"
            send_email( to_email="manit.roy@research.iiit.ac.in",
                        subject="Wildfire Alert",
                        message=f"Selected location ({lati},{longi}) has a high confidence of wildfire detected!")
    else:
        result = f"No Wildfire ({(100 - confidence_score):.2f}%)"
        alert_message = None  # No alert if below threshold

    return result, alert_message

# Conversion function
def convert_to_numeric(array):
    numeric_array = []
    for row in array:
        numeric_row = []
        for cell in row:
            # Extracting the percentage value
            percent = float(cell.split('(')[-1].strip('%)'))
            # Converting to the scale where "No Wildfire 100%" is 0 and "Wildfire 100%" is 100
            value = 100 - percent if "No Wildfire" in cell else percent
            numeric_row.append(value)
        numeric_array.append(numeric_row)
    return numeric_array


def get_lowest_neighbor_direction(probabilities, row, col):
    """
    Find direction to the lowest probability neighboring cell.
    Returns arrow symbol and the probability difference.
    """
    rows, cols = probabilities.shape
    current_prob = probabilities[row][col]
    min_prob = current_prob
    direction = ''
    
    # Check all 8 adjacent cells
    for dr, dc, arrow in [
        (-1, 0, '↑'), (1, 0, '↓'),    # up, down
        (0, -1, '←'), (0, 1, '→'),    # left, right
        (-1, -1, '↖'), (-1, 1, '↗'),  # diagonals
        (1, -1, '↙'), (1, 1, '↘')
    ]:
        new_row, new_col = row + dr, col + dc
        if (0 <= new_row < rows and 
            0 <= new_col < cols and 
            probabilities[new_row][new_col] < min_prob):
            min_prob = probabilities[new_row][new_col]
            direction = arrow
    
    return direction, current_prob - min_prob

def create_probability_heatmap(probabilities=None, rows=9, cols=9):
    """
    Create a heatmap visualization with arrows pointing to lowest probability neighbors.
    
    Parameters:
    probabilities (numpy.ndarray, optional): Array of probability values
    rows (int): Number of rows if generating sample data
    cols (int): Number of columns if generating sample data
    """
    # Input validation and data generation
    if probabilities is not None:
        if not isinstance(probabilities, np.ndarray):
            probabilities = np.array(probabilities)
        rows, cols = probabilities.shape
    else:
        np.random.seed(42)  # For reproducibility
        # Generate random probabilities with some structure to make it interesting
        x, y = np.mgrid[0:rows, 0:cols]
        probabilities = np.sin(x/3) * np.cos(y/3) * 0.3 + 0.5
        probabilities = np.clip(probabilities, 0, 1)
    
    if np.any(probabilities < 0) or np.any(probabilities > 1):
        raise ValueError("All probabilities must be between 0 and 1")
    
    # Calculate figure size
    base_size = 1.5
    fig_width = max(8, base_size * cols)
    fig_height = max(6, base_size * rows)
    
    # Create figure and axis
    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    
    # Create basic heatmap
    sns.heatmap(probabilities, 
                annot=True,
                fmt='.2f',
                cmap='Reds',
                vmin=0,
                vmax=1,
                square=True,
                cbar_kws={'label': 'Probability'})
    
    # Add direction arrows to each cell
    for row in range(rows):
        for col in range(cols):
            direction, prob_diff = get_lowest_neighbor_direction(
                probabilities, row, col
            )
            if direction:  # Only add arrow if there's a lower probability neighbor
                text = ax.texts[row * cols + col]
                current_text = text.get_text()
                # Add arrow and probability difference
                text.set_text(f'{current_text}\n{direction}')
                
                text.set_size(8 if rows > 5 else 10)
    
    plt.title('Probability Heatmap with Directions to Lowest Neighbors')
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.tight_layout()
    
    return plt

def extract_top_5_locations(data):
    locations = []
    
    # Extract relevant details only for healthcare category
    for category, items in data['places'].items():
        if category == 'healthcare':  # Filter only healthcare-related places
            for place in items:
                # Check if type is related to hospital or medical services
                if place['type'] in ['hospital', 'clinic', 'medical']:
                    location_info = {
                        'distance_meters': place['distance_meters'],
                        'contact': place['contact']['phone'],
                        'address': f"{place['address'].get('street', '')}, "
                                   f"{place['address'].get('city', '')}, "
                                   f"Postcode: {place['address'].get('postcode', '')}"
                    }
                    locations.append({'name': place['name'], 'info': location_info})
    
    # Return only the top 5 locations
    return locations[:5]


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    alert_message = None
    duration = None
    longitude = "-122.1017"  # Default value
    latitude = "40.9234"     # Default value
    locations = []

    if request.method == "POST":
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        start_time = time.time()
        grid_centers = generate_grid(float(latitude), float(longitude), grid_size=3)
        result_grid = []

        for row in grid_centers:
            result_row = []
            for lat, lon in row:
                # Generate the Mapbox image URL for each grid center
                image_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},15,0/350x350?access_token={mapbox_api_key}"
                
                # Download the image for the current grid center
                image_path = "temp_image.jpg"  # Temporary path for each image
                response = requests.get(image_url)
                with open(image_path, "wb") as file:
                    file.write(response.content)

                # Run prediction on the downloaded image
                result, alert_message = predict_image(image_path, lat, lon, False)
                
                # Append results to the row list
                result_row.append(result)

                # Optionally delete the image after prediction to free up space
                os.remove(image_path)

            # Append the row to the result grid
            result_grid.append(result_row) 
        
        print("----------------- Grid Results ------------------")
        print(result_grid)
        print("------------------------------------------------")
        # print(convert_to_numeric(result_grid))
        numeric_grid = convert_to_numeric(result_grid)
        print(numeric_grid)
        norm_grid = [[int(value) / 100 for value in row] for row in numeric_grid]
        print(norm_grid)
        plot = create_probability_heatmap(norm_grid)
        plot.savefig("static/heatmap.png")
        # print(transformed_matrix)

        # Generate the Mapbox image URL
        image_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{longitude},{latitude},15,0/350x350?access_token={mapbox_api_key}"
        info=get_location_info(float(latitude),float(longitude))
        locations = extract_top_5_locations(info)
        print(locations)

        # Download the image
        if "run_demo" in request.form:
            image_path = "static/demo.jpg"
        else:
            image_path = "test.jpg"
            response = requests.get(image_url)
            with open(image_path, "wb") as file:
                file.write(response.content)
        
        # Run prediction on the downloaded image and get the alert message
        result, alert_message = predict_image(image_path,latitude,longitude, True)

        # Calculate the duration
        duration = time.time() - start_time

        # Optionally delete the image after prediction to free up space
        if "run_demo" not in request.form:
            os.remove(image_path)

    return render_template("index.html", result=result, duration=duration, alert_message=alert_message, longitude=longitude, latitude=latitude, locations=locations, mapbox_api_key=mapbox_api_key)



# # Example usage
# center_lat = 37.7749  # Replace with your latitude
# center_lon = -122.4194  # Replace with your longitude
# grid_centers = generate_grid(center_lat, center_lon)

# # Display the grid
# for row in grid_centers:
#     print(row)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
