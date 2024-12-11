import os
import re
import shutil
import pandas as pd

# =========================
# Configuration Parameters
# =========================

# Define the input and output folders
input_folder = "combined_dataset"  # Path to your input images folder
output_folder = "FINAL_DATASET"  # Path to save renamed images
true_labels_folder = "true_labels"  # Folder containing true_labels text files

# Define the path for the CSV file
csv_filename = "albanian_combined_articles.csv"


# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the regex pattern to parse filenames
filename_pattern = re.compile(
    r"""^(?P<word_count_range>\d+-\d+)_                  # Word count range (e.g., 40-60)
        (?P<article_number>\d+)_                         # Article number (e.g., 1)
        (?P<image_sequence>\d+)_                         # Image sequence (e.g., 01)
        base_                                             # Literal 'base_'
        (?P<font_size>\d+)                                # Font size (e.g., 12)
        (?:_blur-(?P<blur_level>\d+(?:\.\d+)?))?          # Optional blur level (e.g., blur-1 or blur-1.25)
        (?:_bg-(?P<bg_color_name>[\w-]+))?                # Optional background color (e.g., bg-light_yellow or bg-ADD8E6)
        \.jpg$                                            # File extension
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Read true labels from text files into a dictionary
true_labels = {}
for word_count_range, filename in [
    ("40-60", "true_labels_40-60.txt"),
    ("110-130", "true_labels_110-130.txt"),
    ("180-200", "true_labels_180-200.txt"),
]:
    true_labels_file = os.path.join(true_labels_folder, filename)
    with open(true_labels_file, "r", encoding="utf-8") as file:
        # Split articles by blank lines
        articles = file.read().strip().split('\n\n')
        true_labels[word_count_range] = [article.strip() for article in articles]


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
    article_number = int(match.group('article_number'))  # Convert to int for indexing
    image_sequence = match.group('image_sequence')
    font_size = match.group('font_size')
    blur_level = match.group('blur_level') or '0'  # Set to '0' if not present
    bg_color_name = match.group('bg_color_name') or 'white'  # Set to 'white' if not present

    # Fetch the true label for this article
    try:
        true_label = true_labels[word_count_range][article_number - 1]  # Adjust 1-based index
    except IndexError:
        print(f"Invalid article number {article_number} for word count range {word_count_range}. Skipping.")
        continue

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
        "Article Number": article_number,
        "Image Sequence": image_sequence,
        "Font Size": font_size,
        "Blur Level": blur_level,
        "Background Color": bg_color_name,
        "True Labels": true_label  # Add the true label for this image
    })

    # Optional: Print progress
    if idx % 10 == 0 or idx == len(image_filenames):
        print(f"Processed {idx} / {len(image_filenames)} images.")

# Create a pandas DataFrame from the CSV data
df = pd.DataFrame(csv_data, columns=[
    "Image",
    "Original Name",
    "Word Count Range",
    "Article Number",
    "Image Sequence",
    "Font Size",
    "Blur Level",
    "Background Color",
    "True Labels"  # Add the True Labels column to the CSV
])

# Save the DataFrame to a CSV file
csv_path = os.path.join(output_folder, csv_filename)
df.to_csv(csv_path, index=False)

print(f"\nCSV file '{csv_filename}' has been created in the '{output_folder}' folder.")
print("All images have been renamed and copied to the output folder.")
