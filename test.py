import streamlit as st
import os

uploaded_files = st.file_uploader(
    "Choose a CSV file", accept_multiple_files=True
)

# Dossier où tu veux conserver les fichiers
save_dir = "uploads"
os.makedirs(save_dir, exist_ok=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Construire le chemin de destination
        save_path = os.path.join(save_dir, uploaded_file.name)
        
        # Sauvegarder le fichier sur le disque
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Fichier sauvegardé : {save_path}")
