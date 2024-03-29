// import modules
const express = require('express');
const https = require('https');
const http = require('http');
const multer = require('multer');
const axios = require('axios');
const { createCanvas, loadImage } = require('canvas');
const { buffer } = require('stream/consumers');
const fs = require('fs');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const session = require('express-session');

var privateKey  = fs.readFileSync('/certs/selfsigned.key', 'utf8');
var certificate = fs.readFileSync('/certs/selfsigned.crt', 'utf8');
const credentials = {
  key: privateKey,
  cert: certificate,
};

const secretKey = crypto.randomBytes(64).toString('hex');
//const baseUrl = "http://localhost:3000";
const baseUrl = "http://35.188.89.79";

//const pythonEndpoint = "http://host.docker.internal:8000";
const pythonEndpoint = "http://skatorlp_censor_anything_backend_1:8000";

function generateSignedUrl(imageName, expirationTime) {
  // Create a string with the image name and the expiration time
  const stringToSign = imageName + expirationTime;

  // Create a hash using the secret key and the string to sign
  const hash = crypto.createHmac('sha256', secretKey).update(stringToSign).digest('hex');

  // Return the signed URL with the image name, the expiration time, and the hash as query parameters
  return `${baseUrl}/images/${imageName}?expires=${expirationTime}&signature=${hash}`;
}


// create express app
const app = express();
const httpServer = http.createServer(app);
const httpsServer = https.createServer(credentials, app);
app.use(cors());
app.use(cookieParser());
app.use(express.json());

app.use(session({
  secret: 'my-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 60 * 1000 * 5 // 5 minutes
  }
}));

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
    fileSize: 1024 * 1024 * 25 // limit the file size to 25 MB
  },
  fileFilter: fileFilter
});

app.get('/images/:imageName', (req, res) => {
  // Get the image name, the expiration time, and the signature from the query parameters
  const imageName = req.params.imageName;
  const expirationTime = req.query.expires;
  const signature = req.query.signature;

  // Verify that the expiration time and the signature are valid
  if (expirationTime && signature && Date.now() / 1000 < expirationTime && signature === generateSignedUrl(imageName, expirationTime).split('=')[2]) {
    // Serve the image from the images folder
    console.log(imageName)
    const path = __dirname + '/generated_images/' + imageName;
    res.sendFile(path);
  } else {
    // Send a 403 Forbidden error
    res.status(403).send('Access denied');
  }
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/home.html')
});

app.post('/censored_image', async (req, res) => {
  console.log(req.body.boxes);
  try {
    const response = await axios.post(pythonEndpoint + '/get_segmented_image?sessionId=' + req.session.id,
      {boxes: req.body.boxes}, 
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json'
        }
      });

    // get the image from the response and save it to a file
    const imageData = response.data; // Assuming the image data is returned in the response body
    const imgName = req.session.id + "_censored.jpg";
    const fullName = __dirname + "/generated_images/" + imgName;
    fs.writeFileSync(fullName, imageData);

    const expirationTime = Date.now() / 1000 * 60 * 5; // 5 minutes
    const signedUrl = generateSignedUrl(imgName, expirationTime);

    setTimeout(() => {
      fs.unlink(fullName, (err) => {
        if (err) {
          console.error(`Failed to delete file: ${err}`);
        } else {
          console.log(`Deleted file: ${fullName}`);
        }
      });
    }, 1000 * 60 * 5); 


    res.json({ image_url: signedUrl });

  } catch (error) {
    if (error.response && error.response.status === 400) {
      res.status(400).send('Nothing to censor.');
    } else {
      console.error(error);
      res.status(500).send('Something went wrong');
    }
  }
  console.log("Ending");
});

// define a route for uploading and processing images
app.post('/upload', upload.single('image'), async (req, res) => {

  let sessionId = req.session.id;

  if (req.session.sessionId === sessionId){
    console.log("Session is valid.");
  } else {  
    req.session.sessionId = sessionId;
    console.log("new session was created.")
  }

  try {
    // get the uploaded file
    const file = req.file;

    // load the image from the file path
    const image = await loadImage(file.path);

    setTimeout(() => {
      fs.unlink(file.path, (err) => {
        if (err) {
          console.error(`Failed to delete file: ${err}`);
        } else {
          console.log(`Deleted file: ${file.path}`);
        }
      });
    }, 1000 * 60 * 2);
    console.log("Image loaded")

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
    // append sessionID to the form
    console.log("Session ID: " + sessionId)
    formData.append("sessionId", sessionId);
    console.log("Form created");

    const response = await axios.post(pythonEndpoint + '/find_numberplates', 
      formData, 
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    console.log("Response received");
    const boxes = response.data;
      
    const colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan'];

    for (let i = 0; i < boxes.length; i++) {
      const [x1, y1, x2, y2] = boxes[i];

      ctx.strokeStyle = colors[i % colors.length];
      ctx.lineWidth = image.width * 0.005;

      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    }

    res.send(canvas.toDataURL());
  } catch (error) {
    if (error.response) {
        console.log("Error: " + error.response.data);
        console.log("Status: " + error.response.status);
        if (error.response.status === 400) {
            return res.status(400).send('No numberplates found.');
        }
    } else if (error.request) {
        console.log(error.request);
    } else {
        console.log("Error: " + error.message);
    }
    return res.status(500).send('An error occurred.');
}
});

httpsServer.listen(443, '0.0.0.0', () => {
  console.log('HTTPS Server running on https://0.0.0.0:443');
});
httpServer.listen(80, '0.0.0.0', () => {
  console.log('HTTP Server running on https://0.0.0.0:80');
});