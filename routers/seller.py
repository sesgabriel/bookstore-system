from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from dependencies import get_current_user, require_seller
from models.users import User
from models.book import Item
from models.chart import ChartItem, Chart

router = APIRouter(prefix="/seller", tags=["seller"])


@router.get("/sales")
def get_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    """
    Return sales statistics for the logged-in seller:
    - Total books sold
    - List of books sold with quantities and revenue
    - Total revenue
    """
    # Get all books by this seller
    seller_books = db.query(Item).filter(Item.seller_id == current_user.id).all()
    book_ids = [book.id for book in seller_books]
    
    if not book_ids:
        return {
            "total_books_sold": 0,
            "total_revenue": 0.0,
            "books_sold": []
        }
    
    # Get all ChartItems for this seller's books that are in finalized carts
    sales = db.query(ChartItem).join(Chart).filter(
        ChartItem.book_id.in_(book_ids),
        Chart.active == False  # Only finalized purchases
    ).all()
    
    # Calculate totals per book
    books_sold = []
    total_revenue = 0
    total_books_sold = 0
    
    for book in seller_books:
        book_sales = [s for s in sales if s.book_id == book.id]
        quantity_sold = sum(s.quantity for s in book_sales)
        revenue = sum(s.quantity * s.unit_price for s in book_sales)
        
        if quantity_sold > 0:
            books_sold.append({
                "book_id": book.id,
                "book_name": book.name,
                "quantity_sold": quantity_sold,
                "unit_price": book.price,
                "revenue": revenue
            })
            total_revenue += revenue
            total_books_sold += quantity_sold
    
    return {
        "total_books_sold": total_books_sold,
        "total_revenue": total_revenue,
        "books_sold": books_sold
    }