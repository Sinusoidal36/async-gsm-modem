from pydantic import BaseModel
from datetime import datetime

class SMS(BaseModel):
    index: int
    status: str
    alpha: str
    length: int
    pdu: bytes
    text: str
    from_number: str
    date: datetime