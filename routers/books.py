from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models.book import Item
from schemas.book import ItemCreate, ItemResponse, ItemUpdate
from dependencies import get_current_user, require_seller, get_db
from models.users import User

router = APIRouter(prefix="/books", tags=["books"])

# CREATE
@router.post("/", response_model=ItemResponse, status_code=201)
def create_book(item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(require_seller)):
    new_book = Item(**item.model_dump(), seller_id=current_user.id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# READ (all)
@router.get("/", response_model=list[ItemResponse])
def list_books(name: str | None = Query(None, description="Search by book's name"),
    author: str | None = Query(None, description="Search by author"), min_price: float | None = Query(None, description="Minimum price (in cents)", ge=0),
    max_price: float | None = Query(None, description="Max price (in cents)", ge=0),
    db: Session = Depends(get_db)):

    # validation: min_price cannot be greater than max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )
        
    query = db.query(Item)

    # book name filter
    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))  # partial search, case-insensitive
    
    # author filter
    if author:
        query = query.filter(Item.author.ilike(f"%{author}%"))  # partial search, case-insensitive

    # minimum price filter
    if min_price is not None:
        query = query.filter(Item.price >= min_price)

    # maximum price filter
    if max_price is not None:
        query = query.filter(Item.price <= max_price)

    return query.all()

# READ (one)
@router.get("/{item_id}", response_model=ItemResponse)
def find_book(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    return item

# UPDATE
@router.put("/{item_id}", response_model=ItemResponse)
def update_book(item_id: int, data: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_seller)):
    item = db.query(Item).filter(Item.id == item_id, Item.seller_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Book not found or you don't have permission to update it")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

# DELETE
@router.delete("/{item_id}", status_code=204)
def delete_book(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_seller)): # only sellers book's owner can delete books
    item = db.query(Item).filter(Item.id == item_id, Item.seller_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Book not found or you don't have permission to delete it")
    db.delete(item)
    db.commit()