from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.book import Item
from models.users import User
from models.chart import Chart, ChartItem
from schemas.chart import ChartItemCreate, ChartResponse, ChartItemUpdate
from dependencies import require_client, get_current_user, get_db


router = APIRouter(prefix="/chart", tags=["chart"])


def get_or_create_chart(user: User, db: Session) -> Chart:
    """It will return the SQLAlchemy object."""
    chart = db.query(Chart).filter(
        Chart.user_id == user.id,
        Chart.active == True
    ).first()

    if not chart:
        chart = Chart(user_id=user.id)
        db.add(chart)
        db.commit()
        db.refresh(chart)

    return chart  # SQLAlchemy object


def build_chart_response(chart: Chart) -> dict:
    """It will convert the chart to dict with calculated prices"""
    items_response = []
    total = 0

    for item in chart.items:
        subtotal = item.quantity * item.unit_price
        total += subtotal
        items_response.append({
            "id": item.id,
            "book_id": item.book_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": subtotal
        })

    return {
        "id": chart.id,
        "user_id": chart.user_id,
        "active": chart.active,
        "items": items_response,
        "total": total
    }


# SEE CHART
@router.get("/", response_model=ChartResponse)
def see_chart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):    
    chart = get_or_create_chart(user, db)
    return build_chart_response(chart)


# PUT ITEM
@router.post("/itens", response_model=ChartResponse, status_code=201)
def put_item(item: ChartItemCreate, db: Session = Depends(get_db), user: User = Depends(require_client)):
    chart = get_or_create_chart(user, db)  # SQLAlchemy object

    book = db.query(Item).filter(Item.id == item.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # it will verify if the item already exists
    existent_item = db.query(ChartItem).filter(
        ChartItem.chart_id == chart.id,
        ChartItem.book_id == item.book_id
    ).first()

    total_quantity = item.quantity
    if existent_item:
        total_quantity += existent_item.quantity

    if total_quantity > book.stock:
        raise HTTPException(
            status_code=400, 
            detail=f"Stock not available. Available: {book.stock}, Requested: {total_quantity}"
        )

    if existent_item:
        existent_item.quantity += item.quantity
        db.commit()
        db.refresh(chart)
        return build_chart_response(chart)

    new_item = ChartItem(
        chart_id=chart.id,
        book_id=item.book_id,
        quantity=item.quantity,
        unit_price=book.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(chart)
    return build_chart_response(chart)


# UPDATE ITEM
@router.put("/itens/{item_id}", response_model=ChartResponse)
def update_item(item_id: int, data: ChartItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chart = get_or_create_chart(user, db)

    item = db.query(ChartItem).filter(
        ChartItem.id == item_id,
        ChartItem.chart_id == chart.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in the chart")

    # Stock validation
    book = db.query(Item).filter(Item.id == item.book_id).first()
    if data.quantity > book.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Stock not available. Available: {book.stock}, Requested: {data.quantity}"
        )
    
    if data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = data.quantity

    db.commit()
    db.refresh(chart)
    return build_chart_response(chart)


# REMOVE ITEM
@router.delete("/itens/{item_id}", response_model=ChartResponse)
def remove_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chart = get_or_create_chart(user, db)

    item = db.query(ChartItem).filter(
        ChartItem.id == item_id,
        ChartItem.chart_id == chart.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in the chart")

    db.delete(item)
    db.commit()
    db.refresh(chart)
    return build_chart_response(chart)


# CLEAR CHART
@router.delete("/", response_model=ChartResponse)
def clear_chart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chart = get_or_create_chart(user, db)

    for item in chart.items:
        db.delete(item)

    db.commit()
    db.refresh(chart)
    return build_chart_response(chart)


# CHECKOUT
@router.post("/checkout", response_model=ChartResponse)
def checkout(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chart = get_or_create_chart(user, db)

    if not chart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # stock's final validation
    for item in chart.items:
        book = db.query(Item).filter(Item.id == item.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail=f"Book {item.book_id} not found")
        if book.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock not available for '{book.name}'. Available: {book.stock}, Requested: {item.quantity}"
            )

    # it will decrease each book stock
    for item in chart.items:
        book = db.query(Item).filter(Item.id == item.book_id).first()
        book.stock -= item.quantity

    chart.active = False
    db.commit()
    db.refresh(chart)
    return build_chart_response(chart)


# PURCHASE HISTORY
@router.get("/history", response_model=list[ChartResponse])
def purchase_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    charts = db.query(Chart).filter(
        Chart.user_id == user.id,
        Chart.active == False
    ).all()
    return [build_chart_response(chart) for chart in charts] 