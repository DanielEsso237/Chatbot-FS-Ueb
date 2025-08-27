import os
import streamlit as st
from dotenv import load_dotenv
from backend.chatbot_logic import ChatbotLogic

load_dotenv()

def load_custom_css():
    css_file = "assets/styles/chatbot.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class ChatbotUI:
    def __init__(self, pdf_folder):
        self.chatbot_logic = ChatbotLogic(pdf_folder)

    def get_base64_image(self, image_path):
        try:
            import base64
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return ""

    def render_header(self):
        logo_path = "assets/images/logo.png"
        header_html = f"""
        <div class="custom-header fade-in">
            <h1>
                {'<img src="data:image/png;base64,' + self.get_base64_image(logo_path) + '" class="logo-header"/>' if os.path.exists(logo_path) else '🎓'}
                Chatbot FS-UEb
            </h1>
            <p>Assistant Intelligent pour la Faculté des Sciences - Université d'Ebolowa</p>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

    def render_sidebar(self):
        with st.sidebar:
            logo_path = "assets/images/logo.png"
            if os.path.exists(logo_path):
                st.markdown(f'<img src="data:image/png;base64,{self.get_base64_image(logo_path)}" class="sidebar-logo"/>', unsafe_allow_html=True)
            else:
                st.markdown("🎓", unsafe_allow_html=True)
            st.markdown('<div class="sidebar-title">Chatbot FS-UEb</div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-subtitle">Université d\'Ebolowa<br/>Faculté des Sciences</div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### ℹ️ Informations")
            st.info("Ce chatbot utilise l'IA pour répondre à vos questions basées sur les documents PDF de la faculté.")
            st.markdown("---")
            st.markdown("### 🔧 Fonctionnalités")
            st.markdown("""
            - 🔍 Recherche vectorielle (LangChain + FAISS)
            - 🤖 IA Gemma 2B (Ollama)
            - 📚 Base documentaire
            - 🎯 Réponses contextuelles
            """)

    def render(self):
        load_custom_css()
        self.render_header()
        self.render_sidebar()
        
        self.chatbot_logic.prepare_data(st.session_state)
        self.chatbot_logic.load_index(st.session_state)

        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Limiter à 20 derniers messages
        st.session_state.messages = st.session_state.messages[-20:]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_query := st.chat_input("💬 Posez votre question..."):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            with st.chat_message("assistant"):
                with st.spinner("🤔 Recherche dans les documents..."):
                    response_stream = self.chatbot_logic.run_query(user_query)
                    full_response = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;'>
            <p>🎓 <strong>Chatbot FS-UEb</strong> - Université d'Ebolowa, Faculté des Sciences</p>
            <p>Esso Daniel - OPENMIND ACADEMY</p>
        </div>
        """, unsafe_allow_html=True)
