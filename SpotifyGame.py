from tkinter import Tk, Label, Entry, Button, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk, ImageFilter
import requests
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np

# Spotify API Credentials
SPOTIFY_CLIENT_ID = '85ff204786884864b9e5e44afefef6b7'
SPOTIFY_CLIENT_SECRET = 'fc50fc222100434089251eed0decac25'

# Pexels API Key
PEXELS_API_KEY = "EE2eCMhITUnDs50vcPAVsHLKBIsxa3e8EZi8fczFvE2PhLKInsnci1rr"

# Spotify Authentication
spotify_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)

def fetch_random_image():
    url = "https://api.pexels.com/v1/search"
    queries = ["nature", "space", "people", "epic", "cinematic", "thrilling", "party", "fighting", 
               "angry", "sad", "creepy", "car", "fantasy"]
    query = random.choice(queries)
    params = {"query": query, "per_page": 1000, "page": 1-20}
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

def display_image_with_blurred_background():
    global img, original_image
    image_path = fetch_random_image()
    if image_path:
        original_image = Image.open(image_path)

        # Create and display blurred background
        blurred_bg = create_blurred_background(image_path)
        blurred_bg = ImageTk.PhotoImage(blurred_bg)
        label_bg.config(image=blurred_bg)
        label_bg.image = blurred_bg

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
        results = sp.search(q=song_name, type='track', limit=5)
        tracks = results['tracks']['items']
        if tracks:
            output = ""
            for idx, track in enumerate(tracks):
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                spotify_url = track['external_urls']['spotify']
                output += f"{idx + 1}. {track_name} by {artist_name}\nURL: {spotify_url}\n\n"
            label_results.config(text=output)
        else:
            label_results.config(text="No tracks found.")
    else:
        label_results.config(text="Please enter a song name.")

def next_picture():
    display_image_with_blurred_background()

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
display_image_with_blurred_background()

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

label_results = Label(scrollable_frame, text="", justify="left", wraplength=500)
label_results.pack()

# Function to handle mouse wheel scrolling
def _on_mouse_wheel(event):
    """Scroll canvas with the mouse wheel."""
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Bind mouse wheel events
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

# Run the Tkinter event loop
root.mainloop()
