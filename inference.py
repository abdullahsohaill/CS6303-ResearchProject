# Install necessary packages if not already installed (uncomment to install)
# !pip install openai pandas requests pillow python-dotenv

# Import necessary libraries
import openai
import requests
import base64
import pandas as pd
import os
from io import BytesIO
from PIL import Image
from IPython.display import display, Image as IPythonImage
from dotenv import load_dotenv
from openai import OpenAI 

# Load environment variables from a .env file
load_dotenv()

# Authenticate with the OpenAI API using your API key from an external file
API_key = os.getenv('OPENAI_API_KEY')  # Ensure you have a .env file with OPENAI_API_KEY=your_key
openai.api_key = API_key
client = OpenAI(api_key=API_key)

# Define the system prompt tailored for Urdu OCR tasks
system_prompt = """
As an AI language model specialized in Optical Character Recognition (OCR) for Urdu script, your task is to extract the text from the provided image accurately.

You are required to follow the following instructions:
- Output only the text found in the image.
- Do not add any additional commentary or information.
- Preserve all diacritical marks and nuances of the Urdu script.
- Ensure the transcription is accurate and faithful to the original text.
- Do not translate the text; keep it in Urdu.
"""

# Function to load an image and encode it in Base64
def load_and_encode_image(image_path):
    """
    Loads an image from the specified file path and encodes it in Base64.

    Parameters:
        image_path (str): The file path to the image.

    Returns:
        str: Base64-encoded string of the image.
    """
    try:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        return encoded_image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Function to send the image to GPT-4V and get the OCR result
def perform_ocr(encoded_image, system_prompt):
    """
    Sends the encoded image to the GPT-4V API and returns the OCR result.

    Parameters:
        encoded_image (str): Base64-encoded image string.
        system_prompt (str): The system prompt for the OCR task.

    Returns:
        str: The extracted text from the image.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                {"type": "text", "text": ""},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{encoded_image}"}
                }
            ]}
        ],
            temperature=0.0,
        )
        extracted_text = response.choices[0].message.content
        return extracted_text
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

# Function to process images and update the CSV file
def process_images_and_update_csv(images_folder, csv_file_path, system_prompt):
    """
    Processes images in the specified folder and updates the CSV file with OCR results.

    Parameters:
        images_folder (str): Path to the folder containing images.
        csv_file_path (str): Path to the CSV file to update.
        system_prompt (str): The system prompt for the OCR task.
    """
    # Read the CSV file into a DataFrame
    if os.path.isfile(csv_file_path):
        df = pd.read_csv(csv_file_path)
    else:
        print(f"CSV file {csv_file_path} does not exist.")
        return

    # Initialize 'response' column if it doesn't exist
    # if 'response' not in df.columns:
    #     df['response'] = ''

    # Get list of image files in the folder
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(image_files)
    print(f"Starting OCR processing for {total_images} images.")

    for idx, image_file in enumerate(image_files):
        image_path = os.path.join(images_folder, image_file)
        # Extract image name without extension
        image_name = int(os.path.splitext(image_file)[0])

        encoded_img = load_and_encode_image(image_path)
        if encoded_img:
            extracted_txt = perform_ocr(encoded_img, system_prompt)
            # extracted_txt = "hi"
            if extracted_txt:
                # Find the row in the DataFrame where 'image' matches the image name
                match = df['Image'] == image_name
                # print(image_name)
                if match.any():
                    df.loc[match, 'Response'] = extracted_txt
                else:
                    print(f"Image name {image_name} not found in CSV. Skipping.")
            else:
                print(f"Failed to extract text from {image_file}")
        else:
            print(f"Failed to load {image_file}")

        # Print progress every 50 images
        if (idx + 1) % 50 == 0 or (idx + 1) == total_images:
            print(f"Processed {idx + 1}/{total_images} images.")

    # Save the updated DataFrame back to CSV
    df.to_csv(csv_file_path, index=False)
    print("All images processed successfully. CSV file updated.")

# Specify the images folder and CSV file path
images_folder = 'WordCount40-60_Renamed' # 'images_dataset'  # Replace with your images folder path
csv_file_path = 'inferenced_dataset.csv'  # 'inferenced_set.csv'  # Replace with your CSV file path

# Start processing
process_images_and_update_csv(images_folder, csv_file_path, system_prompt)
