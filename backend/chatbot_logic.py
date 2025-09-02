import os
import pickle
import asyncio
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
            encode_kwargs={'normalize_embeddings': True}  # Normalisation pour une recherche plus rapide
        )
        
        # Configuration Ollama optimisée
        self.llm = OllamaLLM(
            model="gemma:2b", 
            base_url="http://127.0.0.1:11434",
            # Paramètres d'optimisation pour votre config
            temperature=0.1,  # Réduire pour des réponses plus déterministes et rapides
            num_ctx=1024,     # Contexte réduit pour votre RAM limitée (8GB)
            num_thread=4,     # Utiliser tous les cœurs de votre i5
            num_gpu=0,        # Désactiver GPU (GT720M trop faible)
            repeat_penalty=1.1,
            top_k=10,         # Réduire pour accélérer la génération
            top_p=0.9
        )

        self.retriever = None
        self.cache_responses = {}
        self.executor = ThreadPoolExecutor(max_workers=2)  # Pour les opérations asynchrones

        # Prompt optimisé (plus court et direct)
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

        # Cache intelligent - vérifier si les fichiers ont changé
        if os.path.exists(texts_file) and os.path.exists(files_list_file):
            try:
                with open(files_list_file, "rb") as f:
                    old_files = pickle.load(f)
                
                # Vérifier aussi les dates de modification
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

        # Chargement optimisé des documents
        documents = []
        for file in current_files:
            try:
                loader = PyPDFLoader(os.path.join(self.pdf_folder, file))
                docs = loader.load()
                
                # Prétraitement léger pour optimiser
                for doc in docs:
                    # Nettoyer le texte pour réduire la taille
                    doc.page_content = " ".join(doc.page_content.split())
                    
                documents.extend(docs)
            except Exception as e:
                print(f"Erreur lors du chargement de {file}: {e}")

        if not documents:
            st_session_state.texts = []
            return

        # Chunking optimisé - conserver la longueur mais optimiser le processus
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=750,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Séparateurs optimisés
        )
        st_session_state.texts = text_splitter.split_documents(documents)

        # Sauvegarde du cache
        try:
            with open(texts_file, "wb") as f:
                pickle.dump(st_session_state.texts, f)
            with open(files_list_file, "wb") as f:
                pickle.dump(current_files, f)
            
            # Sauvegarder les dates de modification
            files_modified = {}
            for file in current_files:
                files_modified[file] = os.path.getmtime(os.path.join(self.pdf_folder, file))
            
            with open(os.path.join(self.pdf_folder, "files_modified.pkl"), "wb") as f:
                pickle.dump(files_modified, f)
        except Exception as e:
            print(f"Erreur de cache: {e}")

    def load_index(self, st_session_state):
        """Chargement d'index optimisé avec persistence"""
        if "retriever" in st_session_state and st_session_state.retriever:
            self.retriever = st_session_state.retriever
            return

        if not hasattr(st_session_state, "texts") or not st_session_state.texts:
            self.retriever = None
            st_session_state.retriever = None
            return

        # Essayer de charger l'index existant d'abord
        try:
            if os.path.exists(f"{self.index_file}.faiss"):
                db = FAISS.load_local(
                    self.index_file, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.retriever = db.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}  # Réduire le nombre de chunks récupérés
                )
                st_session_state.retriever = self.retriever
                return
        except:
            pass

        # Créer un nouvel index si nécessaire
        try:
            db = FAISS.from_documents(st_session_state.texts, self.embeddings)
            db.save_local(self.index_file)
            self.retriever = db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Limiter à 3 chunks max
            )
            st_session_state.retriever = self.retriever
        except Exception as e:
            print(f"Erreur création index: {e}")
            self.retriever = None
            st_session_state.retriever = None

    def create_rag_chain(self):
        """Création de chaîne RAG optimisée"""
        if not self.retriever:
            return None
            
        prompt = ChatPromptTemplate.from_template(self.system_prompt)
        
        # Chaîne optimisée avec limitation du contexte
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
        """Formater les documents pour limiter la longueur du contexte"""
        # Limiter le nombre de caractères totaux du contexte
        max_context_length = 1500  # Adapté à votre config RAM
        
        formatted = []
        total_length = 0
        
        for doc in docs:
            content = doc.page_content.strip()
            if total_length + len(content) <= max_context_length:
                formatted.append(content)
                total_length += len(content)
            else:
                # Tronquer le dernier document si nécessaire
                remaining = max_context_length - total_length
                if remaining > 100:  # Minimum viable
                    formatted.append(content[:remaining] + "...")
                break
        
        return "\n\n".join(formatted)

    async def run_query_async(self, user_query):
        """Requête asynchrone pour améliorer la réactivité"""
        if user_query in self.cache_responses:
            # Retourner le cache sous forme de générateur
            cached = self.cache_responses[user_query]
            if isinstance(cached, str):
                for chunk in cached.split():
                    yield chunk + " "
            else:
                for chunk in cached:
                    yield chunk
            return

        rag_chain = self.create_rag_chain()
        if not rag_chain:
            yield "Aucun document disponible pour répondre à la requête."
            return

        try:
            # Exécuter la requête dans un thread séparé
            loop = asyncio.get_event_loop()
            response_stream = await loop.run_in_executor(
                self.executor, 
                lambda: list(rag_chain.stream(user_query))
            )
            
            # Mettre en cache et streamer
            full_response = "".join(response_stream)
            self.cache_responses[user_query] = response_stream
            
            for chunk in response_stream:
                yield chunk
                
        except Exception as e:
            error_msg = f"Erreur : {e}"
            yield error_msg

    def run_query(self, user_query):
        """Version synchrone optimisée"""
        if user_query in self.cache_responses:
            cached = self.cache_responses[user_query]
            if isinstance(cached, list):
                for chunk in cached:
                    yield chunk
            else:
                yield cached
            return

        rag_chain = self.create_rag_chain()
        if not rag_chain:
            yield "Aucun document disponible pour répondre à la requête."
            return

        try:
            response_stream = rag_chain.stream(user_query)
            response_chunks = []
            
            for chunk in response_stream:
                response_chunks.append(chunk)
                yield chunk
            
            # Mettre en cache la réponse complète
            self.cache_responses[user_query] = response_chunks
            
            # Limiter la taille du cache (mémoire limitée)
            if len(self.cache_responses) > 50:
                # Supprimer les plus anciennes entrées
                oldest_keys = list(self.cache_responses.keys())[:10]
                for key in oldest_keys:
                    del self.cache_responses[key]
                    
        except Exception as e:
            error_msg = f"Erreur : {e}"
            yield error_msg

    def preload_model(self):
        """Précharger le modèle pour des réponses plus rapides"""
        try:
            # Faire une requête simple pour "chauffer" le modèle
            dummy_query = "test"
            list(self.llm.stream(dummy_query))
        except:
            pass