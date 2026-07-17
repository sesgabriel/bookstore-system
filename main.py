from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models import book, users
from routers import books, auth, chart, seller

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Bookstore API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(auth.router)
app.include_router(chart.router)
app.include_router(seller.router)

@app.get("/")
def root():
    return {"message": "Marketplace API is running"}