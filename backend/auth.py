import psycopg2
import bcrypt
import os

class AuthManager:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.conn = self._connect()

    def _connect(self):
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            print("Connexion à la base de données réussie")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Erreur PostgreSQL: {e}")
            return None

    def register_user(self, username, email, password):
        if not self.conn:
            return False, "Erreur de connexion à la base de données."
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT username FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            if cursor.fetchone():
                cursor.close()
                return False, "Le nom d'utilisateur ou l'email existe déjà."

            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')  
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password_str, "user")
            )
            self.conn.commit()
            cursor.close()
            return True, "Inscription réussie."
        except Exception as e:
            print(f"Erreur lors de l'inscription: {e}")
            return False, f"Erreur: {e}"

    def login_user(self, username, password):
        if not self.conn:
            return False, "Erreur de connexion à la base de données.", None, None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT username, password_hash, role FROM users WHERE username = %s",
                (username,)
            )
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
               
                stored_password_hash = user_data[1].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                    return True, "Connexion réussie.", user_data[0], user_data[2]
                else:
                    return False, "Mot de passe incorrect.", None, None
            else:
                return False, "Utilisateur non trouvé.", None, None
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False, f"Erreur: {e}", None, None

    def check_user_exists(self, username):
        """Vérifier si un utilisateur existe dans la base de données."""
        if not self.conn:
            return False, "Erreur de connexion à la base de données.", None, None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT username, role FROM users WHERE username = %s",
                (username,)
            )
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return True, "Utilisateur trouvé.", user_data[0], user_data[1]
            else:
                return False, "Utilisateur non trouvé.", None, None
        except Exception as e:
            print(f"Erreur lors de la vérification de l'utilisateur: {e}")
            return False, f"Erreur: {e}", None, None

    def __del__(self):
        if self.conn:
            self.conn.close()
            print("Connexion à la base de données fermée")