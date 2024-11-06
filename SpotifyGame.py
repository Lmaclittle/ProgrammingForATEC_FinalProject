import requests
import random
import os

# Pexels API key
API_KEY = "EE2eCMhITUnDs50vcPAVsHLKBIsxa3e8EZi8fczFvE2PhLKInsnci1rr"

# Pexels API URL
url = "https://api.pexels.com/v1/search"

# List of different queries (you can expand this list with more search terms)
queries = ["nature", "space", "people", "epic", "cinematic", "thrilling", "party", "fighting", "angry", "sad", "creepy", "car"]

# Randomly select a query from the list
query = random.choice(queries)

# Parameters for the request
params = {
    "query": query,  # Randomly selects a query
    "per_page": 1000,      # Number of images to fetch
    "page": 1-20,
}

# Headers with the API key
headers = {
    "Authorization": API_KEY
}

# Send a GET request to the Pexels API
response = requests.get(url, headers=headers, params=params)

# Check if the response is successful (status code 200)
if response.status_code == 200:
    try:
        # Try parsing the JSON response
        data = response.json()
        
        # Check if there are any photos in the results
        if data.get("photos"):
            # Randomly select an image from the results
            random_image = random.choice(data["photos"])

            # Get the image URL
            image_url = random_image["src"]["original"]
            print(f"Selected Image URL: {image_url}")

            # Download and save the selected image
            image_data = requests.get(image_url).content
            with open("random_pexels_image.jpg", "wb") as f:
                f.write(image_data)
            print("Image downloaded and saved as 'random_pexels_image.jpg'")
        else:
            print("No images found.")
    except ValueError:
        # Handle JSON decoding error
        print("Error decoding JSON response. Response content:")
        print(response.text)
else:
    # If the request was unsuccessful, print the status code and content
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print(response.text)
