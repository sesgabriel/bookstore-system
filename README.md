# 📚 Bookstore Marketplace

A complete e-commerce platform for buying and selling books with a RESTful API built with FastAPI and a feature-rich CLI client.

---

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication
- Role-based access control (Client / Seller)
- Password hashing with bcrypt
- Session persistence via `.session.json`
- OAuth2 and JSON login endpoints

### 📚 Book Management (Sellers)
- Create, edit, and delete books
- Sales analytics dashboard
- Per-book sales metrics

### 🛒 Shopping Cart (Clients)
- Add/remove items
- Update quantities
- Checkout with stock validation
- Purchase history

### 🌍 Additional Features
- Advanced book search (name, author, price range)
- Multilingual support (🇧🇷 PT / 🇺🇸 EN)
- Interactive CLI with dynamic menus
- User profile with purchase count

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **Pydantic** - Data validation

### Client
- **Requests** - HTTP client
- **i18n** - Internationalization

---

## 📂 Project Structure

```
bookstore-marketplace/
├── backend/
│   ├── main.py              # API entry point
│   ├── database.py          # DB configuration
│   ├── auth.py              # JWT & password utilities
│   ├── dependencies.py      # Dependency injection
│   ├── models/              # SQLAlchemy models
│   │   ├── users.py
│   │   ├── book.py
│   │   └── chart.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── users.py
│   │   ├── book.py
│   │   └── chart.py
│   └── routers/             # API routes
│       ├── auth.py
│       ├── books.py
│       ├── chart.py
│       └── seller.py
└── client/
    ├── client.py            # CLI application
    └── languages.py         # Translations
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8+

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/bookstore-marketplace.git
cd bookstore-marketplace/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy passlib python-jose bcrypt pydantic

# Run server
uvicorn main:app --reload
```

### Client Setup

```bash
cd ../client
pip install requests
python client.py
```

---

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register user |
| POST | `/auth/login` | OAuth2 login |
| POST | `/auth/login-json` | JSON login |
| GET | `/auth/me` | Current user info |

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books/` | Create book (seller) |
| GET | `/books/` | List books with filters |
| GET | `/books/{id}` | Get book details |
| PUT | `/books/{id}` | Update book (seller) |
| DELETE | `/books/{id}` | Delete book (seller) |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chart/` | View active cart |
| POST | `/chart/itens` | Add item |
| PUT | `/chart/itens/{id}` | Update quantity |
| DELETE | `/chart/itens/{id}` | Remove item |
| DELETE | `/chart/` | Clear cart |
| POST | `/chart/checkout` | Checkout |
| GET | `/chart/history` | Purchase history |

### Seller
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/seller/sales` | Sales statistics |

---

## 🎯 Usage

### Quick Start

1. Start server: `uvicorn main:app --reload`
2. Run client: `python client.py`
3. Select language
4. Register as client or seller
5. Login and start using!

### Seller Actions
- Add books with name, description, author, price, stock
- Edit/delete only your books
- View sales analytics

### Client Actions
- Browse books with filters
- Add to cart
- Update quantities
- Checkout
- View purchase history

---

## 🔒 Security

- JWT authentication for all protected endpoints
- Role-based access control
- Input validation with Pydantic
- Stock validation prevents overselling
- Inactive accounts blocked from access

---

## 🌍 Internationalization

Supported languages:
- 🇧🇷 Portuguese
- 🇺🇸 English

Add new languages by extending the `TEXTS` dictionary in `languages.py`.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request


---

## 📧 Contact

Open an issue for questions or suggestions.

---

**Built with ❤️ using FastAPI**
