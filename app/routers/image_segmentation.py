import numpy as np
import cv2

import keras
from keras import ops
import keras_cv

class ImageSegmentation:

    MODEL = "sam_base_sa1b"
    MODEL_INPUT_RESOLUTION = (1024, 1024)

    def __init__(self) -> None:
        self.model = keras_cv.models.SegmentAnythingModel.from_preset(self.MODEL)

    def predict(self, image_path, bboxes):
        image = np.array(keras.utils.load_img(image_path))
        original_resolution = image.shape[:2]
        image = self.__inference_resizing(image)
        overall_mask = np.zeros(original_resolution, dtype=np.uint8)
        print("bboxes", bboxes)
        for bbox in bboxes:
            scaled_bbox = self.__scale_bbox(original_resolution, image.shape[:2], [bbox])
            parsed_bbox = self.__parse_bboxes(scaled_bbox)
            print(parsed_bbox.shape)
            print(parsed_bbox)

            outputs = self.model.predict(
                {"images": image[np.newaxis, ...], "boxes": parsed_bbox}
            )
            mask = self.__inference_resizing(outputs["masks"][0][0][..., None], pad=False)[..., 0]
            mask = ops.convert_to_numpy(mask) > 0.0
            mask = mask.astype(np.uint8)
            mask = self.__reverse_resizing(mask, original_resolution)
            overall_mask = np.logical_or(overall_mask, mask)

        return overall_mask

    
    def __inference_resizing(self, image, pad=True):
        # Compute Preprocess Shape
        image = ops.cast(image, dtype="float32")
        old_h, old_w = image.shape[0], image.shape[1]
        scale = self.MODEL_INPUT_RESOLUTION[0] * 1.0 / max(old_h, old_w)
        new_h = old_h * scale
        new_w = old_w * scale
        preprocess_shape = int(new_h + 0.5), int(new_w + 0.5)

        # Resize the image
        image = ops.image.resize(image[None, ...], preprocess_shape)[0]

        # Pad the shorter side
        if pad:
            pixel_mean = ops.array([123.675, 116.28, 103.53])
            pixel_std = ops.array([58.395, 57.12, 57.375])
            image = (image - pixel_mean) / pixel_std
            h, w = image.shape[0], image.shape[1]
            pad_h = self.MODEL_INPUT_RESOLUTION[0] - h
            pad_w = self.MODEL_INPUT_RESOLUTION[1] - w
            image = ops.pad(image, [(0, pad_h), (0, pad_w), (0, 0)])
            # KerasCV now rescales the images and normalizes them.
            # Just unnormalize such that when KerasCV normalizes them
            # again, the padded values map to 0.
            image = image * pixel_std + pixel_mean
        return image
    
    def __scale_bbox(self, input_res, output_res, bboxes):
        # input_res and output_res are tuples of (width, height)
        # bbox is a list of [x1, y1, x2, y2] coordinates
        # returns a scaled bbox as a list of [x1, y1, x2, y2] coordinates
        scaled_bboxes = []
        for bbox in bboxes:
            max_scale = min(output_res[0] / input_res[0], output_res[1] / input_res[1]) # scaling factor for the longest side
            scaled_bbox = []
            for i in range(4):
                scaled_bbox.append(int(round(bbox[i] * max_scale)))
            scaled_bboxes.append(scaled_bbox)
        return scaled_bboxes
    
    def __parse_bboxes(self, bboxes):
        # convert the list of bboxes to a numpy array of shape (1,1,2,2)
        new_bboxes = []
        for box in bboxes:
            new_bboxes.append(np.array([[box[0], box[1]], [box[2], box[3]]]))
            
        bboxes = np.array(new_bboxes)
        bboxes = bboxes[np.newaxis, ...]
        return bboxes
    
    def __reverse_resizing(self, mask, image_shape, pad=True):
        print("image shape for resizing", image_shape)
        if pad:
            h, w = image_shape[-2], image_shape[-1]
            print(h, w)
            scale = 1024 * 1.0 / max(h, w)
            new_h = int(h * scale + 0.5)
            new_w = int(w * scale + 0.5)
            print(new_h, new_w)
            mask = mask[:new_h, :new_w]
        # Resize the mask
        #mask = ops.image.resize(mask[None, ...], (h, w))[0]
        mask =cv2.resize(mask, (w, h), interpolation=cv2.INTER_CUBIC)
        # Cast the mask
        mask = ops.cast(mask, dtype="float32")
        print(mask.shape)

        return mask