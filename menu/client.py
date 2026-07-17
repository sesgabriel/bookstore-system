import json
import os
import requests
from languages import get_texts

BASE_URL = "http://127.0.0.1:8000"
SESSION_FILE = ".session.json"

token = None
lang = "pt"
t = get_texts("pt")
user_type = None


def load_session():
    """Load saved session from file if exists."""
    global token, user_type
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                session = json.load(f)
                token = session.get("token")

                if token:
                    me_resp = requests.get(
                        f"{BASE_URL}/auth/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if me_resp.status_code == 200:
                        user_type = me_resp.json()["type"]
                        print(f"🔑 Auto-login: {user_type}")
                        return True
                    else:
                        clear_session()
                        return False
        except Exception:
            clear_session()
    return False


def save_session():
    """Save current session to file."""
    if token and user_type:
        session = {"token": token, "user_type": user_type}
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session, f)


def clear_session():
    """Remove saved session file."""
    global token, user_type
    token = None
    user_type = None
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def select_language():
    """Display language selection screen before the main program starts."""
    global lang, t
    print("\n" + "=" * 40)
    print(t["select_language"])
    print(t["option_pt"])
    print(t["option_en"])
    print("=" * 40)

    while True:
        choice = input("> ").strip()
        if choice == "1":
            lang = "pt"
            t = get_texts("pt")
            print(f"\n✅ {t['option_pt'].replace('1. ', '')}")
            return
        elif choice == "2":
            lang = "en"
            t = get_texts("en")
            print(f"\n✅ {t['option_en'].replace('2. ', '')}")
            return
        else:
            print(t["invalid_option"])


