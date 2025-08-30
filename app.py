import streamlit as st
from views.login import LoginPage
from views.register import RegisterPage
from views.chatbot import ChatbotUI
from views.admin import AdminPage
from dotenv import load_dotenv
from utils.cookies import set_cookie, get_cookie
from backend.auth import AuthManager
import os
import pickle

load_dotenv()

def save_session_state():
    """Sauvegarder l'état de la session dans un fichier temporaire."""
    try:
        with open("session_state.pkl", "wb") as f:
            pickle.dump({
                "page": st.session_state.get("page", "login"),
                "logged_in": st.session_state.get("logged_in", False),
                "username": st.session_state.get("username", None),
                "role": st.session_state.get("role", None)
            }, f)
        print("État de la session sauvegardé")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'état de la session : {e}")

def load_session_state(auth_manager):
    """Charger l'état de la session depuis un fichier temporaire."""
    try:
        if os.path.exists("session_state.pkl"):
            with open("session_state.pkl", "rb") as f:
                state = pickle.load(f)
                
                if state.get("logged_in") and state.get("username"):
                    success, _, user, role = auth_manager.login_user(state["username"], "")
                    if success:
                        st.session_state.page = state.get("page", "login")
                        st.session_state.logged_in = state.get("logged_in", False)
                        st.session_state.username = state.get("username", None)
                        st.session_state.role = state.get("role", None)
                        print("État de la session chargé avec succès")
                    else:
                        print("Utilisateur non valide dans session_state.pkl, réinitialisation")
                        st.session_state.page = "login"
                        st.session_state.logged_in = False
                        st.session_state.username = None
                        st.session_state.role = None
                        set_cookie("username", "", max_age=0)
                        if os.path.exists("session_state.pkl"):
                            os.remove("session_state.pkl")
                else:
                    print("Aucun utilisateur valide dans session_state.pkl")
                    st.session_state.page = "login"
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.role = None
        else:
            print("Aucun fichier session_state.pkl trouvé")
    except Exception as e:
        print(f"Erreur lors du chargement de l'état de la session : {e}")

def main():
 
    auth_manager = AuthManager()

    
    if "page" not in st.session_state:
        print("Initialisation de st.session_state")
        load_session_state(auth_manager)
        if "page" not in st.session_state:
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None

    print(f"Page actuelle : {st.session_state.page}, logged_in : {st.session_state.logged_in}, username : {st.session_state.username}")

  
    save_session_state()

  
    if st.session_state.page == "login":
        print("Affichage de la page de connexion")
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.page == "register":
        print("Affichage de la page d'inscription")
        register_page = RegisterPage()
        register_page.render()
    elif st.session_state.page in ["app", "admin"]:
        if not st.session_state.logged_in or not st.session_state.username:
            print("Utilisateur non connecté, redirection vers login")
            st.session_state.page = "login"
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            set_cookie("username", "", max_age=0)
            save_session_state()
            st.rerun()
        else:
            print(f"Affichage de la page {st.session_state.page} pour l'utilisateur {st.session_state.username}")
            role = st.session_state.get("role")
            if role == "admin":
                admin_ui = AdminPage()
                admin_ui.render()
            else:
                app_ui = ChatbotUI(pdf_folder="pdfs")
                app_ui.render()

          
            if st.sidebar.button("🚪 Déconnexion", key="logout_button"):
                print("Déconnexion demandée")
                st.session_state.page = "login"
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                set_cookie("username", "", max_age=0)
                save_session_state()
                if os.path.exists("session_state.pkl"):
                    os.remove("session_state.pkl")
                    print("Fichier de session supprimé")
                st.rerun()

if __name__ == "__main__":
    main()