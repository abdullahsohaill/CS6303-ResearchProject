import os

folder_path = "wc_180-200_initial"

font_sizes = ['12', '18', '24']
word_count_range = "180-200"  

files = sorted(os.listdir(folder_path), key=lambda x: int(''.join(filter(str.isdigit, x))))

sentence_number = 1
for i in range(0, len(files), 3): 
    try:
        # 1. Base font size (12) and base font style (Jameel Noori)
        os.rename(
            os.path.join(folder_path, files[i]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_01_base_{font_sizes[0]}.jpg")
        )

        # 2. Font size 18 and base font style
        os.rename(
            os.path.join(folder_path, files[i + 1]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_02_base_{font_sizes[1]}.jpg")
        )

        # 3. Font size 24 and base font style
        os.rename(
            os.path.join(folder_path, files[i + 2]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_03_base_{font_sizes[2]}.jpg")
        )

    except IndexError:
        print(f"Error: Missing images for sentence number {sentence_number}")
        break

    sentence_number += 1

print("Renaming completed successfully!")
