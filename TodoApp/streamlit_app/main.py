import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# ---- Ініціалізація session_state ----
if "token" not in st.session_state:
    st.session_state["token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "role" not in st.session_state:
    st.session_state["role"] = None
if "edit_todo" not in st.session_state:
    st.session_state["edit_todo"] = None

# st.markdown("""
# <style>
#     body {background-color: #f9f9f9; color: #222;}
#     .stApp {background-color: #ffffff;}
# </style>
# """, unsafe_allow_html=True)
# ---- Світлий фон ----


# ---- Функції ----
def login():
    st.subheader("🔑 Логін")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Увійти"):
        response = requests.post(
            f"{API_URL}/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token

            # отримуємо роль користувача
            headers = {"Authorization": f"Bearer {token}"}
            user_resp = requests.get(f"{API_URL}/users/", headers=headers)
            if user_resp.status_code == 200:
                st.session_state["role"] = user_resp.json()["role"]

            st.success("Успішний вхід!")
            st.session_state["page"] = "todos"
            st.rerun()
        else:
            st.error("Невірний логін або пароль")


def register():
    st.subheader("📝 Реєстрація")
    username = st.text_input("Username (new)")
    email = st.text_input("Email")
    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["user", "admin"])
    if st.button("Зареєструвати"):
        response = requests.post(
            f"{API_URL}/auth/",
            json={
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "role": role,
            },
        )
        if response.status_code == 201:
            st.success("Користувач створений! Тепер увійди.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error(f"Помилка: {response.text}")


def handle_401(resp):
    if resp.status_code == 401:
        st.session_state["token"] = None
        st.session_state["role"] = None
        st.session_state["page"] = "login"
        st.error("Сесія закінчилась. Увійдіть знову.")
        st.rerun()


def todos(all_todos=False):
    st.subheader("📋 Todos")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    # Отримання todos
    url = f"{API_URL}/todos/"
    if all_todos:
        url = f"{API_URL}/admin/todo"

    resp = requests.get(url, headers=headers)
    handle_401(resp)
    if resp.status_code == 200:
        todos = resp.json()
        for t in todos:
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"**{t['title']}** — {t['description']} | "
                         f"Пріоритет: {t['priority']} | Завершено: {t['complete']}")
            with col2:
                if st.button("📝 Редагувати", key=f"edit_{t['id']}"):
                    st.session_state["edit_todo"] = t
                    st.session_state["page"] = "edit_todo"
                    st.rerun()
            with col3:
                if st.button("❌ Видалити", key=f"del_{t['id']}"):
                    del_resp = requests.delete(f"{API_URL}/todos/todo/{t['id']}", headers=headers)
                    handle_401(del_resp)
                    if del_resp.status_code == 204:
                        st.success("Видалено")
                        st.rerun()
    else:
        st.error("Не вдалося отримати todos")

    # Додавання нового todo (тільки для user)
    if not all_todos:
        st.write("---")
        st.subheader("➕ Додати Todo")
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.slider("Priority", 1, 5, 3)
        complete = st.checkbox("Complete")
        if st.button("Додати"):
            add_resp = requests.post(
                f"{API_URL}/todos/todo",
                json={"title": title, "description": description, "priority": priority, "complete": complete},
                headers=headers
            )
            handle_401(add_resp)
            if add_resp.status_code == 201:
                st.success("Todo додано!")
                st.rerun()


def edit_todo():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    t = st.session_state["edit_todo"]
    st.subheader(f"✏️ Редагувати Todo #{t['id']}")

    title = st.text_input("Title", value=t["title"])
    description = st.text_area("Description", value=t["description"])
    priority = st.slider("Priority", 1, 5, t["priority"])
    complete = st.checkbox("Complete", value=t["complete"])

    if st.button("Зберегти"):
        upd_resp = requests.put(
            f"{API_URL}/todos/todo/{t['id']}",
            json={"title": title, "description": description, "priority": priority, "complete": complete},
            headers=headers
        )
        handle_401(upd_resp)
        if upd_resp.status_code == 204:
            st.success("Todo оновлено!")
            st.session_state["page"] = "todos"
            st.rerun()


def profile():
    st.subheader("👤 Профіль")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(f"{API_URL}/users/", headers=headers)
    handle_401(resp)
    if resp.status_code == 200:
        st.json(resp.json())
    else:
        st.error("Не вдалося отримати профіль")


# ---- Головна функція ----
def main():
    st.title("✅ Todo App (FastAPI + Streamlit)")

    if st.session_state["token"]:
        # формуємо меню для увійшлого користувача
        menu = ["Todos", "Profile", "Logout"]
        if st.session_state.get("role") == "admin":
            menu.insert(1, "Admin Panel")

        # захист від ValueError: якщо сторінка не в меню, ставимо за замовчуванням
        if st.session_state.get("page") not in menu:
            st.session_state["page"] = "Todos"

        choice = st.sidebar.radio("Меню", menu, index=menu.index(st.session_state["page"]))

        # обробка вибору
        if choice == "Todos":
            st.session_state["page"] = "Todos"
            todos()
        elif choice == "Admin Panel":
            st.session_state["page"] = "Admin Panel"
            todos(all_todos=True)
        elif choice == "Profile":
            st.session_state["page"] = "Profile"
            profile()
        elif choice == "Logout":
            st.session_state["token"] = None
            st.session_state["role"] = None
            st.session_state["page"] = "Login"
            st.rerun()

    else:
        # меню для неавторизованого користувача
        menu = ["Login", "Register"]
        if st.session_state.get("page") not in menu:
            st.session_state["page"] = "Login"

        choice = st.sidebar.radio("Меню", menu, index=menu.index(st.session_state["page"]))

        if choice == "Login":
            st.session_state["page"] = "Login"
            login()
        elif choice == "Register":
            st.session_state["page"] = "Register"
            register()

    # окремо сторінка редагування todo
    if st.session_state.get("page") == "edit_todo":
        edit_todo()

if __name__ == "__main__":
    main()
