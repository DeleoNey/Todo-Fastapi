# ✅ Todo App (FastAPI + Streamlit)

A **Todo application** built with **FastAPI** as backend and **Streamlit** as frontend.
Supports **user registration**, **JWT authentication**, **roles** (`user` / `admin`) and full CRUD operations for todos.

---

## 🛠 Stack

* **Backend:** FastAPI, SQLAlchemy
* **Frontend:** Streamlit
* **Database:** SQLite (default) / PostgreSQL
* **Authentication:** JWT (Bearer Token)
* **Password hashing:** bcrypt

---

## ⚙ Features

* User registration and login
* JWT authentication
* Roles:

  * `user` → CRUD only for own todos
  * `admin` → view, edit, delete all todos
* Create, update, delete todos
* Light theme frontend
* Automatic session handling in Streamlit

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DeleoNey/Todo-Fastapi.git
cd Todo-Fastapi
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If no `requirements.txt`:

```bash
pip install fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose streamlit
```

### 4. Database setup

* Default: SQLite (`database.py`)

* For PostgreSQL: update `SQLALCHEMY_DATABASE_URL` in `database.py`

* Create tables:

```python
from database import Base, engine
from models import Users, Todos

Base.metadata.create_all(bind=engine)
```

### 5. Start FastAPI backend

```bash
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

### 6. Start Streamlit frontend

```bash
streamlit run streamlit_app/main.py
```

Frontend runs at:

```
http://localhost:8501
```

---

## 🔗 API Endpoints

### Auth

| Method | Endpoint      | Description                 |
| ------ | ------------- | --------------------------- |
| POST   | `/auth/`      | Create a new user           |
| POST   | `/auth/token` | Login and receive JWT token |

### Users

| Method | Endpoint          | Description           |
| ------ | ----------------- | --------------------- |
| GET    | `/users/`         | Get current user info |
| PUT    | `/users/password` | Change password       |

### Todos

| Method | Endpoint                | Description                       |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/todos/`               | Get all todos of the current user |
| GET    | `/todos/todo/{todo_id}` | Get a specific todo               |
| POST   | `/todos/todo`           | Create a new todo                 |
| PUT    | `/todos/todo/{todo_id}` | Update a todo                     |
| DELETE | `/todos/todo/{todo_id}` | Delete a todo                     |

### Admin

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| GET    | `/admin/todo`           | Get all todos (admin only)   |
| DELETE | `/admin/todo/{todo_id}` | Delete any todo (admin only) |

> All endpoints (except registration and login) require JWT token in header:

```
Authorization: Bearer <your_token>
```

---

## 🖥 Streamlit Interface

* **Login** – user authentication
* **Register** – create a new user
* **Todos** – view, add, edit, delete own todos
* **Admin Panel** – view/edit/delete all todos (admin only)
* **Profile** – display current user info

---

## 🔑 JWT Token

* Token expires in **20 minutes**
* Include token in requests:

```
Authorization: Bearer <token>
```

---

## 📝 Examples (Python Requests)

```python
import requests

API_URL = "http://127.0.0.1:8000"

# Login
r = requests.post(f"{API_URL}/auth/token", data={"username": "test", "password": "1234"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get current user
r = requests.get(f"{API_URL}/users/", headers=headers)
print(r.json())

# Create todo
r = requests.post(f"{API_URL}/todos/todo",
                  json={"title": "Test", "description": "Demo", "priority": 3, "complete": False},
                  headers=headers)
print(r.status_code)

# Get all todos
r = requests.get(f"{API_URL}/todos/", headers=headers)
print(r.json())
```

---

## ⚡ Notes

* Default database is SQLite for simplicity
* Passwords are stored hashed using **bcrypt**
* Frontend automatically handles expired JWT and redirects to login
* Light theme is enabled in Streamlit
