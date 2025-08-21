import streamlit as st
import os
from PIL import Image
import base64


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

def get_base64_image(image_path):
    """Convertit une image en base64 pour l'utiliser dans st.markdown"""
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{b64}"


def login_page():
    st.set_page_config(
        page_title="Chatbot FS - Connexion",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    
    load_css()

    
    logo_path = "assets/images/logo.png"
    if os.path.exists(logo_path):
        logo_b64 = get_base64_image(logo_path)
        logo_html = f'<img src="{logo_b64}" alt="Logo FS" class="logo">'
    else:
        logo_html = '<div class="logo-placeholder"></div>'

    
    st.markdown(f"""
        <div class="login-container">
            <div class="login-header">
                <div class="logo-container">
                    {logo_html}
                </div>
                <h1 class="login-title">Chatbot Faculté des Sciences</h1>
                <p class="login-subtitle">Université d'Ebolowa</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    
    st.markdown("""
<div class="form-container">
    <div class="connexion-text">CONNEXION</div>
""", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        username = st.text_input(
            "Nom d'utilisateur",
            placeholder="Entrez votre nom d'utilisateur",
            key="username_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="Entrez votre mot de passe",
            key="password_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        submit = st.form_submit_button(" Se connecter", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    
    if submit:
        if username.strip() == "":
            st.markdown('<div class="error-message">⚠️ Veuillez saisir un nom d\'utilisateur</div>', unsafe_allow_html=True)
        elif password.strip() == "":
            st.markdown('<div class="error-message">⚠️ Veuillez saisir un mot de passe</div>', unsafe_allow_html=True)
        elif username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state.page = "app"
            st.markdown('<div class="success-message">✅ Connexion réussie ! Redirection...</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.markdown('<div class="error-message">❌ Identifiants invalides</div>', unsafe_allow_html=True)

    
    st.markdown("""
        <div class="login-footer">
            <p>© 2025 Université d'Ebolowa - Faculté des Sciences</p>
            <p class="help-text">Besoin d'aide ? Contactez l'administration</p>
        </div>
    """, unsafe_allow_html=True)
