import streamlit as st
from views.login import LoginPage
from views.register import RegisterPage
from views.chatbot import VectorialSearchGemma
from dotenv import load_dotenv 

load_dotenv() 

def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.page == "register":
        register_page = RegisterPage()
        register_page.render()
    elif st.session_state.page == "app":
        app = VectorialSearchGemma(pdf_folder="pdfs")
        app.prepare_data()
        app.load_index()
        app.render()
        if st.sidebar.button("🚪 Déconnexion"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main()
