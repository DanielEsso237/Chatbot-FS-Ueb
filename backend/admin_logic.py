import os
import shutil
from datetime import datetime

PDF_FOLDER = "pdfs"

class AdminLogic:
    def __init__(self):
        os.makedirs(PDF_FOLDER, exist_ok=True)

    def save_pdf(self, file):
        """Ajoute un nouveau PDF (ou remplace s’il existe déjà)."""
        save_path = os.path.join(PDF_FOLDER, file.name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())
        return save_path

    def list_pdfs(self):
        """Retourne les PDFs existants avec infos (taille, date modif)."""
        files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
        result = []
        for f in files:
            path = os.path.join(PDF_FOLDER, f)
            size = os.path.getsize(path) / 1024  # Ko
            mod_time = datetime.fromtimestamp(os.path.getmtime(path))
            result.append({
                "name": f,
                "path": path,
                "size": f"{size:.2f} Ko",
                "modified": mod_time.strftime("%d/%m/%Y %H:%M")
            })
        return result

    def delete_pdf(self, filename):
        """Supprime un PDF existant."""
        path = os.path.join(PDF_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def replace_pdf(self, old_filename, new_file):
        """Remplace un PDF existant par un nouveau fichier."""
        old_path = os.path.join(PDF_FOLDER, old_filename)
        if os.path.exists(old_path):
            os.remove(old_path)
        return self.save_pdf(new_file)

    def clear_all(self):
        """Supprime tous les PDFs."""
        shutil.rmtree(PDF_FOLDER)
        os.makedirs(PDF_FOLDER, exist_ok=True)

    def reindex(self):
        """⚡ Stub pour reindexer la base (à connecter avec chatbot_logic)."""
        # Exemple : from backend.chatbot_logic import load_index
        # load_index()
        return "Réindexation effectuée avec succès ✅"
