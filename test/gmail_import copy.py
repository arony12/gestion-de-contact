from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def importer_contacts_gmail():
    """Récupère les contacts Gmail de l'utilisateur connecté"""
    creds = None

    # Si un token existe déjà, on le recharge
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Sinon, on demande la connexion via navigateur
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Sauvegarde du token pour les connexions futures
        with open('token.json', 'w') as token:
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

        nom = names[0]['displayName'] if names else "Inconnu"
        email = emails[0]['value'] if emails else "Aucun"
        tel = phones[0]['value'] if phones else "Aucun"

        contacts.append([nom, tel, email])

    return contacts
