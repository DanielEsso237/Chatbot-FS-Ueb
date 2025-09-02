import os
import pickle
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

class OptimizedChatbotLogic:
    def __init__(self, pdf_folder, index_file="faiss_index"):
        self.pdf_folder = pdf_folder
        self.index_file = index_file
        
        # Configuration Ollama optimisée pour votre configuration
        self.model_path = r"C:\Users\T.SHIGARAKI\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L12-v2\snapshots\c004d8e3e901237d8fa7e9fff12774962e391ce5"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_path,
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Configuration Ollama optimisée
        self.llm = OllamaLLM(
            model="gemma:2b", 
            base_url="http://127.0.0.1:11434",
            temperature=0.1,
            num_ctx=1024,
            num_thread=4,
            num_gpu=0,
            repeat_penalty=1.1,
            top_k=10,
            top_p=0.9
        )

        self.retriever = None
        self.cache_responses = {}
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Prompt optimisé
        self.system_prompt = """
Tu es un assistant spécialisé. Réponds uniquement avec le contexte fourni.

Règles :
- Réponse dans le contexte -> reformule clairement
- Pas de réponse -> réponds "question hors contexte"
- Français uniquement
- Maximum 3 phrases concises

Contexte: {context}
Question: {question}
Réponse:
"""

    def prepare_data(self, st_session_state):
        """Préparation des données optimisée avec cache intelligent"""
        texts_file = os.path.join(self.pdf_folder, "texts.pkl")
        files_list_file = os.path.join(self.pdf_folder, "files_list.pkl")
        
        if not os.path.exists(self.pdf_folder):
            st_session_state.texts = []
            return

        current_files = [f for f in os.listdir(self.pdf_folder) if f.endswith(".pdf")]
        
        if not current_files:
            st_session_state.texts = []
            return

        # Cache intelligent
        if os.path.exists(texts_file) and os.path.exists(files_list_file):
            try:
                with open(files_list_file, "rb") as f:
                    old_files = pickle.load(f)
                
                files_modified = {}
                for file in current_files:
                    files_modified[file] = os.path.getmtime(os.path.join(self.pdf_folder, file))
                
                cache_file = os.path.join(self.pdf_folder, "files_modified.pkl")
                if os.path.exists(cache_file):
                    with open(cache_file, "rb") as f:
                        old_modified = pickle.load(f)
                    
                    if (set(current_files) == set(old_files) and 
                        files_modified == old_modified):
                        with open(texts_file, "rb") as f:
                            st_session_state.texts = pickle.load(f)
                        return
            except:
                pass

        # Chargement des documents
        documents = []
        for file in current_files:
            try:
                loader = PyPDFLoader(os.path.join(self.pdf_folder, file))
                docs = loader.load()
                
                for doc in docs:
                    doc.page_content = " ".join(doc.page_content.split())
                    
                documents.extend(docs)
            except Exception as e:
                print(f"Erreur lors du chargement de {file}: {e}")

        if not documents:
            st_session_state.texts = []
            return

        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=750,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        st_session_state.texts = text_splitter.split_documents(documents)

        # Sauvegarde du cache
        try:
            with open(texts_file, "wb") as f:
                pickle.dump(st_session_state.texts, f)
            with open(files_list_file, "wb") as f:
                pickle.dump(current_files, f)
            
            files_modified = {}
            for file in current_files:
                files_modified[file] = os.path.getmtime(os.path.join(self.pdf_folder, file))
            
            with open(os.path.join(self.pdf_folder, "files_modified.pkl"), "wb") as f:
                pickle.dump(files_modified, f)
        except Exception as e:
            print(f"Erreur de cache: {e}")

    def load_index(self, st_session_state):
        """Chargement d'index optimisé"""
        if "retriever" in st_session_state and st_session_state.retriever:
            self.retriever = st_session_state.retriever
            return

        if not hasattr(st_session_state, "texts") or not st_session_state.texts:
            self.retriever = None
            st_session_state.retriever = None
            return

        try:
            if os.path.exists(f"{self.index_file}.faiss"):
                db = FAISS.load_local(
                    self.index_file, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.retriever = db.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                )
                st_session_state.retriever = self.retriever
                return
        except:
            pass

        try:
            db = FAISS.from_documents(st_session_state.texts, self.embeddings)
            db.save_local(self.index_file)
            self.retriever = db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            st_session_state.retriever = self.retriever
        except Exception as e:
            print(f"Erreur création index: {e}")
            self.retriever = None
            st_session_state.retriever = None

    def create_rag_chain(self):
        """Création de chaîne RAG"""
        if not self.retriever:
            return None
            
        prompt = ChatPromptTemplate.from_template(self.system_prompt)
        
        chain = (
            {
                "context": self.retriever | self._format_docs, 
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain
    
    def _format_docs(self, docs):
        """Formater les documents"""
        max_context_length = 1500
        
        formatted = []
        total_length = 0
        
        for doc in docs:
            content = doc.page_content.strip()
            if total_length + len(content) <= max_context_length:
                formatted.append(content)
                total_length += len(content)
            else:
                remaining = max_context_length - total_length
                if remaining > 100:
                    formatted.append(content[:remaining] + "...")
                break
        
        return "\n\n".join(formatted)

    def run_query_with_status(self, user_query):
        """Version avec statuts pour UI fluide"""
        # Étape 1: Vérifier le cache
        yield "status", "🔍 Recherche dans le cache..."
        time.sleep(0.1)  # Petit délai pour l'affichage
        
        if user_query in self.cache_responses:
            yield "status", "✅ Réponse trouvée en cache !"
            time.sleep(0.2)
            yield "status", "💬 Affichage de la réponse..."
            
            cached = self.cache_responses[user_query]
            if isinstance(cached, list):
                for chunk in cached:
                    yield "content", chunk
                    time.sleep(0.05)  # Délai entre les chunks pour simulation streaming
            else:
                # Si c'est une string, on la divise en mots
                words = cached.split()
                for i, word in enumerate(words):
                    yield "content", word + " "
                    if i % 3 == 0:  # Pause tous les 3 mots
                        time.sleep(0.05)
            return

        # Étape 2: Créer la chaîne RAG
        yield "status", "🔧 Initialisation du système de recherche..."
        time.sleep(0.1)
        
        rag_chain = self.create_rag_chain()
        if not rag_chain:
            yield "content", "❌ Aucun document disponible pour répondre à la requête."
            return

        try:
            # Étape 3: Recherche dans les documents
            yield "status", "📚 Recherche dans les documents..."
            time.sleep(0.2)
            
            # Étape 4: Génération de la réponse
            yield "status", "🤖 Génération de la réponse par Gemma..."
            time.sleep(0.1)
            
            yield "status", "💬 Affichage en temps réel..."
            
            # Stream de la réponse
            response_stream = rag_chain.stream(user_query)
            response_chunks = []
            
            for chunk in response_stream:
                if chunk and chunk.strip():
                    response_chunks.append(chunk)
                    yield "content", chunk
            
            # Mettre en cache
            if response_chunks:
                self.cache_responses[user_query] = response_chunks
                
                # Limiter la taille du cache
                if len(self.cache_responses) > 50:
                    oldest_keys = list(self.cache_responses.keys())[:10]
                    for key in oldest_keys:
                        del self.cache_responses[key]
                        
        except Exception as e:
            yield "status", "❌ Erreur lors du traitement..."
            time.sleep(0.1)
            error_msg = f"Une erreur est survenue: {str(e)}"
            yield "content", error_msg

    def run_query(self, user_query):
        """Version simple pour compatibilité"""
        for msg_type, content in self.run_query_with_status(user_query):
            if msg_type == "content":
                yield content

    def preload_model(self):
        """Précharger le modèle"""
        try:
            dummy_query = "test"
            list(self.llm.stream(dummy_query))
        except:
            pass