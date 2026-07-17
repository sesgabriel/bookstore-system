from pydantic import BaseModel

class ChartItemCreate(BaseModel):
    book_id: int
    quantity: int = 1


class ChartItemUpdate(BaseModel):
    quantity: int

class ChartItemResponse(BaseModel):
    id: int
    book_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True

class ChartResponse(BaseModel):
    id: int
    user_id: int
    active: bool
    items: list[ChartItemResponse] = []
    total: float

    class Config:
        from_attributes = True