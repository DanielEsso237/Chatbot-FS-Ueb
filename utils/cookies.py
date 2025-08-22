import streamlit.components.v1 as components
import json

def set_cookie(key, value):
    """
    Définit un cookie dans le navigateur de l'utilisateur.
    """
    cookie_script = f"""
    <script>
        document.cookie = "{key}={value}; max-age=86400; path=/";
    </script>
    """
    components.html(cookie_script, height=0)

def get_cookie(key):
    """
    Récupère la valeur d'un cookie.
    """
    get_script = f"""
    <script>
        const value = document.cookie.split('; ').find(row => row.startsWith('{key}')).split('=')[1];
        window.parent.document.dispatchEvent(new CustomEvent('streamlit:component:value', {{ detail: value }}));
    </script>
    """
    # Streamlit n'a pas de retour direct pour les scripts JS. Pour une solution simple
    # nous allons retourner None et utiliser la logique principale pour vérifier
    # la présence du cookie. Pour cette démo, la logique principale le cherchera
    # directement.
    return None

def get_cookie_value_from_js(key):
    """
    Récupère la valeur du cookie en utilisant le contexte JavaScript.
    """
    js_code = f"""
        let value = null;
        const cookies = document.cookie.split(';');
        for(let i = 0; i < cookies.length; i++) {{
            let cookie = cookies[i].trim();
            if (cookie.startsWith('{key}=')) {{
                value = cookie.substring('{key}='.length, cookie.length);
                break;
            }}
        }}
        return value;
    """
    return components.html(f"<script>{js_code}</script>", height=0, width=0)

