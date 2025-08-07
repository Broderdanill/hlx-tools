from fastapi import APIRouter
from pydantic import BaseModel
from urllib.parse import quote

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/urlencode")
def urlencode_string(data: TextInput):
    return {"encoded": quote(data.text)}