def get_input(prompt, required=True):
    """Get user input with validation for required fields."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print(t["required_field"])


def is_logged_in():
    """Check if user has a valid token."""
    return token is not None


def get_user_info():
    """Fetch and display logged-in user information."""
    if not is_logged_in():
        return None

    headers = get_headers()
    if not headers:
        return None

    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return None


def display_user_panel():
    """Display user info panel at the top of the menu."""
    if not is_logged_in():
        print("\n" + "─" * 40)
        print(f"   {t['not_logged_in']}")
        print("─" * 40)
        return

    user_info = get_user_info()
    if not user_info:
        print("\n" + "─" * 40)
        print(f"   {t['user_info_error']}")
        print("─" * 40)
        return

    # Get purchase count for clients
    purchase_count = 0
    if user_type == "client":
        headers = get_headers()
        history_resp = requests.get(f"{BASE_URL}/chart/history", headers=headers)
        if history_resp.status_code == 200:
            purchase_count = len(history_resp.json())

    print("\n" + "─" * 40)
    print(f"   👤 {user_info['name']}")
    print(f"   📧 {user_info['email']}")
    print(f"   🏷️  {user_info['type'].upper()}")

    if user_type == "client":
        print(f"   {t['purchases']}: {purchase_count}")

    print("─" * 40)


def menu():
    """Display dynamic menu with sequential numbering based on user type."""
    display_user_panel()
    print("\n" + "=" * 40)
    print(t["welcome"])
    print("=" * 40)

    if not is_logged_in():
        # Not logged in - show only public options
        print(t["menu_list_books"])
        print(t["menu_view_book"])
        print(t["menu_register"])
        print(t["menu_login"])
    elif user_type == "seller":
        # Seller menu - sequential numbering
        print(t["menu_list_books"])
        print(t["menu_view_book"])
        print(t["menu_add_book"])
        print(t["menu_edit_book"])
        print(t["menu_delete_book"])
        print(t["menu_sales_history"])
        print(t["menu_logout"])
    else:
        # Client menu - sequential numbering
        print(t["menu_list_books"])
        print(t["menu_view_book"])
        print(t["menu_view_cart"])
        print(t["menu_add_cart"])
        print(t["menu_update_cart"])
        print(t["menu_remove_cart"])
        print(t["menu_clear_cart"])
        print(t["menu_checkout"])
        print(t["menu_history"])
        print(t["menu_logout"])

    print(t["menu_exit"])
    print("=" * 40)


def register_user():
    """Register a new user (client or seller)."""
    print(f"\n{t['register_title']}")
    name = get_input(t["name"])
    email = get_input(t["email"])
    password = get_input(t["password"])

    print(t["user_type"])
    type_choice = get_input("> ")
    user_type_selected = "client" if type_choice == "1" else "seller"

    data = {"name": name, "email": email, "password": password, "type": user_type_selected}
    resp = requests.post(f"{BASE_URL}/auth/signup", json=data)

    if resp.status_code == 201:
        print(t["register_success"])
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


def login():
    """Authenticate user and store JWT token persistently."""
    global token, user_type
    print(f"\n{t['login_title']}")

    print(f"{t['login_json']} | {t['login_oauth']}")
    choice = get_input("> ")

    if choice == "1":
        email = get_input(t["email"])
        password = get_input(t["password"])
        data = {"email": email, "password": password}
        resp = requests.post(f"{BASE_URL}/auth/login-json", json=data)
    else:
        email = get_input("Email (username): ")
        password = get_input(t["password"])
        data = {"username": email, "password": password}
        resp = requests.post(f"{BASE_URL}/auth/login", data=data)

    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(t["login_success"])

        me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
        if me_resp.status_code == 200:
            user_type = me_resp.json()["type"]
            print(f"   Logged in as: {user_type}")
        else:
            print("⚠️ Could not fetch user type, defaulting to client")
            user_type = "client"

        save_session()
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


def logout():
    """Clear current session and remove saved token."""
    clear_session()
    print("👋 Logged out.")


def get_headers():
    """Return authorization headers with JWT token."""
    if not token:
        print(t["login_first"])
        return None
    return {"Authorization": f"Bearer {token}"}


def require_login(func):
    """Decorator to ensure user is logged in before executing action."""
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            print(t["login_first"])
            return
        return func(*args, **kwargs)
    return wrapper


@require_login
def add_book():
    """Add a new book to the marketplace (seller only)."""
    headers = get_headers()
    if not headers:
        return

    print(f"\n{t['add_book_title']}")
    name = get_input(t["book_name"])
    description = get_input(t["description"])
    author = get_input(t["author"])
    price = float(get_input(t["price"]))
    stock = int(get_input(t["stock"]))

    data = {
        "name": name,
        "description": description,
        "author": author,
        "price": price,
        "stock": stock
    }
    resp = requests.post(f"{BASE_URL}/books/", json=data, headers=headers)

    if resp.status_code == 201:
        print(t["book_added"])
        print(resp.json())
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


def list_books():
    """List books with optional filters (no login required)."""
    print(f"\n{t['list_books_title']}")
    print(t["filter_hint"])

    name = get_input(t["filter_name"], required=False) or None
    author = get_input(t["filter_author"], required=False) or None

    min_price_input = get_input(t["filter_min_price"], required=False)
    max_price_input = get_input(t["filter_max_price"], required=False)

    params = {}
    if name:
        params["name"] = name
    if author:
        params["author"] = author
    if min_price_input:
        params["min_price"] = float(min_price_input)
    if max_price_input:
        params["max_price"] = float(max_price_input)

    resp = requests.get(f"{BASE_URL}/books/", params=params)

    if resp.status_code == 200:
        books = resp.json()
        if not books:
            print(t["no_purchases"].format(item="livro" if lang == "pt" else "book"))
            return

        print(f"\n{t['books_found'].format(count=len(books), item='livro' if lang == 'pt' else 'book')}")
        for book in books:
            print(f"  ID: {book['id']} | {book['name']} | {t['author'].replace(': ', '')}: {book.get('author', 'N/A')} | R$ {book['price']:.2f} | {t['stock'].replace(': ', '')}: {book['stock']}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


def view_book():
    """View detailed information about a specific book (no login required)."""
    book_id = get_input(t["book_id"])
    resp = requests.get(f"{BASE_URL}/books/{book_id}")

    if resp.status_code == 200:
        book = resp.json()
        print(f"\n{t['view_book_title']} {book['name']}")
        print(f"   {t['author'].replace(': ', '')}: {book.get('author', 'N/A')}")
        print(f"   {t['description'].replace(': ', '')}: {book['description']}")
        print(f"   {t['price'].replace(' (ex: 29.90)', '')}: R$ {book['price']:.2f}")
        print(f"   {t['stock'].replace(': ', '')}: {book['stock']}")
    else:
        print(f"{t['error']}: {resp.status_code}")


@require_login
def edit_book():
    """Edit an existing book (seller only, must own the book)."""
    headers = get_headers()
    if not headers:
        return

    book_id = get_input(t["book_id"])

    print(t["edit_hint"])
    name = get_input(t["book_name"], required=False)
    description = get_input(t["description"], required=False)
    author = get_input(t["author"], required=False)
    price_input = get_input(t["price"], required=False)
    stock_input = get_input(t["stock"], required=False)

    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    if author:
        data["author"] = author
    if price_input:
        data["price"] = float(price_input)
    if stock_input:
        data["stock"] = int(stock_input)

    resp = requests.put(f"{BASE_URL}/books/{book_id}", json=data, headers=headers)

    if resp.status_code == 200:
        print(t["updated"])
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def delete_book():
    """Delete a book from the marketplace (seller only, must own the book)."""
    headers = get_headers()
    if not headers:
        return

    book_id = get_input(t["book_id"])
    resp = requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)

    if resp.status_code == 204:
        print(t["deleted"])
    else:
        print(f"{t['error']}: {resp.status_code}")


@require_login
def view_cart():
    """View current active shopping cart with book names (client only)."""
    headers = get_headers()
    if not headers:
        return

    resp = requests.get(f"{BASE_URL}/chart/", headers=headers)

    if resp.status_code == 200:
        chart = resp.json()
        status = t["cart_active"] if chart["active"] else t["cart_finished"]
        print(f"\n{t['cart_title']} #{chart['id']} | {status}")
        if not chart["items"]:
            print(f"   {t['cart_empty']}")
            return

        for item in chart["items"]:
            # Fetch book details to get the name
            book_resp = requests.get(f"{BASE_URL}/books/{item['book_id']}", headers=headers)
            book_name = "Unknown"
            if book_resp.status_code == 200:
                book_name = book_resp.json().get("name", "Unknown")
            print(f"   📖 {book_name} | Qty: {item['quantity']} | R$ {item['subtotal']:.2f}")
        print(f"   {t['cart_total']}: R$ {chart['total']:.2f}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def add_to_cart():
    """Add a book to the shopping cart with search functionality (client only)."""
    headers = get_headers()
    if not headers:
        return

    print(f"\n{t['add_cart_title']}")
    print(t["filter_hint"])

    # Search for books
    name = get_input(t["filter_name"], required=False) or None
    author = get_input(t["filter_author"], required=False) or None

    params = {}
    if name:
        params["name"] = name
    if author:
        params["author"] = author

    resp = requests.get(f"{BASE_URL}/books/", params=params)

    if resp.status_code != 200:
        print(f"{t['error']}: {resp.status_code}")
        return

    books = resp.json()
    if not books:
        print(t["no_purchases"].format(item="livro" if lang == "pt" else "book"))
        return

    # Show results
    print(f"\n📚 {len(books)} {t['books_found']}:")
    for i, book in enumerate(books, 1):
        print(f"  {i}. ID: {book['id']} | {book['name']} | {t['author'].replace(': ', '')}: {book.get('author', 'N/A')} | R$ {book['price']:.2f} | {t['stock'].replace(': ', '')}: {book['stock']}")

    # User selects by number or ID
    selection = get_input(t["select_book"])

    try:
        idx = int(selection) - 1
        if 0 <= idx < len(books):
            selected_book = books[idx]
        else:
            selected_book = next((b for b in books if str(b['id']) == selection), None)
    except ValueError:
        selected_book = next((b for b in books if str(b['id']) == selection), None)

    if not selected_book:
        print(t["book_not_found_results"])
        return

    book_id = selected_book['id']
    print(f"\n{t['selected']}: {selected_book['name']} | R$ {selected_book['price']:.2f}")

    # Ask quantity
    max_stock = selected_book['stock']
    quantity_input = get_input(f"{t['quantity']} ({t['max_stock']} {max_stock}): ")
    quantity = int(quantity_input) if quantity_input else 1

    if quantity > max_stock:
        print(f"{t['stock_error']} {max_stock} {t['in_stock']}")
        return

    # Add to cart
    data = {"book_id": book_id, "quantity": quantity}
    resp = requests.post(f"{BASE_URL}/chart/itens", json=data, headers=headers)

    if resp.status_code == 201:
        print(t["item_added"])
        chart = resp.json()
        print(f"   {t['cart_total_label']}: R$ {chart['total']:.2f}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")

@require_login
def update_cart_item():
    """Update quantity of an item in the cart (client only)."""
    headers = get_headers()
    if not headers:
        return

    item_id = get_input("Item ID: ")
    quantity = int(get_input(t["new_quantity"]))

    data = {"quantity": quantity}
    resp = requests.put(f"{BASE_URL}/chart/itens/{item_id}", json=data, headers=headers)

    if resp.status_code == 200:
        print(t["updated"])
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def remove_from_cart():
    """Remove an item from the shopping cart (client only)."""
    headers = get_headers()
    if not headers:
        return

    item_id = get_input("Item ID: ")
    resp = requests.delete(f"{BASE_URL}/chart/itens/{item_id}", headers=headers)

    if resp.status_code == 200:
        print(t["item_removed"])
    else:
        print(f"{t['error']}: {resp.status_code}")


@require_login
def clear_cart():
    """Remove all items from the shopping cart (client only)."""
    headers = get_headers()
    if not headers:
        return

    confirm = get_input(t["delete_confirm"])
    confirm_key = "s" if lang == "pt" else "y"
    if confirm.lower() != confirm_key:
        print(t["cancelled"])
        return

    resp = requests.delete(f"{BASE_URL}/chart/", headers=headers)

    if resp.status_code == 200:
        print(t["cart_cleared"])
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def checkout():
    """Finalize purchase and deactivate cart (client only)."""
    headers = get_headers()
    if not headers:
        return

    confirm = get_input(t["confirm_purchase"])
    confirm_key = "s" if lang == "pt" else "y"
    if confirm.lower() != confirm_key:
        print(t["cancelled"])
        return

    resp = requests.post(f"{BASE_URL}/chart/checkout", headers=headers)

    if resp.status_code == 200:
        chart = resp.json()
        print(t["purchase_success"])
        print(f"   {t['total_paid']}: R$ {chart['total']:.2f}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def purchase_history():
    """View client's purchase history with book names (client only)."""
    headers = get_headers()
    if not headers:
        return

    resp = requests.get(f"{BASE_URL}/chart/history", headers=headers)

    if resp.status_code == 200:
        charts = resp.json()
        if not charts:
            print(t["no_purchases"])
            return

        print(f"\n{t['history_title']}")
        print(f"📜 {len(charts)} {t['purchase']}(s):")
        for chart in charts:
            print(f"\n  {t['purchase']} #{chart['id']} | {t['cart_total']}: R$ {chart['total']:.2f}")
            for item in chart["items"]:
                # Fetch book details to get the name
                book_resp = requests.get(f"{BASE_URL}/books/{item['book_id']}", headers=headers)
                book_name = "Unknown"
                if book_resp.status_code == 200:
                    book_name = book_resp.json().get("name", "Unknown")
                print(f"    📖 {book_name} | Qty: {item['quantity']} | R$ {item['subtotal']:.2f}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


@require_login
def sales_history():
    """View seller's sales history with book names and revenue."""
    headers = get_headers()
    if not headers:
        return

    resp = requests.get(f"{BASE_URL}/seller/sales", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n📊 {t['sales_history_title']}")
        print(f"   {t['total_books_sold']}: {data['total_books_sold']}")
        print(f"   {t['total_revenue']}: R$ {data['total_revenue']:.2f}")
        
        if not data['books_sold']:
            print(f"\n   {t['no_sales']}")
            return
        
        print(f"\n   {t['books_sold']}:")
        for book in data['books_sold']:
            print(f"      📖 {book['book_name']}")
            print(f"         {t['qty_sold']}: {book['quantity_sold']}")
            print(f"         {t['unit_price']}: R$ {book['unit_price']:.2f}")
            print(f"         {t['revenue']}: R$ {book['revenue']:.2f}")
    else:
        print(f"{t['error']}: {resp.status_code} - {resp.text}")


def main():
    """Main entry point - starts with language selection and auto-login."""
    select_language()

    if load_session():
        print(f"\n🚀 {t['welcome']}")
        print(f"   Logged in as: {user_type}")
    else:
        print(f"\n🚀 {t['welcome']}")
        print("   Not logged in")

    while True:
        menu()
        choice = get_input(t["choice_prompt"])

        # Route actions based on user type and menu choice
        if not is_logged_in():
            actions = {
                "1": list_books,
                "2": view_book,
                "3": register_user,
                "4": login,
                "0": lambda: print(t["exit"]) or exit()
            }
        elif user_type == "seller":
            actions = {
                "1": list_books,
                "2": view_book,
                "3": add_book,
                "4": edit_book,
                "5": delete_book,
                "6": sales_history,
                "7": logout,
                "0": lambda: print(t["exit"]) or exit()
            }
        else:  # client
            actions = {
                "1": list_books,
                "2": view_book,
                "3": view_cart,
                "4": add_to_cart,
                "5": update_cart_item,
                "6": remove_from_cart,
                "7": clear_cart,
                "8": checkout,
                "9": purchase_history,
                "10": logout,
                "0": lambda: print(t["exit"]) or exit()
            }

        action = actions.get(choice)
        if action:
            action()
        else:
            print(t["invalid_option"])


if __name__ == "__main__":
    main()