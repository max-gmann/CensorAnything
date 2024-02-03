from typing import Union, Annotated, List
from fastapi import FastAPI, File, UploadFile

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

app = FastAPI()

class SessionData(BaseModel):
    image_path: str
    bboxes: List = []
    masks: List = []
    final_image: UploadFile = None

cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)


@app.post("/find_numberplates")
async def find_numberplates(file: UploadFile, response: Response):

    session = uuid4()
    
    file.filename = f"{session}.jpg"
    contents = await file.read()
    
    file_path = f"{IMAGE_STORAGE_PATH}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(contents)

    prediction = numberplate_detector.predict(file_path)

    if len(prediction["boxes"]) == 0:
        return "no numberplate found"
    
    data = SessionData(image_path=file_path, bboxes = prediction["boxes"].tolist())

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return data.bboxes

# async def add_bbox(session_data: SessionData, bbox: List):

@app.get("/get_segmented_image", dependencies=[Depends(cookie)])
async def segment_image(session_data: SessionData = Depends(verifier)):
    masks = image_segmentor.predict(image_path=session_data.image_path, 
                                    bboxes= session_data.bboxes)
    print("Masks generated successfully.")
    print(masks)
    
    final_image = censor_image(session_data.image_path, masks)
    # save final image to disk

    import cv2
    cv2.imwrite("number_one.jpg", final_image)


    return session_data


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    #print(session_data.image.filename)
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"


