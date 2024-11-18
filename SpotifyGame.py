import requests
import random
import os
from tkinter import Tk, Label, Entry, Button, filedialog, PhotoImage
from PIL import Image, ImageTk  # For displaying images in Tkinter
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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
    # Pexels API URL and parameters
    url = "https://api.pexels.com/v1/search"
    queries = ["nature", "space", "people", "epic", "cinematic", "thrilling", "party", "fighting", "angry", "sad", "creepy", "car"]
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

def display_image():
    image_path = fetch_random_image()
    if image_path:
        img = Image.open(image_path)
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        label_image.config(image=img)
        label_image.image = img
    else:
        label_image.config(text="Failed to load image")

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

# GUI setup
root = Tk()
root.title("Random Image & Spotify Search")
root.geometry("600x600")

# Image Display Label
label_image = Label(root)
label_image.pack(pady=10)
display_image()

# Song Search Input
label_prompt = Label(root, text="Enter a song to search:")
label_prompt.pack()
entry_song = Entry(root, width=40)
entry_song.pack(pady=5)

# Search Button
button_search = Button(root, text="Search Song", command=search_song)
button_search.pack(pady=10)

# Results Label
label_results = Label(root, text="", justify="left", wraplength=500)
label_results.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
