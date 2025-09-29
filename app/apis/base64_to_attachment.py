from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import re

router = APIRouter()

class Base64ToAttachmentRequest(BaseModel):
    base64: str = Field(..., description="Base64-kodad fil. 'data:*;base64,'-prefix tillåts men krävs ej.")
    file_name: str = Field(..., description="Ex. 'file.pdf'")
    content_type: str = Field(..., description="Ex. 'application/pdf'")

class ARAttachment(BaseModel):
    name: str
    contentType: str
    data: str  # base64 utan data-URL-prefix
    size: int  # bytes (dekoderat)

def _normalize_base64(s: str) -> str:
    s = s.strip()
    # Ta bort ev. data-URL prefix
    if "base64," in s:
        s = s.split("base64,", 1)[1].strip()
    return s

def _byte_length_of_base64(b64: str) -> int:
    padding = 2 if b64.endswith("==") else (1 if b64.endswith("=") else 0)
    return (len(b64) * 3) // 4 - padding

@router.post("/base64_to_Attachment", response_model=ARAttachment)
def base64_to_attachment_endpoint(data: Base64ToAttachmentRequest):
    clean = _normalize_base64(data.base64)

    if not clean:
        raise HTTPException(status_code=400, detail="'base64' får inte vara tom.")

    # Enkel validering (tillåter whitespace)
    if not re.fullmatch(r"[A-Za-z0-9+/=\s]+", clean):
        raise HTTPException(status_code=400, detail="Ogiltig base64-sträng.")

    size = _byte_length_of_base64(clean)

    return ARAttachment(
        name=data.file_name,
        contentType=data.content_type,
        data=clean,
        size=size,
    )
