from fastapi import APIRouter
from pydantic import BaseModel
import jsonpath_ng

router = APIRouter()

class SelectorInput(BaseModel):
    json_data: dict
    selector: str  # Ex: $.user.name

@router.post("/json-selector")
def select_json_path(data: SelectorInput):
    try:
        expr = jsonpath_ng.parse(data.selector)
        matches = [match.value for match in expr.find(data.json_data)]
        return {"result": matches}
    except Exception as e:
        return {"error": str(e)}
