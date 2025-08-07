from fastapi import APIRouter, Query
import random

router = APIRouter()

@router.get("/random-number")
def get_random_number(from_: int = Query(..., alias="from"), to: int = Query(...)):
    return {"random": random.randint(from_, to)}
