import tkinter as tk
from tkinter import Tk, Label, Entry, Button, Canvas, Scrollbar, Frame, messagebox
from PIL import Image, ImageTk, ImageFilter
import requests
import random
import spotipy
import pygame
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from scipy.spatial.distance import cdist

# API Credentials
SPOTIFY_CLIENT_ID = '85ff204786884864b9e5e44afefef6b7'
SPOTIFY_CLIENT_SECRET = 'fc50fc222100434089251eed0decac25'
PEXELS_API_KEY = "EE2eCMhITUnDs50vcPAVsHLKBIsxa3e8EZi8fczFvE2PhLKInsnci1rr"

# Initialize Spotify and Pygame
spotify_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)
pygame.mixer.init()

root = tk.Tk()
root.title("Music Game")
root.geometry("600x600")

# Create the label_prompt widget globally at the start of the app
label_prompt = Label(root, text="")
label_prompt.pack()
# ------------------------------ BEGINNING - PLAYER COUNT ------------------------------
def open_player_count_window():
    """Open the player count input window."""
    player_count_window = tk.Toplevel(root)
    player_count_window.title("Enter Number of Players")
    player_count_window.geometry("300x200")

    label_prompt = tk.Label(player_count_window, text="How many players are there?")
    label_prompt.pack(pady=20)

    player_count_entry = tk.Entry(player_count_window)
    player_count_entry.pack(pady=5)

    def start_game():
        num_players = player_count_entry.get()
        if num_players.isdigit() and int(num_players) > 0:
            global players
            players = int(num_players)
            print(f"Number of players: {players}")
            player_count_window.destroy()  # Only close the player count window
            open_music_game_window()  # Open the music game window
        else:
            messagebox.showerror("Invalid input", "Please enter a valid number of players.")

    submit_button = tk.Button(player_count_window, text="Start Game", command=start_game)
    submit_button.pack(pady=10)

    player_count_window.grab_set()  # Make this window modal
    player_count_window.wait_window()  # Block until the player count window is closed

# ------------------------------ START GAME & PLAYER TURN FUNCTIONS ------------------------------
def open_music_game_window():
    """Start the main music game and handle player turns."""
    global player_number
    try: 
        player_number = 1  # Start with player 1
        label_prompt.config(text=f"Player {player_number}, please make a submission.")

        # Pack widgets for player input
        entry_song.pack(pady=5)
        button_search.pack(pady=10)
        frame_results.pack(pady=10, fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Set up the background and image
        label_bg.place(relwidth=1, relheight=1)
        display_image_with_gradient_background()

        # Bind mouse events for zoom functionality
        label_image.bind("<Motion>", on_hover)
        label_image.bind("<Leave>", on_leave)
        label_zoom.place_forget()

        print("Music game started successfully.")
        start_player_turns()
    except Exception as e:
        print(f"Error starting music game: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def start_player_turns():
    """Start the current player's turn to select a song."""
    if player_number <= players:
        label_prompt.config(text=f"Player {player_number}, please make a submission.")
        entry_song.config(state="normal")  # Allow player to input song name
        button_search.config(state="normal")  # Enable song search functionality

        def on_submission():
            song_name = entry_song.get()
            if song_name:
                messagebox.showinfo("Submission Received", f"Player {player_number} submitted: {song_name}")
                entry_song.delete(0, tk.END)  # Clear input field
                player_turn_complete()  # Proceed after the current player has confirmed their submission
            else:
                messagebox.showwarning("Input Required", "Please enter a song name.")

        submit_button = tk.Button(root, text="CONFIRM", command=on_submission)
        submit_button.pack(pady=10)
    else:
        messagebox.showinfo("All Players Submitted", "All players have made their submissions!")
        # Proceed to the next phase of the game
        judging_phase()

def player_turn_complete():
    """Move to the next player's turn."""
    global player_number
    player_number += 1
    if player_number <= players:
        start_player_turns()  # Continue with the next player's turn
    else:
        messagebox.showinfo("Game Over", "All players have made their submissions!")
        judging_phase()  # Proceed to the next phase once all players have completed

def judging_phase():
    """Proceed to the next phase of the game after all players have submitted their songs."""
    # Add code for the next phase of the game (e.g., comparing songs, scoring, etc.)
    pass

# ------------------------------ Helper Functions ------------------------------

def fetch_random_image():
    """Fetch a random image from the Pexels API."""
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
    image = image.resize((100, 100))
    np_image = np.array(image)
    avg_color = np.mean(np_image.reshape(-1, 3), axis=0).astype(int)
    dominant_color = tuple(avg_color)
    
    background = Image.new("RGB", (root.winfo_screenwidth(), root.winfo_screenheight()), dominant_color)
    blurred_background = background.filter(ImageFilter.GaussianBlur(radius=30))
    
    return blurred_background

def create_gradient_background(color1, color2):
    """Create a gradient background using two colors."""
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    gradient_image = Image.new("RGB", (width, height))
    for y in range(height):
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
    
    if len(sorted_colors) >= 2:
        distances = cdist(np.array(sorted_colors), np.array(sorted_colors), metric='euclidean')
        np.fill_diagonal(distances, 0)
        max_index = np.unravel_index(np.argmax(distances), distances.shape)
        return sorted_colors[max_index[0]], sorted_colors[max_index[1]]
    else:
        return sorted_colors[0], sorted_colors[0]

def create_gradient_from_most_contrasting_colors(image_path):
    """Generate a gradient using the two most contrasting colors from an image."""
    color1, color2 = find_two_most_contrasting_colors(image_path)
    gradient_bg = create_gradient_background(color1, color2)
    return gradient_bg

# ------------------------------ GUI Functions ------------------------------

def display_image_with_gradient_background():
    global img, original_image
    image_path = fetch_random_image()
    if image_path:
        original_image = Image.open(image_path)
        gradient_bg = create_gradient_from_most_contrasting_colors(image_path)
        gradient_bg = ImageTk.PhotoImage(gradient_bg)
        label_bg.config(image=gradient_bg)
        label_bg.image = gradient_bg

        max_width, max_height = 400, 300
        original_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(original_image)
        label_image.config(image=img)
        label_image.image = img
    else:
        label_image.config(text="Failed to load image")

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
                preview_url = track.get('preview_url')
                output += f"{idx + 1}. {track_name} by {artist_name}\nURL: {spotify_url}\n\n"

                if preview_url:
                    has_preview = True
                    play_button = Button(scrollable_frame, text=f"Play {track_name}",
                                          command=lambda url=preview_url: play_preview(url))
                    play_button.pack(pady=5)

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
        response = requests.get(preview_url)
        if response.status_code == 200 and response.content:
            with open("preview.mp3", "wb") as f:
                f.write(response.content)
            
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

# Mouse event functions for zoom
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

# ------------------------------ GUI Setup ------------------------------

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

canvas_results = Canvas(scrollable_frame, bg=scrollable_frame["bg"], bd=0, highlightthickness=0)
canvas_results.pack(fill="both", expand=True)

# Update the results text
def update_results_text(text):
    canvas_results.delete("all")  # Clear previous text
    canvas_results.create_text(10, 10, anchor="nw", text=text, fill="black", width=500)

update_results_text("Type a song here")

# Mouse wheel event handler
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

# Start by opening the player count window
open_player_count_window()

# Run the main application loop
root.mainloop()