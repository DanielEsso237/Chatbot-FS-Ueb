import os
import streamlit as st
import base64
from backend.admin_logic import AdminLogic

class AdminPage:
    def __init__(self):
        self.logic = AdminLogic()

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
            <p>Gérez les documents PDF pour alimenter le chatbot</p>
        </div>
        """, unsafe_allow_html=True)

    def render_upload(self):
        st.markdown("<h3>➕ Ajouter ou remplacer un PDF</h3>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Choisissez vos fichiers PDF", accept_multiple_files=True, type=["pdf"])
        if uploaded_files:
            progress = st.progress(0)
            for i, uploaded_file in enumerate(uploaded_files, 1):
                self.logic.save_pdf(uploaded_file)
                st.success(f"✅ {uploaded_file.name} ajouté avec succès !")
                progress.progress(i / len(uploaded_files))
            st.balloons()

    def render_existing_files(self):
        st.markdown("<h3>📂 Fichiers existants</h3>", unsafe_allow_html=True)
        files = self.logic.list_pdfs()
        if files:
            for file in files:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                with col1:
                    st.markdown(f"**{file['name']}**")
                with col2:
                    st.caption(f"Taille : {file['size']}")
                with col3:
                    st.caption(f"Modifié : {file['modified']}")
                with col4:
                    if st.button("🗑 Supprimer", key=f"del_{file['name']}"):
                        if self.logic.delete_pdf(file["name"]):
                            st.success(f"{file['name']} supprimé ✅")
                            st.experimental_rerun()

        else:
            st.info("Aucun fichier PDF présent pour le moment.")

    def render_reindex(self):
        st.markdown("<h3>🔄 Réindexation</h3>", unsafe_allow_html=True)
        if st.button("⚡ Réindexer la base de connaissances"):
            with st.spinner("Réindexation en cours..."):
                msg = self.logic.reindex()
            st.success(msg)

    def render(self):
        st.set_page_config(
            page_title="Chatbot FS - Admin",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        self._load_css()
        self.render_header()
        st.markdown("---")
        self.render_upload()
        st.markdown("---")
        self.render_existing_files()
        st.markdown("---")
        self.render_reindex()
