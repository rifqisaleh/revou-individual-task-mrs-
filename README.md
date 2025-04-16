# Greenmarket Backend

## Directory

- [🔹 Overview](#overview)
- [🔹 Features Implemented](#features-implemented)
- [🔹 Installation and Setup](#installation-and-setup)
- [🔹 API Access Rundown](#api-access-rundown)
- [🔹 Available Endpoints](#available-endpoints)
- [🔹 Testing Setup & Safety Notes](#testing-setup--safety-notes)

---

## Overview

Greenmarket Backend is the server-side system for a sustainable marketplace platform. It handles user registration and authentication, product listing and management, cart handling, and checkout order processing.

It is designed to support role-based access (user, seller, admin), efficient product filtering and pagination, and safe transaction workflows.

---

## Features Implemented

- **User Management**: JWT-based login and registration with role-based access.
- **Product Catalog**:
  - CRUD operations for sellers/admins.
  - Public listing with filtering, sorting, and pagination.
- **Shopping Cart**: Add, remove, and view cart items per user.
- **Order Checkout**: Convert cart to order with stock management.
- **Admin Control**: Update order status via role-restricted endpoints.
- **Testing**: Full test suite using `pytest` and in-memory database.

---

## Installation and Setup

### Prerequisites

- Python 3.11+
- `uv` package manager (or `pip`)
- WSL (recommended for Windows users)

### Clone the Repository

```bash
git clone https://github.com/rifqisaleh/revou-individual-task-mrs-.git
cd revou-individual-task-mrs-
```

### Set Up Virtual Environment

```bash
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Dependencies

```bash
uv pip install -r requirements.txt
# or
uv sync
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=your_postgres_or_sqlite_url
JWT_SECRET_KEY=supersecretkey
```

### Start the Server

```bash
python -m app.main
# or
FLASK_APP=app/main.py flask run --debug
```

---

## API Access Rundown

Authentication is required to access protected endpoints. Each JWT contains the user's ID and role, and authorization is enforced at the route level.

Roles supported:
- **user**
- **seller**
- **admin**

Use the JWT token in the `Authorization` header like:

```
Authorization: Bearer <your_token_here>
```

---

## Available Endpoints

### 🔐 Auth
- `POST /register` – Register a new user.
- `POST /login` – Login and receive a JWT.

### 📦 Products
- `GET /products/` – Public product listing
  - Supports: `?min_price=`, `max_price=`, `in_stock=`, `seller_id=`, `sort_by=`, `order=`, `page=`, `limit=`
- `GET /products/<id>` – Get product details
- `POST /products/` – Create product (seller/admin only)
- `PUT /products/<id>` – Update product (owner or admin only)
- `DELETE /products/<id>` – Delete product (owner or admin only)

### 🛒 Cart
- `GET /cart/` – View current cart
- `POST /cart/` – Add product to cart
- `DELETE /cart/<item_id>/` – Remove item from cart

### 🧾 Orders
- `POST /orders/checkout` – Checkout and create an order from cart
- `GET /orders/me` – View user’s order history
- `GET /orders/<id>` – View a specific order
- `PATCH /orders/<id>` – Update order status (admin/seller only)

---

## Testing Setup & Safety Notes

All tests run in an **isolated in-memory SQLite database** and will not affect any external or real database.

### Test Configuration

Configured via `conftest.py` to override the database for tests:

```python
app.config.update({
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
})
```

### Running Tests

Simply run:

```bash
pytest
```

To view code coverage:

```bash
pytest --cov=app
```

> All test data is automatically discarded after each test run.

---

For project questions, contact [mrifqisaleh@gmail.com] or visit the repository.