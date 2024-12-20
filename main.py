from rembg import remove
from PIL import Image, ImageFilter
import io
import os

HORIZONTAL_PADDING = 20
TOP_PADDING = 20
BOTTOM_PADDING = 20
MAX_SIZE = 2048
BLUR = 10
INPUT_FOLDER = 'input_images'
OUTPUT_FOLDER = 'output_images'
TEXT_APPENDED_TO_IMG_NAME = '_altered'

def resize_image(image):
    """Resize the image if its width or height is greater than max_size."""
    width, height = image.size
    if width > MAX_SIZE or height > MAX_SIZE:
        # Maintain aspect ratio
        aspect_ratio = width / height
        if aspect_ratio > 1:
            new_width = MAX_SIZE
            new_height = int(MAX_SIZE / aspect_ratio)
        else:
            new_height = MAX_SIZE
            new_width = int(MAX_SIZE * aspect_ratio)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image
    return image

def remove_background_and_crop(input_path, output_path):
    # Load the image with Rembg and remove the background
    with open(input_path, 'rb') as f:
        input_image = f.read()
    output_image = remove(input_image)
    
    # Convert the output to a PIL image
    output_pil_image = Image.open(io.BytesIO(output_image)).convert("RGBA")

    # Get the bounding box of the non-transparent part
    bbox = output_pil_image.getbbox()

    # Add padding to the bounding box
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - HORIZONTAL_PADDING) 
    y0 = max(0, y0 - TOP_PADDING) 
    x1 = min(output_pil_image.width, x1 + HORIZONTAL_PADDING) 
    y1 = min(output_pil_image.height, y1 + BOTTOM_PADDING)

    # Crop the image with the padding
    cropped_image = output_pil_image.crop((x0, y0, x1, y1))

    # Resize the image if necessary
    resized_cropped_image = resize_image(cropped_image)

    # Create a new mask with blurred edges
    alpha = cropped_image.split()[3] 
    blurred_alpha = alpha.filter(ImageFilter.GaussianBlur(BLUR))

    # Combine the blurred alpha channel back with the image resized_cropped_image.putalpha(blurred_alpha)
    resized_cropped_image.putalpha(blurred_alpha)

    # Save the cropped image with transparency
    resized_cropped_image.save(output_path, format="PNG")

def process_folder():
    # Check if the output folder exists, and create it if it doesn't
    if not os.path.exists(OUTPUT_FOLDER):
        print(f"Creating output folder: {OUTPUT_FOLDER}")
        os.makedirs(OUTPUT_FOLDER)
    else:
        print(f"Output folder already exists: {OUTPUT_FOLDER}")

    # Process each file in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + TEXT_APPENDED_TO_IMG_NAME + '.png')
            print(f"About to process file: {filename}")
            remove_background_and_crop(input_path, output_path)
            print(f"Finished processing file: {filename}")
        else:
            print(f"Skipping non-image file: {filename}")



process_folder()