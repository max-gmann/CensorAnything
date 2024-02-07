import os
from PIL import Image

def check_and_save_rotated_images(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            try:
                with Image.open(image_path) as image:
                    if "exif" in image.info:
                        exif_data = image._getexif()
                        if exif_data is not None and 274 in exif_data:
                            orientation = exif_data[274]
                            if orientation == 3:
                                rotated_image = image.rotate(180, expand=True)
                            elif orientation == 6:
                                rotated_image = image.rotate(-90, expand=True)
                            elif orientation == 8:
                                rotated_image = image.rotate(90, expand=True)
                            else:
                                rotated_image = image
                            rotated_image.save(image_path)
            except (IOError, OSError):
                print(f"Failed to process image: {image_path}")

# Usage example
folder_path = "/Users/mgx/Library/CloudStorage/GoogleDrive-skatorlp@googlemail.com/Meine Ablage/Licence Plate Detection Dataset v1/val"
check_and_save_rotated_images(folder_path)
