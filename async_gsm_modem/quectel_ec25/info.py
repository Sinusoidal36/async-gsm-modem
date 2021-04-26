from pydantic import BaseModel

class ProductInfo(BaseModel):
    manufacturer: str
    model: str
    revision: str