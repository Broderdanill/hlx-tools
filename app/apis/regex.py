from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re

router = APIRouter()

class RegexRequest(BaseModel):
    text: str = Field(..., description="Text att köra regex mot")
    regex: str = Field(..., description="Regex-mönster (utan snedstreck)")
    flags: Optional[str] = Field(default="", description="Ex. 'g', 'i', 'm', 's', 'x'")
    # ⚙️ Nya fält:
    conform: Optional[bool] = Field(
        default=False,
        description="Om true: försök 'fixa' texten att stämma med regex och returnera den fixerade strängen (annars tom)."
    )
    require_full_match: Optional[bool] = Field(
        default=False,
        description="Om true: texten måste matcha hela mönstret (equivalent till ^...$)."
    )
    template: Optional[str] = Field(
        default=None,
        description="Valfritt ersättningsmönster (t.ex. '0\\1-\\2') som byggs från första matchens grupper. Används endast när conform=true."
    )

class RegexMatch(BaseModel):
    match: str
    index: int
    captures: List[str]
    groups: Optional[Dict[str, Any]] = None

class RegexResponse(BaseModel):
    ok: bool
    valid: bool
    pattern: str
    flags: str
    matches: List[RegexMatch]
    firstMatch: Optional[str] = None
    # 🆕 den fixerade strängen:
    conformed: str = ""

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

    # Hämta träffar (som tidigare)
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

    # ✅ valid: antingen fullmatch (om begärt) eller minst en träff
    full_ok = rx.fullmatch(data.text) is not None
    valid = full_ok if data.require_full_match else (len(matches) > 0)

    # 🛠️ conform: bygg "fixad" sträng
    conformed = ""
    if data.conform:
        if data.require_full_match:
            # Kräver att hela strängen matchar — annars tom
            if full_ok:
                if data.template:
                    # Bygg utifrån första (och enda) fullmatch
                    m = rx.fullmatch(data.text)
                    try:
                        conformed = m.expand(data.template) if m else ""
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Fel i template-expand: {e}")
                else:
                    # redan giltig: returnera originalet
                    conformed = data.text
            else:
                conformed = ""  # ej korrekt -> tom
        else:
            # Kräv inte hel-match: ta första delmatch och ev. formatera den
            m = rx.search(data.text)
            if m:
                if data.template:
                    try:
                        conformed = m.expand(data.template)
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Fel i template-expand: {e}")
                else:
                    # Ingen template: returnera första matchande substringen
                    conformed = m.group(0)
            else:
                conformed = ""

    return RegexResponse(
        ok=True,
        valid=bool(valid),
        pattern=data.regex,
        flags=data.flags or "",
        matches=matches,
        firstMatch=matches[0].match if matches else None,
        conformed=conformed,
    )
