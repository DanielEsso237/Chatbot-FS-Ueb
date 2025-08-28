import psycopg2
import bcrypt
import os

class AuthManager:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")

    def _connect(self):
        try:
            return psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
        except psycopg2.OperationalError as e:
            print("Erreur PostgreSQL :", e)
            return None

    def hash_password(self, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def check_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, email, password, role="user"):
        conn = self._connect()
        if not conn:
            return False, "Erreur de connexion à la base de données."

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM users WHERE username = %s OR email = %s",
                    (username, email)
                )
                if cur.fetchone()[0] > 0:
                    return False, "Le nom d'utilisateur ou l'e-mail est déjà utilisé."

                hashed_password = self.hash_password(password)
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (username, email, hashed_password, role)
                )
            conn.commit()
            return True, "Inscription réussie !"
        except psycopg2.Error:
            conn.rollback()
            return False, "Une erreur est survenue lors de l'inscription."
        finally:
            if conn:
                conn.close()

    def login_user(self, username, password):
        conn = self._connect()
        if not conn:
            return False, "Erreur de connexion à la base de données.", None, None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password_hash, role FROM users WHERE username = %s",
                    (username,)
                )
                result = cur.fetchone()
                if result:
                    hashed_password, role = result
                    if self.check_password(password, hashed_password):
                        return True, "Connexion réussie.", username, role
                    else:
                        return False, "Mot de passe incorrect.", None, None
                else:
                    return False, "Nom d'utilisateur non trouvé.", None, None
        except psycopg2.Error:
            return False, "Une erreur est survenue lors de la connexion.", None, None
        finally:
            if conn:
                conn.close()
