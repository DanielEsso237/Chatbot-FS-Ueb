import os
import streamlit as st
import base64

PDF_FOLDER = "pdfs" 

class AdminPage:
    def __init__(self):
        os.makedirs(PDF_FOLDER, exist_ok=True)

    def _load_css(self):
        css_file = "assets/styles/admin.css"
        if os.path.exists(css_file):
            with open(css_file, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def _get_base64_image(self, image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""

    def render_header(self):
        logo_path = "assets/images/logo.png"
        logo_b64 = self._get_base64_image(logo_path)
        st.markdown(f"""
        <div class="admin-header">
            {'<img src="data:image/png;base64,' + logo_b64 + '" class="admin-logo"/>' if logo_b64 else '🎓'}
            <h1>Chatbot Faculté des Sciences</h1>
            <h2>📚 Espace Administrateur</h2>
            <p>Ajoutez de nouveaux documents PDF pour le chatbot</p>
        </div>
        """, unsafe_allow_html=True)

    def render_upload(self):
        st.markdown("<h3>➕ Ajouter des PDFs</h3>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Choisissez vos fichiers PDF",
            accept_multiple_files=True,
            type=["pdf"]
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                save_path = os.path.join(PDF_FOLDER, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"✅ {uploaded_file.name} ajouté avec succès !")

    def render_existing_files(self):
        st.markdown("<h3>📂 Fichiers existants</h3>", unsafe_allow_html=True)
        files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
        if files:
            for f in files:
                st.markdown(f"- {f}")
        else:
            st.info("Aucun fichier PDF présent pour le moment.")

    def render(self):
        
        st.set_page_config(
            page_title="Chatbot FS - Admin",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        self._load_css()
        self.render_header()
        st.markdown("---")
        self.render_upload()
        st.markdown("---")
        self.render_existing_files()
