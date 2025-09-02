import streamlit as st
from views.login import LoginPage
from views.register import RegisterPage
from views.chatbot import OptimizedChatbotUI
from views.admin import AdminPage
from dotenv import load_dotenv
from utils.cookies import set_cookie, get_cookie
from backend.auth import AuthManager
import os
import pickle
import time

load_dotenv()

def save_session_state():
    """Sauvegarder l'état de la session dans un fichier temporaire."""
    try:
        time.sleep(0.1)
        with open("session_state.pkl", "wb") as f:
            pickle.dump({
                "page": st.session_state.get("page", "login"),
                "logged_in": st.session_state.get("logged_in", False),
                "username": st.session_state.get("username", None),
                "role": st.session_state.get("role", None)
            }, f)
    except Exception:
        pass

def load_session_state(auth_manager):
    """Charger l'état de la session depuis un fichier temporaire."""
    try:
        if os.path.exists("session_state.pkl"):
            with open("session_state.pkl", "rb") as f:
                state = pickle.load(f)
                if state.get("logged_in") and state.get("username"):
                    success, _, user, role = auth_manager.check_user_exists(state["username"])
                    if success:
                        st.session_state.page = state.get("page", "login")
                        st.session_state.logged_in = state.get("logged_in", False)
                        st.session_state.username = state.get("username", None)
                        st.session_state.role = state.get("role", None)
                    else:
                        st.session_state.page = "login"
                        st.session_state.logged_in = False
                        st.session_state.username = None
                        st.session_state.role = None
                        set_cookie("username", "", max_age=0)
                        if os.path.exists("session_state.pkl"):
                            os.remove("session_state.pkl")
                else:
                    st.session_state.page = "login"
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.role = None
        else:
            pass
    except Exception:
        st.session_state.page = "login"
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None

def main():
    auth_manager = AuthManager()

    if "page" not in st.session_state:
        load_session_state(auth_manager)
        if "page" not in st.session_state:
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None

    save_session_state()

    if st.session_state.page == "login":
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.page == "register":
        register_page = RegisterPage()
        register_page.render()
    elif st.session_state.page in ["app", "admin"]:
        if not st.session_state.logged_in or not st.session_state.username:
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            set_cookie("username", "", max_age=0)
            save_session_state()
            st.rerun()
        else:
            role = st.session_state.get("role")
            if role == "admin":
                admin_ui = AdminPage()
                admin_ui.render()
            else:
                app_ui = OptimizedChatbotUI(pdf_folder="pdfs")
                app_ui.render()

            if st.sidebar.button("🚪 Déconnexion", key="logout_button"):
                st.session_state.page = "login"
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                set_cookie("username", "", max_age=0)
                save_session_state()
                if os.path.exists("session_state.pkl"):
                    os.remove("session_state.pkl")
                st.rerun()

if __name__ == "__main__":
    main()
