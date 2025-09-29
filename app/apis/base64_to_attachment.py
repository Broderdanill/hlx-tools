from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
import base64
import mimetypes
import re

router = APIRouter()

class Base64ToAttachmentRequest(BaseModel):
    base64: str = Field(..., description="Base64-kodad fil. 'data:*;base64,'-prefix tillåts.")
    file_name: str = Field(..., description="Filnamn som ska användas i Content-Disposition.")
    content_type: str | None = Field(
        default=None,
        description="MIME-typ. Om None försöker vi gissa från filnamnet."
    )

def _normalize_base64(s: str) -> str:
    s = s.strip()
    if "base64," in s:
        s = s.split("base64,", 1)[1].strip()
    return s

@router.post("/base64_to_attachment")
def base64_to_attachment(data: Base64ToAttachmentRequest):
    """
    Tar emot base64 + filnamn och returnerar BINÄR fil
    med korrekta headers för AR System (Developer Studio filter).
    """
    clean = _normalize_base64(data.base64)
    if not clean:
        raise HTTPException(status_code=400, detail="'base64' får inte vara tom.")

    # tillåt whitespace men inga andra tecken
    if not re.fullmatch(r"[A-Za-z0-9+/=\s]+", clean):
        raise HTTPException(status_code=400, detail="Ogiltig base64-sträng.")

    try:
        binary = base64.b64decode(clean, validate=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kunde inte dekoda base64: {e}")

    # MIME-type: använd given, annars gissa från filnamn, annars octet-stream
    ct = data.content_type
    if not ct:
        guessed, _ = mimetypes.guess_type(data.file_name)
        ct = guessed or "application/octet-stream"

    headers = {
        "Content-Disposition": f'attachment; filename="{data.file_name}"'
    }
    return Response(content=binary, media_type=ct, headers=headers)
