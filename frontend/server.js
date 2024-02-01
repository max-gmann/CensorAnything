// import modules
const express = require('express');
const multer = require('multer');
const axios = require('axios');
const { createCanvas, loadImage } = require('canvas');
const { buffer } = require('stream/consumers');
const fs = require('fs');
const cors = require('cors');

// create express app
const app = express();
app.use(cors());

// set up static folder for serving html files
app.use(express.static('public'));

// set up the storage options
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    // specify the destination folder
    cb(null, './uploads');
  },
  filename: function (req, file, cb) {
    // specify the file name
    cb(null, file.originalname);
  }
});

// set up the file filter
const fileFilter = (req, file, cb) => {
  // accept only image files
  if (file.mimetype === 'image/jpeg' || file.mimetype === 'image/png' || file.mimetype === 'image/jpg') {
    cb(null, true);
  } else {
    cb(null, false);
  }
};

// create the upload middleware
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 1024 * 1024 * 5 // limit the file size to 5 MB
  },
  fileFilter: fileFilter
});

// define a route for uploading and processing images
app.post('/upload', upload.single('image'), async (req, res) => {
    console.log("uploading")
  try {
    // get the uploaded file
    const file = req.file;
    console.log(file)

    // load the image from the file path
    const image = await loadImage(file.path);

    // create a canvas with the same size as the image
    const canvas = createCanvas(image.width, image.height);
    const ctx = canvas.getContext('2d');

    // draw the image on the canvas
    ctx.drawImage(image, 0, 0);

    console.log("Creating form");
    
    const dataURL = canvas.toDataURL("image/jpeg");

    const res2 = await fetch(dataURL);
    const blob = await res2.blob();

    const formData = new FormData();
    formData.append("file", blob, "image.jpg");

    const response = await axios.post('http://127.0.0.1:8000/find_numberplates', 
      formData, 
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    console.log("Response received");
    console.log(response.data);
    const boxes = response.data;

    // define some colors for the boxes
    const colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan'];

    // loop through the boxes and draw them on the canvas
    for (let i = 0; i < boxes.length; i++) {
      // get the box coordinates
      const [x1, y1, x2, y2] = boxes[i];

      // set the stroke style and line width
      ctx.strokeStyle = colors[i % colors.length];
      ctx.lineWidth = 5;

      // draw the box
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    }

    // send the modified image back to the client
    res.send(canvas.toDataURL());
  } catch (error) {
    // handle any errors
    console.log("An error has occured.")
    console.error(error);
    res.status(500).send('Something went wrong');
  }
});

// start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});