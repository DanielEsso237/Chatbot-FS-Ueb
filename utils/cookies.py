import streamlit.components.v1 as components

def set_cookie(key, value, max_age=86400):
    """
    Définit un cookie dans le navigateur de l'utilisateur.
    """
    cookie_script = f"""
    <script>
        document.cookie = "{key}={value}; max-age={max_age}; path=/";
    </script>
    """
    components.html(cookie_script, height=0)

def get_cookie(key):
    """
    Récupère la valeur d'un cookie (simplifié, retourne None car Streamlit ne peut pas récupérer directement les valeurs JS).
    """
    # Comme Streamlit ne peut pas récupérer directement les valeurs JS, on s'appuie sur la session state
    return None