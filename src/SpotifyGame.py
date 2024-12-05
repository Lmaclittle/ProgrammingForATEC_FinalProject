import tkinter as tk
from tkinter import Tk, Label, Entry, Button, Canvas, Scrollbar, Frame, messagebox, Listbox
from PIL import Image, ImageTk, ImageFilter
import requests
import random
import spotipy
import pygame
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from scipy.spatial.distance import cdist
from io import BytesIO

# API Credentials
SPOTIFY_CLIENT_ID = '85ff204786884864b9e5e44afefef6b7'
SPOTIFY_CLIENT_SECRET = 'fc50fc222100434089251eed0decac25'
PEXELS_API_KEY = "EE2eCMhITUnDs50vcPAVsHLKBIsxa3e8EZi8fczFvE2PhLKInsnci1rr"

# Initialize Spotify and Pygame
spotify_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)
pygame.mixer.init()

root = tk.Tk()
root.title("Music Vibe Game")
root.geometry("600x700")

# Create the label_prompt widget globally at the start of the app
label_prompt = Label(root, text="")
label_prompt.pack()

track_data = []
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
def confirm_submission():
    """Function to handle confirming the song submission."""
    song_name = entry_song.get()
    if song_name:
        messagebox.showinfo("Song Confirmed", f"Player {player_number} confirmed: {song_name}")
        entry_song.delete(0, tk.END)  # Clear input field
        player_turn_complete()  # Proceed to the next player's turn
    else:
        messagebox.showwarning("Input Required", "Please enter a song name to confirm.")

    confirm_button.config(text="CONFIRM", command=confirm_submission)


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

def on_submission():
            song_name = entry_song.get()
            if song_name:
                messagebox.showinfo("Submission Received", f"Player {player_number} submitted: {song_name}")
                entry_song.delete(0, tk.END)  # Clear input field
                confirm_button.place_forget()  # Hide the confirm button after submission
                player_turn_complete()  # Proceed after the current player has confirmed their submission
            else:
                messagebox.showwarning("Input Required", "Please enter a song name to confirm.")

def start_player_turns():
    """Start the current player's turn to select a song."""
    if player_number <= players:
        label_prompt.config(text=f"Player {player_number}, please make a submission.")
        entry_song.config(state="normal")  # Allow player to input song name
        button_search.config(state="normal")  # Enable song search functionality
        # Confirm Button (global to avoid duplication)
        confirm_button.config(text="CONFIRM", command=on_submission)  # Link the CONFIRM button to the on_submission function
        confirm_button.pack(pady=10)  # Show the button
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
    """Search for songs on Spotify and populate the Listbox with results."""
    song_name = entry_song.get()
    if song_name:
        # Clear old results and album image
        results_listbox.delete(0, tk.END)  # Clear the Listbox
        label_album_image.place_forget()  # Hide the album image
        track_data.clear()  # Reset the track data

        # Perform the new search
        results = sp.search(q=song_name, type='track', limit=15)
        tracks = results['tracks']['items']
        if tracks:
            for idx, track in enumerate(tracks):
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                results_listbox.insert(tk.END, f"{track_name} by {artist_name}")

                # Store track data for future use (including album art URL)
                track_data.append({
                    'name': track_name,
                    'artist': artist_name,
                    'album_image_url': track['album']['images'][0]['url']  # Fetch the largest image
                })
        else:
            messagebox.showinfo("No Results", "No tracks found for the search query.")
    else:
        messagebox.showwarning("Empty Query", "Please enter a song name.")


def on_song_select(event):
    """Display the album image of the selected song."""
    selected_idx = results_listbox.curselection()
    if selected_idx:
        track_data_idx = selected_idx[0]
        album_image_url = track_data[track_data_idx]['album_image_url']
        selected_song = f"{track_data[track_data_idx]['name']} by {track_data[track_data_idx]['artist']}"

        # Automatically fill the entry field with the selected song
        entry_song.delete(0, tk.END)  # Clear any existing text
        entry_song.insert(0, selected_song)  # Insert the selected song into the entry field
        confirm_button.config(state="normal")  # Enable the confirm button once a song is selected

        # Download and display the image
        response = requests.get(album_image_url)
        if response.status_code == 200:
            album_image = Image.open(BytesIO(response.content))

            # Set the desired maximum size for the album cover
            max_width = 150  # Adjust this value to make the image smaller or larger
            max_height = 150  # Adjust this value to control the height

            # Resize the image to fit within the desired dimensions
            album_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            album_img = ImageTk.PhotoImage(album_image)
            label_album_image.config(image=album_img)
            label_album_image.image = album_img

            # Position the album image to overlap the listbox
            label_album_image.place(x=root.winfo_width() - album_image.width - 10, y=results_listbox.winfo_y() + 300)  # Overlapping position

        else:
            print(f"Failed to load image: {response.status_code}")


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

label_album_image = Label(root)
label_album_image.place_forget()  # Initially hide the label

# Bind mouse events for zoom functionality
label_image.bind("<Motion>", on_hover)
label_image.bind("<Leave>", on_leave)

# Zoom display label (initially hidden)
label_zoom = Label(root)
label_zoom.place_forget()

# Song Search Input
label_prompt = Label(root, text="Enter a song to search:")
label_prompt.pack()
entry_song = Entry(root, width=40)
entry_song.pack(pady=5)

# Search Button
button_search = Button(root, text="Search Song", command=search_song)
button_search.pack(pady=10)

# Confirm Button (global to avoid duplication)
confirm_button = Button(root, text="CONFIRM")
confirm_button.pack(pady=10)
confirm_button.place_forget()  # Initially hide the button

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

# Song Results Listbox
results_listbox = Listbox(scrollable_frame, selectmode="browse", height=15)
results_listbox.pack(pady=10, fill="both", expand=True)
# Dynamically update the width of the Listbox based on the root window size
def update_listbox_width(event):
    results_listbox.config(width=root.winfo_width())
    results_listbox.bind("<ButtonRelease-1>", on_song_select)


# Bind the resizing event of the root window
root.bind("<Configure>", update_listbox_width)

# Mouse wheel event handler
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

# Start by opening the player count window
open_player_count_window()

# Run the main application loop
root.mainloop()