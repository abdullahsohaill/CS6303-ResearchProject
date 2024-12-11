from PIL import Image, ImageFilter, ImageColor
import os

input_folder = "wc_40-60_initial"
output_folder = "wc_40-60_blur"
os.makedirs(output_folder, exist_ok=True)

blur_levels = [0.75, 1.5]
background_colors = {
    "slate_gray": "#708090", 
    "light_yellow": "#FFFACD"
}
BACKGROUND_THRESHOLD = 240

for filename in os.listdir(input_folder):
    if "base_18" in filename and filename.lower().endswith(('.jpg', '.jpeg')):
        try:
            image_path = os.path.join(input_folder, filename)
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert("RGB")

            # Apply blur levels and save with descriptive names
            for blur_level in blur_levels:
                blurred_img = img.filter(ImageFilter.GaussianBlur(blur_level))
                base_name, ext = os.path.splitext(filename)
                new_filename = f"{base_name}_blur-{blur_level}{ext}"
                blurred_img.save(os.path.join(output_folder, new_filename))
                print(f"Saved blurred image: {new_filename}")

            # Apply background colors and save with color names
            for color_name, hex_code in background_colors.items():
                img_bg = img.copy()
                pixels = img_bg.load()
                bg_rgb = ImageColor.getrgb(hex_code)

                for y in range(img_bg.height):
                    for x in range(img_bg.width):
                        r, g, b = pixels[x, y]
                        if r > BACKGROUND_THRESHOLD and g > BACKGROUND_THRESHOLD and b > BACKGROUND_THRESHOLD:
                            pixels[x, y] = bg_rgb

                new_filename = f"{base_name}_bg-{color_name}{ext}"
                img_bg.save(os.path.join(output_folder, new_filename))
                print(f"Saved background-colored image: {new_filename}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")

print("Image modifications completed and saved in the output folder.")
