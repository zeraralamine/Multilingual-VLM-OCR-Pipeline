import os
import re
from PIL import Image

def split_double_column_images(input_folder, output_folder):
    """
    Solves VLM bounding-box collisions by physically slicing double-column 
    layouts into single-column reading paths.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Sort files numerically
    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith((".png", ".jpg", ".jpeg"))], 
                         key=lambda x: [int(c) for c in re.findall(r'\d+', x)])

    print(f"Processing {len(image_files)} double-column pages...")

    for index, img_file in enumerate(image_files):
        img_path = os.path.join(input_folder, img_file)
        img = Image.open(img_path)
        
        width, height = img.size
        center = width // 2
        
        # Crop Left and Right columns
        left_col = img.crop((0, 0, center, height))
        right_col = img.crop((center, 0, width, height))
        
        # Save sequentially
        base_name = os.path.splitext(img_file)[0]
        left_col.save(os.path.join(output_folder, f"{base_name}_1_Left.png"))
        right_col.save(os.path.join(output_folder, f"{base_name}_2_Right.png"))

    print("Pre-processing complete. Images are ready for VLM extraction.")

if __name__ == "__main__":
    split_double_column_images('./data/1_raw_scans', './data/2_columns')
