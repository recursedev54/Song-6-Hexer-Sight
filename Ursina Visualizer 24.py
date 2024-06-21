from ursina import *
import time
import librosa
import numpy as np
import hashlib

# Function to generate colors based on audio file contents
def generate_colors(audio_data):
    # Compute the hash of the audio file's contents
    audio_hash = hashlib.md5(audio_data).hexdigest()

    # Use the hash value as the seed for random number generation
    np.random.seed(int(audio_hash[:8], 16))

    # Generate random colors
    num_colors = 6
    random_colors = [np.random.randint(0, 256, 3) for _ in range(num_colors)]

    # Convert RGB values to hexadecimal format
    hex_colors = ['#' + ''.join(f'{c:02x}' for c in color) for color in random_colors]

    return hex_colors

# Function to invert hex colors
def invert_hex_color(hex_color):
    inverted_color = '#{:02x}{:02x}{:02x}'.format(
        255 - int(hex_color[1:3], 16),
        255 - int(hex_color[3:5], 16),
        255 - int(hex_color[5:7], 16)
    )
    return inverted_color

# Load the audio file using librosa
audio_file = 'june.wav'
y, sr = librosa.load(audio_file)

# Calculate the tempo (BPM)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
beat_duration = 60.0 / tempo  # Duration of a beat in seconds

# Generate beat timings based on the calculated tempo
# Calculate the duration of the song
song_duration = librosa.get_duration(y=y, sr=sr)
beat_timings = [i * beat_duration for i in range(int(song_duration // beat_duration) + 1)]

# Get the audio file contents as bytes
with open(audio_file, "rb") as f:
    audio_data = f.read()

# Generate colors based on the audio file contents
colors = generate_colors(audio_data)
# Generate inverted colors
inverted_colors = [invert_hex_color(color) for color in colors]

# Define the Ursina app
app = Ursina()

# Set up the window
window.title = 'Music-Beat Swirl Game'
window.borderless = False
window.exit_button.visible = True
window.fps_counter.enabled = True

# Define the background color
camera.background_color = color.black

# Create a parent entity to rotate the entire shape
parent_entity = Entity()

# Create the left half of the rectangle that will change color with a rhythm
left_half = Entity(parent=parent_entity, model=Mesh(vertices=[Vec3(-1, -0.5, 0), Vec3(0, -0.5, 0), Vec3(0, 0.5, 0), Vec3(-1, 0.5, 0)], triangles=[(0, 1, 2), (2, 3, 0)]), color=color.white, scale=(20, 20, 1), position=(0, 0, 0))

# Create the right half of the rectangle that will change color with inverted colors
right_half = Entity(parent=parent_entity, model=Mesh(vertices=[Vec3(0, -0.5, 0), Vec3(1, -0.5, 0), Vec3(1, 0.5, 0), Vec3(0, 0.5, 0)], triangles=[(0, 1, 2), (2, 3, 0)]), color=color.white, scale=(20, 20, 1), position=(0, 0, 0))

# Adding the music file to be played
audio = Audio('june.wav', loop=True, autoplay=True)

# Variable to specify the delay before the animation should begin (in seconds)
animation_start_delay = 0.0  # Adjust this value as needed

# Define the start time
start_time = time.time()

# Define the function to change color on the beat
def change_color_on_beat():
    current_time = time.time() - start_time - animation_start_delay
    if current_time < 0:
        return  # Do not start the animation before the delay
    for beat in beat_timings:
        if abs(current_time - beat) < 0.1:
            color_index = int(np.mod(current_time // beat_duration, len(colors)))
            left_half.color = color.hex(colors[color_index])
            right_half.color = color.hex(inverted_colors[color_index])
            break

# Update function to be called every frame
def update():
    change_color_on_beat()
    parent_entity.rotation_z += 0.5

# Run the Ursina app
app.run()
