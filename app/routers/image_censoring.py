import numpy as np
import cv2
import keras
from keras import ops

def censor_image(image_path, mask, blur_kernel=60):
    print(mask.shape, mask.dtype)
    image = np.array(keras.utils.load_img(image_path))
    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite("before.jpg", image)

    blurred_image = cv2.blur(image, (blur_kernel, blur_kernel))
    cv2.imwrite("blurred.jpg", blurred_image)

    mask = ops.convert_to_numpy(mask) #> 0.0
    mask = mask.astype(np.uint8) * 255
    #mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    print(mask.shape, mask.dtype)
    print(image.shape, image.dtype)

    img1 = cv2.bitwise_and(image, image, mask= cv2.bitwise_not(np.uint8(mask)))
    img2 = cv2.bitwise_and(blurred_image, blurred_image, mask= np.uint8(mask))

    final_image = cv2.add(img1, img2)

    test = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite("after.jpg", test)

    return final_image