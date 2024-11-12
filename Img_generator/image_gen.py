import os

folder_path = "WordCount40-60"

font_sizes = ['12', '18', '24']
font_styles = ['Jameel Noori Nastaleeq', 'Alvi Nastaleeq', 'Nafees Nastaleeq']
word_count_range = "40-60"  

files = sorted(os.listdir(folder_path), key=lambda x: int(''.join(filter(str.isdigit, x))))

sentence_number = 1
for i in range(0, len(files), 5): 
    try:
        # 1. Base font size (12) and base font style (Jameel Noori)
        os.rename(
            os.path.join(folder_path, files[i]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_01_base_{font_sizes[0]}_{font_styles[0]}.jpg")
        )

        # 2. Font size 18 and base font style
        os.rename(
            os.path.join(folder_path, files[i + 1]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_02_base_{font_sizes[1]}_{font_styles[0]}.jpg")
        )

        # 3. Font size 24 and base font style
        os.rename(
            os.path.join(folder_path, files[i + 2]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_03_base_{font_sizes[2]}_{font_styles[0]}.jpg")
        )

        # 4. Base font size and font style Alvi Nastaleeq
        os.rename(
            os.path.join(folder_path, files[i + 3]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_04_base_{font_sizes[1]}_{font_styles[1]}.jpg")
        )

        # 5. Base font size and font style Nafees Nastaleeq
        os.rename(
            os.path.join(folder_path, files[i + 4]),
            os.path.join(folder_path, f"{word_count_range}_{sentence_number}_05_base_{font_sizes[1]}_{font_styles[2]}.jpg")
        )

    except IndexError:
        print(f"Error: Missing images for sentence number {sentence_number}")
        break

    sentence_number += 1

print("Renaming completed successfully!")
