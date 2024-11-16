import os
import re
import shutil
import pandas as pd

# =========================
# Configuration Parameters
# =========================

# Define the input and output folders
input_folder = "UpdatedWordCount40-60"  # Path to your input images folder
output_folder = "WordCount40-60_Renamed"  # Path to save renamed images

# Define the path for the CSV file
csv_filename = "image_dimensions.csv"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the regex pattern to parse filenames
# This pattern assumes filenames like:
# {word_count_range}_{sentence_number}_{image_sequence}_base_{font_size}_{font_style}.jpg
# or
# {word_count_range}_{sentence_number}_{image_sequence}_base_{font_size}_{font_style}_blur-{blur_level}.jpg
# or
# {word_count_range}_{sentence_number}_{image_sequence}_base_{font_size}_{font_style}_bg-{bg_color_hex}.jpg
# Adjusted regex pattern to support color names and decimal blur levels
filename_pattern = re.compile(
    r"""^(?P<word_count_range>\d+-\d+)_                  # Word count range (e.g., 40-60)
        (?P<sentence_number>\d+)_                         # Sentence number (e.g., 1)
        (?P<image_sequence>\d+)_                          # Image sequence (e.g., 01)
        base_                                             # Literal 'base_'
        (?P<font_size>\d+)_                               # Font size (e.g., 12)
        (?P<font_style>[^_]+(?: [^_]+)*)                 # Font style (e.g., Jameel Noori Nastaleeq)
        (?:_blur-(?P<blur_level>\d+(?:\.\d+)?))?         # Optional blur level (e.g., blur-1 or blur-1.25)
        (?:_bg-(?P<bg_color_name>[\w-]+))?               # Optional background color (e.g., bg-light_yellow or bg-ADD8E6)
        \.jpg$                                            # File extension
    """,
    re.VERBOSE | re.IGNORECASE,
)


# Initialize a list to hold CSV data
csv_data = []

# Get a sorted list of image filenames
image_filenames = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith(('.jpg', '.jpeg'))
])

# Assign sequential numbers starting from 1
for idx, filename in enumerate(image_filenames, start=1):
    # Match the filename against the regex pattern
    match = filename_pattern.match(filename)
    
    if not match:
        print(f"Filename '{filename}' does not match the expected pattern. Skipping.")
        continue  # Skip files that don't match the pattern

    # Extract matched groups
    word_count_range = match.group('word_count_range')
    sentence_number = match.group('sentence_number')
    image_sequence = match.group('image_sequence')
    font_size = match.group('font_size')
    font_style = match.group('font_style').strip()  # Remove any leading/trailing spaces
    blur_level = match.group('blur_level') or '0'  # Set to '0' if not present
    bg_color_name = match.group('bg_color_name') or '0'  # Set to '0' if not present

    # Define the new image name
    new_img = f"{idx}"
    new_image_name = f"{idx}.jpg"

    # Define source and destination paths
    src_path = os.path.join(input_folder, filename)
    dest_path = os.path.join(output_folder, new_image_name)

    try:
        # Copy the image to the output folder with the new name
        shutil.copyfile(src_path, dest_path)
    except Exception as e:
        print(f"Error copying '{filename}' to '{new_image_name}': {e}")
        continue  # Skip to the next file in case of error

    # Append the data to the CSV list
    csv_data.append({
        "Image": new_img,
        "Original Name": filename,  # New column for original filename
        "Word Count Range": word_count_range,
        "Sentence Number": sentence_number,
        "Image Sequence": image_sequence,
        "Font Size": font_size,
        "Font Style": font_style,
        "Blur Level": blur_level,
        "Background Color": bg_color_name  # updated variable name
    })


    # Optional: Print progress
    if idx % 10 == 0 or idx == len(image_filenames):
        print(f"Processed {idx} / {len(image_filenames)} images.")

# Create a pandas DataFrame from the CSV data
df = pd.DataFrame(csv_data, columns=[
    "Image",
    "Original Name",
    "Word Count Range",
    "Sentence Number",
    "Image Sequence",
    "Font Size",
    "Font Style",
    "Blur Level",
    "Background Color"
])

# Save the DataFrame to a CSV file
csv_path = os.path.join(output_folder, csv_filename)
df.to_csv(csv_path, index=False)

print(f"\nCSV file '{csv_filename}' has been created in the '{output_folder}' folder.")
print("All images have been renamed and copied to the output folder.")
