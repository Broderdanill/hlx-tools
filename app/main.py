from fastapi import FastAPI
from app.apis import (
    urlencode,
    urldecode,
    random_number,
    json_selector,
    file_to_base64,
    strip_html
)

app = FastAPI()

app.include_router(urlencode.router)
app.include_router(urldecode.router)
app.include_router(random_number.router)
app.include_router(json_selector.router)
app.include_router(file_to_base64.router)
app.include_router(strip_html.router)
