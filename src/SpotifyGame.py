from tkinter import Tk, Label, Entry, Button, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk, ImageFilter
import requests
import random
import spotipy
import pygame
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from scipy.spatial.distance import cdist

### THIS IS A TEST TO SEE IF IT WORKS ###

# Spotify API Credentials
SPOTIFY_CLIENT_ID = '85ff204786884864b9e5e44afefef6b7'
SPOTIFY_CLIENT_SECRET = 'fc50fc222100434089251eed0decac25'

# Pexels API Key
PEXELS_API_KEY = "EE2eCMhITUnDs50vcPAVsHLKBIsxa3e8EZi8fczFvE2PhLKInsnci1rr"

# Spotify Authentication
spotify_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)

#Pygame is used for sound
pygame.mixer.init()

def fetch_random_image():
    url = "https://api.pexels.com/v1/search"
    queries = ["nature", "space", "people", "epic", "cinematic", "thrilling", "party", "fighting", 
               "angry", "sad", "creepy", "car", "fantasy"]
    query = random.choice(queries)
    params = {"query": query, "per_page": 1000, "page": random.randint(1, 20)}
    headers = {"Authorization": PEXELS_API_KEY}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("photos"):
            random_image = random.choice(data["photos"])
            image_url = random_image["src"]["original"]
            image_data = requests.get(image_url).content
            with open("random_pexels_image.jpg", "wb") as f:
                f.write(image_data)
            return "random_pexels_image.jpg"
    return None

def create_blurred_background(image_path):
    """Create a blurred background using the dominant color of the image."""
    image = Image.open(image_path)
    
    # Resize image to speed up processing (optional)
    image = image.resize((100, 100))
    
    # Convert image to numpy array and get the dominant color
    np_image = np.array(image)
    avg_color = np.mean(np_image.reshape(-1, 3), axis=0).astype(int)
    dominant_color = tuple(avg_color)
    
    # Create a solid color image with the dominant color
    background = Image.new("RGB", (root.winfo_screenwidth(), root.winfo_screenheight()), dominant_color)
    
    # Apply Gaussian blur
    blurred_background = background.filter(ImageFilter.GaussianBlur(radius=30))
    
    return blurred_background

def create_gradient_background(color1, color2):
    """Create a gradient background using two colors."""
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    gradient_image = Image.new("RGB", (width, height))
    for y in range(height):
        # Interpolate between color1 and color2
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        for x in range(width):
            gradient_image.putpixel((x, y), (r, g, b))
    return gradient_image

def find_two_most_contrasting_colors(image_path):
    """Find two most contrasting colors from an image."""
    image = Image.open(image_path).resize((100, 100))
    np_image = np.array(image).reshape(-1, 3)
    unique_colors, counts = np.unique(np_image, axis=0, return_counts=True)
    sorted_colors = [tuple(map(int, color)) for color in unique_colors[np.argsort(-counts)]]
    
    # Find the two colors with the maximum contrast (Euclidean distance)
    if len(sorted_colors) >= 2:
        distances = cdist(np.array(sorted_colors), np.array(sorted_colors), metric='euclidean')
        np.fill_diagonal(distances, 0)  # Ignore self-distances
        max_index = np.unravel_index(np.argmax(distances), distances.shape)
        return sorted_colors[max_index[0]], sorted_colors[max_index[1]]
    else:
        # Fallback in case there are fewer colors
        return sorted_colors[0], sorted_colors[0]

def create_gradient_from_most_contrasting_colors(image_path):
    """Generate a gradient using the two most contrasting colors from an image."""
    color1, color2 = find_two_most_contrasting_colors(image_path)
    gradient_bg = create_gradient_background(color1, color2)
    return gradient_bg

def display_image_with_gradient_background():
    global img, original_image
    image_path = fetch_random_image()
    if image_path:
        original_image = Image.open(image_path)
        
        # Create and display gradient background
        gradient_bg = create_gradient_from_most_contrasting_colors(image_path)
        gradient_bg = ImageTk.PhotoImage(gradient_bg)
        label_bg.config(image=gradient_bg)
        label_bg.image = gradient_bg

        # Resize and display the main image on top
        max_width, max_height = 400, 300
        original_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(original_image)
        label_image.config(image=img)
        label_image.image = img
    else:
        label_image.config(text="Failed to load image")

