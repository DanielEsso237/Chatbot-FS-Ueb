import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    print("Connexion à la base de données réussie !")
    conn.close()
except psycopg2.OperationalError as e:
    print(f"Échec de la connexion à la base de données : {e}")