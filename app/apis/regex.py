from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re

router = APIRouter()

class RegexRequest(BaseModel):
    text: str = Field(..., description="Text att köra regex mot")
    regex: str = Field(..., description="Regex-mönster (utan snedstreck)")
    flags: Optional[str] = Field(default="", description="Ex. 'g', 'i', 'm', 's', 'x'")

class RegexMatch(BaseModel):
    match: str
    index: int
    captures: List[str]
    groups: Optional[Dict[str, Any]] = None

class RegexResponse(BaseModel):
    ok: bool
    pattern: str
    flags: str
    matches: List[RegexMatch]
    firstMatch: Optional[str] = None

_FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
    "x": re.VERBOSE,
}

def _compile(pattern: str, flags_str: str) -> re.Pattern:
    flags_val = 0
    for ch in flags_str or "":
        if ch == "g":
            continue  # hanteras logiskt nedan
        if ch in _FLAG_MAP:
            flags_val |= _FLAG_MAP[ch]
        else:
            raise ValueError(f"Okänd flagga: {ch}")
    return re.compile(pattern, flags_val)

@router.post("/regex", response_model=RegexResponse)
def regex_endpoint(data: RegexRequest):
    if not data.regex:
        raise HTTPException(status_code=400, detail="'regex' krävs.")

    try:
        rx = _compile(data.regex, data.flags or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ogiltig regex/flagga: {e}")

    matches: List[RegexMatch] = []

    try:
        if "g" in (data.flags or ""):
            for m in rx.finditer(data.text):
                matches.append(
                    RegexMatch(
                        match=m.group(0),
                        index=m.start(),
                        captures=[g if g is not None else "" for g in m.groups()],
                        groups=m.groupdict() or None,
                    )
                )
        else:
            m = rx.search(data.text)
            if m:
                matches.append(
                    RegexMatch(
                        match=m.group(0),
                        index=m.start(),
                        captures=[g if g is not None else "" for g in m.groups()],
                        groups=m.groupdict() or None,
                    )
                )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Regex-matchning misslyckades: {e}")

    return RegexResponse(
        ok=True,
        pattern=data.regex,
        flags=data.flags or "",
        matches=matches,
        firstMatch=matches[0].match if matches else None,
    )