def on_hover(event):
    """Display zoomed-in view when the mouse hovers over the image."""
    if original_image:
        x, y = event.x, event.y
        zoom_size = 100  # Size of the zoomed region

        # Calculate cropping box for the zoomed region
        left = max(0, x - zoom_size // 2)
        top = max(0, y - zoom_size // 2)
        right = min(original_image.width, x + zoom_size // 2)
        bottom = min(original_image.height, y + zoom_size // 2)

        # Crop and resize the zoomed region for display
        zoomed_region = original_image.crop((left, top, right, bottom))
        zoomed_region = zoomed_region.resize((200, 200), Image.Resampling.LANCZOS)
        zoomed_img = ImageTk.PhotoImage(zoomed_region)

        # Update the zoomed label
        label_zoom.config(image=zoomed_img)
        label_zoom.image = zoomed_img
        label_zoom.place(x=event.x_root - root.winfo_rootx() + 20, y=event.y_root - root.winfo_rooty() + 20)

def on_leave(event):
    """Hide the zoomed-in view when the mouse leaves the image."""
    label_zoom.place_forget()

def search_song():
    song_name = entry_song.get()
    if song_name:
        results = sp.search(q=song_name, type='track', limit=15)
        tracks = results['tracks']['items']
        if tracks:
            has_preview = False
            output = ""
            for idx, track in enumerate(tracks):
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                spotify_url = track['external_urls']['spotify']
                preview_url = track.get('preview_url')  # Get the preview URL

                output += f"{idx + 1}. {track_name} by {artist_name}\nURL: {spotify_url}\n\n"

                # Create play button only if a preview URL exists
                if preview_url:
                    has_preview = True
                    play_button = Button(scrollable_frame, text=f"Play {track_name}",
                                          command=lambda url=preview_url: play_preview(url))
                    play_button.pack(pady=5)  # Add padding between buttons

            update_results_text(output)
            
            if not has_preview:
                update_results_text(output + "\nNo tracks with previews available.")
        else:
            update_results_text(text="No tracks found.")
    else:
        update_results_text(text="Please enter a song name.")

def play_preview(preview_url):
    """Play the song preview when the button is clicked."""
    try:
        # Download the MP3 file from the preview URL
        response = requests.get(preview_url)
        if response.status_code == 200 and response.content:
            with open("preview.mp3", "wb") as f:
                f.write(response.content)
            
            # Load the downloaded file and play it
            pygame.mixer.music.load("preview.mp3")
            pygame.mixer.music.play()
        else:
            print(f"Failed to download or invalid file: {response.status_code}")
    except Exception as e:
        print(f"Error playing preview: {e}")

def stop_preview():
    """Stop the preview audio."""
    pygame.mixer.music.stop()

def next_picture():
    display_image_with_gradient_background()

# GUI setup
root = Tk()
root.title("Random Image & Spotify Search")
root.geometry("600x600")

# Background Display Label
label_bg = Label(root)
label_bg.place(relwidth=1, relheight=1)  # Cover the entire window

# Image Display Label (on top of the background)
label_image = Label(root)
label_image.pack(pady=10)
display_image_with_gradient_background()

# Bind mouse events for zoom functionality
label_image.bind("<Motion>", on_hover)
label_image.bind("<Leave>", on_leave)

# Zoom display label (initially hidden)
label_zoom = Label(root)
label_zoom.place_forget()

# "Next Picture" Button
button_next = Button(root, text="Next Picture", command=next_picture)
button_next.pack(pady=10)

# Song Search Input
label_prompt = Label(root, text="Enter a song to search:")
label_prompt.pack()
entry_song = Entry(root, width=40)
entry_song.pack(pady=5)

# Search Button
button_search = Button(root, text="Search Song", command=search_song)
button_search.pack(pady=10)

# Scrollable Music Results
frame_results = Frame(root)
frame_results.pack(pady=10, fill="both", expand=True)

canvas = Canvas(frame_results)
scrollbar = Scrollbar(frame_results, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Replace Label with Canvas text for better blending
canvas_results = Canvas(scrollable_frame, bg=scrollable_frame["bg"], bd=0, highlightthickness=0)
canvas_results.pack(fill="both", expand=True)

# Function to update the results (simulating `label_results` behavior)
def update_results_text(text):
    canvas_results.delete("all")  # Clear previous text
    canvas_results.create_text(10, 10, anchor="nw", text=text, fill="black", width=500)

# Use the `update_results_text` function to display search results
update_results_text("Type a song here")

# Function to handle mouse wheel scrolling
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

# Bind mouse wheel events
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

# Run the Tkinter event loop
root.mainloop()
