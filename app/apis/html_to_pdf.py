from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import base64

router = APIRouter()

class HtmlToPdfRequest(BaseModel):
    html: str = Field(..., description="HTML-sträng som ska renderas till PDF")
    file_name: str = Field(default="document.pdf", description="Filnamn i svaret (meta)")

class HtmlToPdfResponse(BaseModel):
    base64: str
    contentType: str = "application/pdf"
    fileName: str
    size: int

@router.post("/html_to_pdf", response_model=HtmlToPdfResponse)
def html_to_pdf_endpoint(data: HtmlToPdfRequest):
    if not data.html or not isinstance(data.html, str):
        raise HTTPException(status_code=400, detail="'html' måste vara en icke-tom sträng.")

    # Importera här (inte globalt) så att appen kan starta även om lib saknas
    try:
        from weasyprint import HTML  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"WeasyPrint saknas eller kunde inte laddas: {e}"
        )

    try:
        # Minimal säker HTML-inbäddning
        html_doc = f"<!doctype html><html><head><meta charset='utf-8'></head><body>{data.html}</body></html>"
        pdf_bytes: bytes = HTML(string=html_doc).write_pdf()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Misslyckades att generera PDF: {e}")

    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    return HtmlToPdfResponse(
        base64=b64,
        contentType="application/pdf",
        fileName=data.file_name or "document.pdf",
        size=len(pdf_bytes),
    )
