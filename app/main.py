from fastapi import FastAPI, UploadFile
from pydub import AudioSegment

from video2frames import Video2Frames

app = FastAPI()


@app.post("/")
async def root(file: UploadFile):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    utils = Video2Frames()
    utils.convert(
        file_location,
        "output/"
    )
    return {
        "status": "success",
    }