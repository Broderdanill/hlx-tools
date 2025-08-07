
from fastapi import APIRouter
from pydantic import BaseModel
from bs4 import BeautifulSoup

router = APIRouter()

class HtmlInput(BaseModel):
    html: str

@router.post("/strip-html")
def strip_html_tags(data: HtmlInput):
    soup = BeautifulSoup(data.html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    cleaned = ' '.join(text.split())
    return {"text": cleaned}
