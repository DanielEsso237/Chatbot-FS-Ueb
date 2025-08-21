import streamlit as st

USERS = {
    "admin": "admin123",
    "user": "user123"
}

def login_page():
    st.set_page_config(initial_sidebar_state="collapsed")

    st.markdown("<h2 style='text-align:center;'>🔐 Connexion</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Nom d’utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")

    if submit:
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state.page = "app"
            st.success("Connexion réussie ✅")
            st.rerun()
        else:
            st.error("Identifiants invalides ❌")
