from fastapi import APIRouter, File, UploadFile
import base64

router = APIRouter()

@router.post("/file-to-base64")
async def file_to_base64(file: UploadFile = File(...)):
    content = await file.read()
    b64_encoded = base64.b64encode(content).decode('utf-8')
    return {
        "filename": file.filename,
        "base64": b64_encoded
    }
