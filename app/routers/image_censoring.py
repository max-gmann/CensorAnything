import numpy as np
import cv2
import keras
from keras import ops

def censor_image(image_path, mask):
    print(mask.shape, mask.dtype)
    image = np.array(keras.utils.load_img(image_path))
    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # calculate blur_kernel based on image dimensions
    blur_kernel = int(max(image.shape[:2]) / 100 * 1.5)

    blurred_image = cv2.blur(image, (blur_kernel, blur_kernel))

    mask = ops.convert_to_numpy(mask)
    mask = mask.astype(np.uint8) * 255

    print(mask.shape, mask.dtype)
    print(image.shape, image.dtype)

    img1 = cv2.bitwise_and(image, image, mask= cv2.bitwise_not(np.uint8(mask)))
    img2 = cv2.bitwise_and(blurred_image, blurred_image, mask= np.uint8(mask))

    final_image = cv2.add(img1, img2)

    return cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)