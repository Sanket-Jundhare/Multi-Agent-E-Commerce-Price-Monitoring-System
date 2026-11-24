from typing import Optional

from pydantic import BaseModel, EmailStr

class TrackProductRequest(BaseModel):
    email: EmailStr
    product_name: str
    budget: int
    product_url: Optional[str] = None