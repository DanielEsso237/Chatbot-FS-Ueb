import streamlit as st
from views.login import LoginPage
from views.register import RegisterPage
from views.chatbot import ChatbotUI
from dotenv import load_dotenv 
from utils.cookies import get_cookie_value_from_js, set_cookie
load_dotenv() 

def main():
    # Vérifie si la page doit être initialisée
    if "page" not in st.session_state:
        # Tente de récupérer le nom d'utilisateur à partir d'un cookie
        username = get_cookie_value_from_js("username")
        
        if username:
            # Si un cookie est trouvé, met à jour la session pour que l'utilisateur soit connecté
            st.session_state.page = "app"
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            # Sinon, affiche la page de connexion par défaut
            st.session_state.page = "login"

    # Gère la navigation de l'application
    if st.session_state.page == "login":
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.page == "register":
      register_page = RegisterPage()
      register_page.render()

    elif st.session_state.page == "app":
        
        app_ui = ChatbotUI(pdf_folder="pdfs")
        app_ui.render()
        
        if st.sidebar.button("🚪 Déconnexion"):
            # Efface les cookies et l'état de la session
            set_cookie("username", "") # Vide le cookie
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main()

