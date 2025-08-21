import os
import json
import requests
import streamlit as st
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss

class VectorialSearchGemma:
    def __init__(self, pdf_folder, index_file="index.faiss", data_file="data.json"):
        self.pdf_folder = pdf_folder
        self.index_file = index_file
        self.data_file = data_file
        self.model_path = r"C:\Users\T.SHIGARAKI\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L12-v2\snapshots\c004d8e3e901237d8fa7e9fff12774962e391ce5"
        self.model = SentenceTransformer(self.model_path)
        self.index = None
        self.texts = []
        self.api_url = "http://127.0.0.1:11434/api/generate"  # endpoint correct
        self.system_prompt = """
Tu es un assistant spécialisé en extraction d’informations depuis des documents PDF.
Réponds uniquement avec les informations présentes dans le contexte fourni.
- Si la réponse est dans le contexte → répond de façon concise et claire (max 3 phrases).
- Si la réponse n’est pas dans le contexte → répond exactement : "question hors contexte".
- Toujours en français.
"""

    # Extraction et préparation des textes
    def prepare_data(self):
        if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.texts = json.load(f)
        else:
            self.texts = self.extract_texts_from_pdfs()
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=2)

    def extract_texts_from_pdfs(self):
        texts = []
        for file in os.listdir(self.pdf_folder):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(self.pdf_folder, file)
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
        return texts

    # FAISS
    def build_index(self):
        print("Création de l'index FAISS à partir des textes...")
        embeddings = self.model.encode(self.texts)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        faiss.write_index(self.index, self.index_file)
        print("Index FAISS créé et sauvegardé.")

    def load_index(self):
        if os.path.exists(self.index_file):
            print("Chargement de l'index FAISS existant...")
            self.index = faiss.read_index(self.index_file)
        else:
            print("Index FAISS non trouvé, construction en cours...")
            self.build_index()
    
        if self.index is None:
            raise ValueError("Index FAISS non initialisé !")

    def search_pdfs(self, query, top_k=3):
      if self.index is None:
        raise ValueError("Index FAISS non initialisé !")
    
      query_embedding = self.model.encode([query])
      distances, indices = self.index.search(query_embedding, top_k)
      results = [self.texts[i] for i in indices[0]]

      print("\n📄 Résultats FAISS complets (debug) :")
      for i, res in enumerate(results):
        print(f"\n--- Résultat {i+1} ---\n{res}\n")  # affichage complet
        print("-" * 50)
    
      # On peut concaténer pour Gemma
      return results


    # Gemma interaction via Ollama API (HTTP) – version simple sans streaming
    def ask_gemma(self, query, context):
      prompt = f"{self.system_prompt}\nContexte:\n{context}\nQuestion: {query}\nRéponse :"

      try:
         response = requests.post(
            self.api_url,
            headers={"Content-Type": "application/json"},
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "max_tokens": 256,
                "temperature": 0.2
            },
            
         )

         if response.status_code != 200:
            return f"[ERREUR GEMMA API] {response.status_code}: {response.text}"

         # Lire le flux JSON concaténé ligne par ligne
         full_response = ""
         for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "response" in data:
                    full_response += data["response"]
            except json.JSONDecodeError:
                continue

         if not full_response:
            return "Pas de réponse."
         return full_response

      except requests.exceptions.RequestException as e:
        return f"[ERREUR GEMMA API] {str(e)}"




    # Streamlit interface
    def render(self):
      # Sidebar avec logo
      logo_path = "assets/logo.png"  # chemin vers ton image
      if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=50)  # ajuste la largeur si nécessaire
      st.sidebar.markdown("**Chatbot FS-Ueb**")  # titre dans la sidebar

      # Titre principal
      st.title("Chatbot FS-Ueb")

      if "messages" not in st.session_state:
        st.session_state.messages = []

      for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

      if user_query := st.chat_input("Pose une question en relation avec tes PDF"):
        context_list = self.search_pdfs(user_query, top_k=1)
        context_text = " ".join(context_list)

        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("assistant"):
            response = self.ask_gemma(user_query, context_text)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    vs = VectorialSearchGemma(pdf_folder="pdfs")
    vs.prepare_data()
    vs.load_index()
    vs.render()
