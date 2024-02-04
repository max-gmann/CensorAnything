import cv2
from typing import Union, Annotated, List
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel

from uuid import UUID, uuid4

from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi import FastAPI, Response, Depends

from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi import HTTPException, FastAPI, Response, Depends
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

from torchvision.io import read_image

from uuid import UUID, uuid4

from routers.numberplate_detection import NumberPlateDetection
from routers.image_segmentation import ImageSegmentation
from routers.image_censoring import censor_image

IMAGE_STORAGE_PATH = "/Users/mgx/Documents/censor_sam/app/images"

numberplate_detector = NumberPlateDetection()
image_segmentor = ImageSegmentation()

class Box(BaseModel):
    startX: float
    startY: float
    endX: float
    endY: float

class BoxesData(BaseModel):
    boxes: List[Box]

uploads = {"test": 
           {"image_path": IMAGE_STORAGE_PATH + "/test.jpg", 
            "bboxes": [[1542.46240234375,3424.305908203125,2121.431884765625,3575.4013671875]]
            }
    }

app = FastAPI()

@app.post("/find_numberplates")
async def find_numberplates(file: UploadFile, sessionId: str = File(...)):

    print(sessionId)
    
    file.filename = f"{sessionId}.jpg"
    contents = await file.read()
    
    file_path = f"{IMAGE_STORAGE_PATH}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(contents)

    prediction = numberplate_detector.predict(file_path)

    bboxes = prediction["boxes"].tolist()

    if len(bboxes) == 0:
        uploads[sessionId] = {"image_path": file_path, "bboxes": bboxes}
        raise HTTPException(status_code=400, detail="No number plates found")

    uploads[sessionId] = {"image_path": file_path, "bboxes": bboxes}

    return bboxes

# async def add_bbox(session_data: SessionData, bbox: List):

@app.post("/get_segmented_image")
async def segment_image(request: Request, boxes_data: BoxesData):
    session_id = request.query_params["sessionId"]

    boxes = boxes_data.boxes
    boxes_list = [[box.startX, box.startY, box.endX, box.endY] for box in boxes]

    uploads[session_id]["bboxes"].extend(boxes_list)

    print(uploads[session_id]["bboxes"])

    # get sessionId from request

    if session_id not in uploads.keys():
        return "Session not found"

    masks = image_segmentor.predict(image_path=uploads[session_id]["image_path"], 
                                    bboxes= uploads[session_id]["bboxes"])
    print("Masks generated successfully.")
    print(masks)
    
    final_image = censor_image(uploads[session_id]["image_path"], masks)
    
    new_image_path = f"{IMAGE_STORAGE_PATH}/{session_id}_censored.jpg"
    cv2.imwrite(new_image_path, final_image)

    return FileResponse(new_image_path, media_type="image/jpeg", filename="censored_image.jpg")


