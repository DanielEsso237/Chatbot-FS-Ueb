C:\Users\T.SHIGARAKI\Desktop\Chatbot-FS\views\login.py
import streamlit as st
import os
from PIL import Image

USERS = {
    "admin": "admin123",
    "user": "user123"
}

def load_css():
    """Charge le fichier CSS personnalisé"""
    css_file = "assets/styles/login.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def login_page():
    st.set_page_config(
        page_title="Chatbot FS - Connexion",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Charger les styles CSS
    load_css()

    # Container principal avec classes CSS personnalisées
    st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="logo-container">
    """, unsafe_allow_html=True)

    # Display the logo using st.image()
    logo_path = "assets/images/logo.png"
    if os.path.exists(logo_path):
        logo_image = Image.open(logo_path)
        st.image(logo_image, width=120, use_column_width=False, output_format="PNG") # Streamlit will handle the path correctly

    st.markdown("""
                </div>
                <h1 class="login-title">Chatbot Faculté des Sciences</h1>
                <p class="login-subtitle">Université d'Ebolowa</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ... (rest of your login_page function)