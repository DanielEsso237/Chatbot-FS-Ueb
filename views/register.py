import streamlit as st
import os
import base64
from backend.auth import AuthManager

class RegisterPage:
    def __init__(self):
        self.auth_manager = AuthManager()

    def _load_css(self):
        css_file = "assets/styles/login.css"
        if os.path.exists(css_file):
            with open(css_file, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def _get_base64_image(self, image_path):
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{b64}"

    def render(self):
        st.set_page_config(
            page_title="Chatbot FS - Inscription",
            page_icon="🎓",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        self. _load_css()
        
        logo_path = "assets/images/logo.png"
        if os.path.exists(logo_path):
            logo_b64 = self._get_base64_image(logo_path)
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
                <div class="connexion-text">INSCRIPTION</div>
        """, unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            username = st.text_input(
                "Nom d'utilisateur",
                placeholder="Entrez votre nom d'utilisateur",
                key="username_input"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            email = st.text_input(
                "Adresse e-mail",
                placeholder="Entrez votre adresse e-mail",
                key="email_input"
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
            
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            confirm_password = st.text_input(
                "Confirmer le mot de passe",
                type="password",
                placeholder="Confirmez votre mot de passe",
                key="confirm_password_input"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            submit = st.form_submit_button(" S'inscrire", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submit:
            if not username or not email or not password or not confirm_password:
                st.markdown('<div class="error-message">⚠️ Veuillez remplir tous les champs.</div>', unsafe_allow_html=True)
            elif password != confirm_password:
                st.markdown('<div class="error-message">❌ Les mots de passe ne correspondent pas.</div>', unsafe_allow_html=True)
            else:
                success, message = self.auth_manager.register_user(username, email, password)
                if success:
                    st.session_state.page = "login"
                    st.session_state["registration_success"] = True
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)

        st.markdown('<div class="register-link" style="text-align:center; margin-top:10px;">', unsafe_allow_html=True)
        if st.button("Se connecter"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="login-footer">
                <p>© 2025 Université d'Ebolowa - Faculté des Sciences</p>
                <p class="help-text">Besoin d'aide ? Contactez l'administration</p>
            </div>
        """, unsafe_allow_html=True)
