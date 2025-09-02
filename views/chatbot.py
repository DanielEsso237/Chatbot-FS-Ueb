import os
import streamlit as st
import asyncio
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
        
        # Précharger le modèle au démarrage pour des réponses plus rapides
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
            
            # Indicateur de performance
            st.markdown("### 🚀 Optimisations Actives")
            optimizations = [
                "✅ Cache intelligent des réponses",
                "✅ Modèle préchargé",
                "✅ Index FAISS persistant",
                "✅ Contexte optimisé (1500 chars)",
                "✅ Chunking parallèle",
                "✅ Paramètres CPU optimisés"
            ]
            for opt in optimizations:
                st.markdown(f"<small>{opt}</small>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ℹ️ Informations")
            st.info("Version optimisée pour votre configuration i5 4ème gen + 8GB RAM")
            
            st.markdown("---")
            st.markdown("### 🔧 Fonctionnalités")
            st.markdown("""
            - 🔍 Recherche vectorielle rapide
            - 🤖 Gemma 2B optimisé CPU
            - 📚 Cache intelligent
            - ⚡ Réponses accélérées
            - 🎯 Contexte limité mais précis
            """)
            
            # Bouton pour vider le cache
            if st.button("🗑️ Vider le cache"):
                self.chatbot_logic.cache_responses.clear()
                if hasattr(st.session_state, 'messages'):
                    st.session_state.messages = []
                st.success("Cache vidé !")
                st.experimental_rerun()

    def render_performance_metrics(self):
        """Afficher des métriques de performance"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📝 Réponses en cache", 
                value=len(self.chatbot_logic.cache_responses),
                help="Nombre de réponses mises en cache pour des requêtes futures plus rapides"
            )
        
        with col2:
            docs_loaded = len(getattr(st.session_state, 'texts', []))
            st.metric(
                label="📚 Documents chargés", 
                value=docs_loaded,
                help="Nombre de chunks de documents disponibles pour la recherche"
            )
        
        with col3:
            index_status = "✅ Actif" if self.chatbot_logic.retriever else "❌ Inactif"
            st.metric(
                label="🔍 Index FAISS", 
                value=index_status,
                help="Statut de l'index de recherche vectorielle"
            )

    def render_quick_questions(self):
        """Afficher des questions rapides prédéfinies"""
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
                    # Simuler une requête utilisateur
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.experimental_rerun()

    def render_typing_indicator(self):
        """Indicateur de frappe plus fluide"""
        return st.empty()

    def render(self):
        st.set_page_config(
            page_title="Chatbot FS-UEb ⚡",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        load_custom_css()
        self.render_header()
        self.render_sidebar()
        
        # Préparation des données avec indicateur de progression
        with st.spinner("📚 Chargement des documents..."):
            self.chatbot_logic.prepare_data(st.session_state)
        
        with st.spinner("🔍 Initialisation de l'index..."):
            self.chatbot_logic.load_index(st.session_state)
        
        # Métriques de performance
        self.render_performance_metrics()
        st.markdown("---")
        
        # Interface de chat optimisée
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Initialiser les messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Message de bienvenue
            welcome_msg = """
            👋 Bonjour ! Je suis votre assistant intelligent optimisé pour la Faculté des Sciences.
            
            ⚡ **Nouvelles optimisations** :
            - Réponses plus rapides grâce au cache intelligent
            - Modèle préchargé pour réduire la latence
            - Configuration adaptée à votre PC
            
            Posez-moi vos questions sur les documents de la faculté !
            """
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

        # Limiter l'historique pour économiser la mémoire (configuration 8GB RAM)
        st.session_state.messages = st.session_state.messages[-15:]  # Réduire de 20 à 15

        # Afficher l'historique des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Questions rapides si pas de conversation
        if len(st.session_state.messages) <= 1:
            self.render_quick_questions()
            st.markdown("---")

        # Zone de saisie avec placeholder optimisé
        if user_query := st.chat_input("💬 Votre question (tapez puis Entrée)..."):
            # Afficher immédiatement la question de l'utilisateur
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            # Réponse de l'assistant avec indicateurs optimisés
            with st.chat_message("assistant"):
                # Indicateur de traitement plus précis
                thinking_placeholder = st.empty()
                thinking_placeholder.markdown("🧠 **Analyse en cours...**")
                
                response_placeholder = st.empty()
                
                try:
                    # Stream optimisé
                    response_stream = self.chatbot_logic.run_query(user_query)
                    
                    # Collecter et afficher la réponse
                    full_response = ""
                    chunk_buffer = ""
                    
                    for chunk in response_stream:
                        if chunk:
                            chunk_buffer += chunk
                            full_response += chunk
                            
                            # Affichage par "mots" pour un meilleur effet
                            if len(chunk_buffer.split()) >= 3 or chunk.endswith(('.', '!', '?')):
                                thinking_placeholder.empty()
                                response_placeholder.markdown(full_response + "▌")
                                chunk_buffer = ""
                    
                    # Affichage final
                    thinking_placeholder.empty()
                    response_placeholder.markdown(full_response)
                    
                    # Sauvegarder la réponse
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    thinking_placeholder.empty()
                    error_msg = "❌ Une erreur est survenue. Veuillez réessayer."
                    response_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Footer optimisé
        st.markdown("""
        <div style='text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;'>
            <p>⚡ <strong>Chatbot FS-UEb Optimisé</strong> - Université d'Ebolowa, Faculté des Sciences</p>
            <p>🚀 Version haute performance pour i5 4ème gen | Esso Daniel - OPENMIND ACADEMY</p>
        </div>
        """, unsafe_allow_html=True)