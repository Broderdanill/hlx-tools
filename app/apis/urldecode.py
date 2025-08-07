
from fastapi import APIRouter
from pydantic import BaseModel
from urllib.parse import unquote

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/urldecode")
def urldecode_string(data: TextInput):
    return {"decoded": unquote(data.text)}
