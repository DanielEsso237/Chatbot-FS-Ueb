import streamlit as st
from views.login import LoginPage
from views.register import RegisterPage
from views.chatbot import ChatbotUI
from views.admin import AdminPage
from dotenv import load_dotenv
from utils.cookies import get_cookie_value_from_js, set_cookie

load_dotenv()

def main():
    if "page" not in st.session_state:
        username = get_cookie_value_from_js("username")
        if username:
            st.session_state.page = "app"
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.page == "register":
        register_page = RegisterPage()
        register_page.render()
    elif st.session_state.page in ["app", "admin"]:
        role = st.session_state.get("role")
        if role == "admin":
            admin_ui = AdminPage()
            admin_ui.render()
        else:
            app_ui = ChatbotUI(pdf_folder="pdfs")
            app_ui.render()

        if st.sidebar.button("🚪 Déconnexion"):
            set_cookie("username", "")
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main()
