import numpy as np
from PIL import Image

def replace_color_with_transparent_numpy(image_path, target_color_rgb):
    # Open image and convert to RGBA
    img = Image.open(image_path).convert('RGBA')
    # Convert image to NumPy array
    img_data = np.array(img)

    # Define the target color and the replacement color (transparent)
    target_color = np.array(target_color_rgb + (255,)) # Need full RGBA for comparison
    transparent_color = np.array([0, 0, 0, 0]) # R, G, B, Alpha = 0

    # Create a mask where pixels match the target color
    # (img_data == target_color) returns a boolean array for each channel
    # .all(axis=-1) checks if all channels (R, G, B, A) match
    mask = (np.abs(img_data - target_color) < 25).all(axis=-1)

    # Replace the matching pixels with the transparent color
    img_data[mask] = transparent_color

    # Convert the NumPy array back to a Pillow Image and save
    final_image = Image.fromarray(img_data, mode='RGBA')
    final_image.save(image_path, "PNG")#.split('.')[0] + "_transparent.png", "PNG")
    print(f"Image saved as {image_path} with color {target_color_rgb} made transparent.")

# Example usage:
# Replace the color black (0, 0, 0) with transparent
# replace_color_with_transparent_numpy(r"images\tech_slot_saw.png", (255, 238, 191))
replace_color_with_transparent_numpy(r"images\tech_slot_auto_use.png", (255, 0, 0))