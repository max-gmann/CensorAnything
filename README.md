<div align="center">

# :oncoming_automobile: Censor Anything :camera:


---

### Automatically censors any numberplate
<p style="display: flex; align-items: center; justify-content: space-between;">
  <img src="model_training/examples/DSC04434.jpeg" style="width: 45%;" />
  <span>&#8594;</span>
  <img src="model_training/examples/censored_image (7).jpg" style="width: 45%;" /> 
</p>

### Add additional objects, faces or text to be censored.
<p style="display: flex; align-items: center; justify-content: space-between;">
  <img src="model_training/examples/_DSC6024.jpeg" style="width: 45%;" />
  <span>&#8594;</span>
  <img src="model_training/examples/censored_image (8).jpg" style="width: 45%;" /> 
</p>

### Retains original image quality with high-precision cutouts
<p style="display: flex; align-items: center; justify-content: space-between;">
  <img src="model_training/examples/DJI_0812.jpg" style="width: 45%;" />
  <span>&#8594;</span>
  <img src="model_training/examples/censored_image (11).jpg" style="width: 45%;" /> 
</p>

---

</div>

## :bookmark_tabs: Table of Contents
- [:oncoming\_automobile: Censor Anything :camera:](#oncoming_automobile-censor-anything-camera)
  - [:bookmark\_tabs: Table of Contents](#bookmark_tabs-table-of-contents)
  - [:information\_source: General Info](#information_source-general-info)
  - [:computer: Technologies](#computer-technologies)
  - [:book: Usage](#book-usage)
  - [:page\_facing\_up: License](#page_facing_up-license)

---




## :information_source: General Info
This project was originally inspired by the need to censor license plates on images I took at car meets. The solution was to train a instance segmentation model to detect numberplates and blur numberplates with openCV. 

### Version 2
Seeing a impressive zero-shot demo of Meta AI's [Segment Anything model](https://segment-anything.com/) on Twitter sparked the idea to extend this project to dynamically allow the user to censor any other objects in an image. For more interactivity a object detection model is now only used to predict bounding boxes for numberplates and the user has the ability to draw additional bounding boxes directly on the image. The Segment Anything model then segments these objects with suprising accuracy and the resulting mask is used for censoring the requested parts of the image.

![Model Flow](model_training/model_flow.drawio.png)




---

## :computer: Technologies


* keras-cv
* Python: 3.10
* OpenCV: 4.5.1
* PyTorch: 2.4.1

### Deployment:
* FastAPI
* node.js with express
* Google Cloud Platform Compute Engine
* Docker 
* GitHub Actions (Docker Build & Deployment)

![Architecture Diagram](model_training/censor_anything.png)

---

## :book: Usage

The project is available here: [censor-anything.com](www.censor-anything.com) 

Start by uploading any imgage you like. It will automatically scanned for numberplates. Next, you will be able to add aditional objects to censor by drawing bounding boxes. Finally, clicking the "Censor" button will apply the Segment Anything model to select all the objects with bounding boxes and return the censored image which can be downloaded.

(Please note that the website is running on a very cheap and thus slow server without GPU acceleration. So inference might take a while :D Also, if the domain is not available anymore I have likely run out of GCP credits.)

---

## :page_facing_up: License
MIT License

Copyright (c) [2024] [Max Grundmann]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<div align="center">

Made by [Max Grundmann](https://github.com/max-gmann)

</div>
