from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --- AJOUTS POUR LA GESTION DES CHEMINS ---
# Le dossier où se trouve ce script
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__)) 
CLIENT_SECRET_FILE = os.path.join(DOSSIER_SCRIPT, 'client_secret.json')
TOKEN_FILE = os.path.join(DOSSIER_SCRIPT, 'token.json')

SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def nettoyer_fichiers_json():
    """Supprime les fichiers JSON (token et client_secret) s'ils existent"""
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print(f"✓ Fichier {TOKEN_FILE} supprimé")
        
        if os.path.exists(CLIENT_SECRET_FILE):
            os.remove(CLIENT_SECRET_FILE)
            print(f"✓ Fichier {CLIENT_SECRET_FILE} supprimé")
    except Exception as e:
        print(f"Erreur lors de la suppression des fichiers JSON: {e}")

def importer_contacts_gmail():
    """Récupère les contacts Gmail de l'utilisateur connecté"""
    creds = None

    # Si un token existe déjà, on le recharge (utilise le chemin corrigé)
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Sinon, on demande la connexion via navigateur
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Utilise le chemin corrigé pour le secret
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarde du token pour les connexions futures (utilise le chemin corrigé)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('people', 'v1', credentials=creds)

    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=100,
        personFields='names,emailAddresses,phoneNumbers'
    ).execute()

    connections = results.get('connections', [])
    contacts = []

    for person in connections:
        names = person.get('names', [])
        emails = person.get('emailAddresses', [])
        phones = person.get('phoneNumbers', [])

        # Amélioration: gérer les cas où les listes sont vides pour éviter des erreurs d'indexation
        nom = names[0]['displayName'] if names and 'displayName' in names[0] else "Inconnu"
        email = emails[0]['value'] if emails and 'value' in emails[0] else "Aucun"
        tel = phones[0]['value'] if phones and 'value' in phones[0] else "Aucun"

        contacts.append([nom, tel, email])

    # Suppression automatique des fichiers JSON après l'import
    nettoyer_fichiers_json()

    return contacts