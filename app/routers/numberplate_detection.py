import os

os.environ["KERAS_BACKEND"] = "tensorflow"

import timeit
import numpy as np
import matplotlib.pyplot as plt
import keras
from keras import ops
import keras_cv
import os 
import torch
from pprint import pprint
 
from torchvision.io import read_image
from torchvision.utils import draw_bounding_boxes

import matplotlib.pyplot as plt

class NumberPlateDetection:

    MODEL_LOCATION = "../app/models/checkpoint.pth"

    def __init__(self) -> None:
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.model = torch.load(NumberPlateDetection.MODEL_LOCATION, map_location=self.device)
        self.model.eval()
        print("Model loaded successfully")
        
    def predict(self, image):
        image = read_image(image) / 255.0
        image = image[:3, ...].to(self.device)

        with torch.no_grad():
            start_time = timeit.default_timer()  # Start measuring time
            predictions = self.model([image, ])
            end_time = timeit.default_timer()  # Stop measuring time
            inference_time = end_time - start_time  # Calculate inference time
            print("Inference time:", inference_time)  # Print inference time

            prediction = predictions[0]

        # filter predictions with confidence score above 0.98
        scores = prediction["scores"]
        mask = scores > 0.98
        prediction["boxes"] = prediction["boxes"][mask]
        prediction["labels"] = prediction["labels"][mask]
        prediction["scores"] = prediction["scores"][mask]

        print(prediction)
        return prediction


