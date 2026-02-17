import cv2
import numpy as np
from PIL import Image

def replace_color_with_transparent_numpy(image_path, target_color_rgb, fill_gaps=True):
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

    if not fill_gaps:
        # Replace the matching pixels with the transparent color
        img_data[mask] = transparent_color
    else:
        mask_to_fill_l = np.zeros((*img_data.shape[:-1], 1))
        mask_to_fill_r = np.zeros((*img_data.shape[:-1], 1))
        mask_to_fill_l[~(mask[:, ::-1])] = 255
        mask_to_fill_r[~mask] = 255
        # mask_to_fill[30:40, 20:30] = 255
        # Создаем ядро (структурный элемент)
        # Чем больше размер (5,5), тем более крупные дырки будут закрыты
        kernel = np.ones((2, 2), np.uint8)

        # Применяем операцию закрытия
        result_l = cv2.morphologyEx(mask_to_fill_l, cv2.MORPH_CLOSE, kernel)
        result_r = cv2.morphologyEx(mask_to_fill_r, cv2.MORPH_CLOSE, kernel)
        result_r[(result_l[:, ::-1]) == 0] = 0
        img_data[result_r == 0] = transparent_color
        # cv2.imwrite(image_path.split('.')[0] + '_.png', img_data)

    final_image = Image.fromarray(img_data, mode='RGBA')
    final_image.save(image_path, "PNG")#.split('.')[0] + "_transparent.png", "PNG")
    print(f"Image saved as {image_path} with color {target_color_rgb} made transparent.")

# Example usage:
# Replace the color black (0, 0, 0) with transparent
image_path = r"images\tunnel_alt.png"
replace_color_with_transparent_numpy(image_path, (236, 235, 174))
# replace_color_with_transparent_numpy(image_path, (255, 238, 191))
# replace_color_with_transparent_numpy(image_path, (234, 216, 149))
# replace_color_with_transparent_numpy(image_path, (255, 0, 0))