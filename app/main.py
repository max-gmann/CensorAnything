import cv2, os
from typing import List

from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from fastapi import HTTPException, FastAPI

from pydantic import BaseModel

from routers.numberplate_detection import NumberPlateDetection
from routers.image_segmentation import ImageSegmentation
from routers.image_censoring import censor_image

IMAGE_STORAGE_PATH = "./images"

numberplate_detector = NumberPlateDetection()
image_segmentor = ImageSegmentation()

class Box(BaseModel):
    startX: float
    startY: float
    endX: float
    endY: float

class BoxesData(BaseModel):
    boxes: List[Box]

def file_streamer(path):
    with open(path, 'rb') as f:
        yield from f
    os.remove(path)

# content for debugging only
uploads = {"test": 
           {"image_path": IMAGE_STORAGE_PATH + "/test.jpg", 
            "bboxes": [[1542.46240234375,3424.305908203125,2121.431884765625,3575.4013671875]]
            }
    }

def file_streamer(path):
    with open(path, 'rb') as f:
        yield from f
    os.remove(path)

app = FastAPI()

@app.post("/find_numberplates")
async def find_numberplates(file: UploadFile, sessionId: str = File(...)):

    print(sessionId)
    
    file.filename = f"{sessionId}.jpg"
    contents = await file.read()
    
    file_path = f"{IMAGE_STORAGE_PATH}/{file.filename}"

    with open(file_path, "wb") as f:
        print("writing file")
        f.write(contents)

    print("starting prediciton")
    prediction = numberplate_detector.predict(file_path)
    print("prediction done")

    bboxes = prediction["boxes"].tolist()

    if len(bboxes) == 0:
        uploads[sessionId] = {"image_path": file_path, "bboxes": bboxes}
        raise HTTPException(status_code=400, detail="No number plates found")

    uploads[sessionId] = {"image_path": file_path, "bboxes": bboxes}

    return bboxes

@app.post("/get_segmented_image")
async def segment_image(request: Request, boxes_data: BoxesData):
    session_id = request.query_params["sessionId"]

    boxes = boxes_data.boxes
    boxes_list = [[box.startX, box.startY, box.endX, box.endY] for box in boxes]

    uploads[session_id]["bboxes"].extend(boxes_list)

    if session_id not in uploads.keys():
        return "Session not found"

    if len(uploads[session_id]["bboxes"]) == 0:
        raise HTTPException(status_code=400, detail="Nothing to censor.")

    masks = image_segmentor.predict(image_path=uploads[session_id]["image_path"], 
                                    bboxes= uploads[session_id]["bboxes"])
    
    final_image = censor_image(uploads[session_id]["image_path"], masks)
    
    new_image_path = f"{IMAGE_STORAGE_PATH}/{session_id}_censored.jpg"
    cv2.imwrite(new_image_path, final_image)

    original_image_path = uploads[session_id]["image_path"]
    os.remove(original_image_path)

    print("deleting", new_image_path)
    print("deleting", uploads[session_id]["image_path"])

    del uploads[session_id]
    
    return StreamingResponse(file_streamer(new_image_path), 
                             media_type="image/jpeg")


