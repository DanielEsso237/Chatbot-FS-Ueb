import os
import streamlit as st
import time
from dotenv import load_dotenv
from backend.chatbot_logic import OptimizedChatbotLogic

load_dotenv()

def load_custom_css():
    css_file = "assets/styles/chatbot.css"
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

class OptimizedChatbotUI:
    def __init__(self, pdf_folder):
        self.chatbot_logic = OptimizedChatbotLogic(pdf_folder)
        if "model_preloaded" not in st.session_state:
            with st.spinner("🔧 Initialisation du modèle..."):
                self.chatbot_logic.preload_model()
            st.session_state.model_preloaded = True

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
                Chatbot FS-UEb ⚡
            </h1>
            <p>Assistant Intelligent Optimisé - Faculté des Sciences, Université d'Ebolowa</p>
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
            
            st.markdown('<div class="sidebar-title">Chatbot FS-UEb ⚡</div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-subtitle">Université d\'Ebolowa<br/>Faculté des Sciences</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 🚀 Optimisations Actives")
            optimizations = [
                "✅ Cache intelligent des réponses",
                "✅ Modèle préchargé",
                "✅ Streaming fluide",
                "✅ Interface réactive",
            ]
            for opt in optimizations:
                st.markdown(f"<small>{opt}</small>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ℹ️ Informations")
            st.info("Ce chatbot est optimisé pour répondre rapidement aux questions basées sur les documents de la Faculté des Sciences. Posez vos questions en toute simplicité !")
            
            st.markdown("---")
            st.markdown("### 🔧 Fonctionnalités")
            st.markdown("""
            - 🔍 Recherche vectorielle rapide
            - 🤖 Réponse basée sur les documents contenant les informations sur la faculté
            - 📚 Cache intelligent
            - ⚡ Réponses en temps réel
            - 🎯 Interface moderne
            """)
            
            if st.button("🗑️ Vider le cache"):
                self.chatbot_logic.cache_responses.clear()
                if hasattr(st.session_state, 'messages'):
                    st.session_state.messages = []
                st.success("Cache vidé !")
                st.rerun()

    def render_performance_metrics(self):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📝 Réponses en cache", 
                value=len(self.chatbot_logic.cache_responses),
                help="Nombre de réponses mises en cache"
            )
        
        with col2:
            docs_loaded = len(getattr(st.session_state, 'texts', []))
            st.metric(
                label="📚 Documents chargés", 
                value=docs_loaded,
                help="Nombre de chunks de documents disponibles"
            )
        
        with col3:
            index_status = "✅ Actif" if self.chatbot_logic.retriever else "❌ Inactif"
            st.metric(
                label="🔍 Index FAISS", 
                value=index_status,
                help="Statut de l'index de recherche vectorielle"
            )

    def render_quick_questions(self):
        st.markdown("### 💬 Questions rapides")
        
        quick_questions = [
            "Quels sont les programmes d'études disponibles ?",
            "Comment s'inscrire à la faculté ?",
            "Quels sont les frais de scolarité ?",
            "Où trouve-t-on les emplois du temps ?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(f"❓ {question}", key=f"quick_{i}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.session_state.pending_query = question
                    st.rerun()

    def render_typing_animation(self, text, placeholder):
        displayed_text = ""
        for char in text:
            displayed_text += char
            placeholder.markdown(f"**{displayed_text}**")
            time.sleep(0.02)

    def process_query_streaming(self, user_query, status_placeholder, response_placeholder):
        full_response = ""
        current_status = ""
        
        try:
            for msg_type, content in self.chatbot_logic.run_query_with_status(user_query):
                if msg_type == "status":
                    current_status = content
                    status_placeholder.markdown(f"**{current_status}**")
                    
                elif msg_type == "content":
                    if current_status:
                        status_placeholder.empty()
                        current_status = ""
                    
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            status_placeholder.empty()
            response_placeholder.markdown(full_response)
            
            return full_response
            
        except Exception as e:
            status_placeholder.empty()
            error_msg = "❌ Une erreur est survenue. Veuillez réessayer."
            response_placeholder.markdown(error_msg)
            return error_msg

    def render(self):
        st.set_page_config(
            page_title="Chatbot FS-UEb ⚡",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        load_custom_css()
        self.render_header()
        self.render_sidebar()
        
        with st.spinner("📚 Chargement des documents..."):
            self.chatbot_logic.prepare_data(st.session_state)
        
        with st.spinner("🔍 Initialisation de l'index..."):
            self.chatbot_logic.load_index(st.session_state)
        
        self.render_performance_metrics()
        st.markdown("---")
        
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            welcome_msg = """
            👋 Bonjour ! Je suis votre assistant intelligent optimisé pour la Faculté des Sciences.
            
            ⚡ **Nouvelles fonctionnalités** :
            - Interface fluide et réactive
            - Streaming en temps réel
            - Statuts de traitement visibles
            - Réponses plus naturelles
            
            Posez-moi vos questions sur les documents de la faculté !
            """
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

        st.session_state.messages = st.session_state.messages[-15:]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if len(st.session_state.messages) <= 1:
            self.render_quick_questions()
            st.markdown("---")

        if hasattr(st.session_state, 'pending_query'):
            user_query = st.session_state.pending_query
            delattr(st.session_state, 'pending_query')
            
            with st.chat_message("user"):
                st.markdown(user_query)
            
            with st.chat_message("assistant"):
                status_placeholder = st.empty()
                response_placeholder = st.empty()
                
                response = self.process_query_streaming(user_query, status_placeholder, response_placeholder)
                st.session_state.messages.append({"role": "assistant", "content": response})

        if user_query := st.chat_input("💬 Votre question (tapez puis Entrée)..."):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            with st.chat_message("assistant"):
                status_placeholder = st.empty()
                response_placeholder = st.empty()
                
                response = self.process_query_streaming(user_query, status_placeholder, response_placeholder)
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("""
        <div style='text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;'>
            <p>⚡ <strong>Chatbot FS-UEb Optimisé</strong> - Université d'Ebolowa, Faculté des Sciences</p>
            <p>🚀 Esso Daniel - OPENMIND ACADEMY</p>
        </div>
        """, unsafe_allow_html=True)