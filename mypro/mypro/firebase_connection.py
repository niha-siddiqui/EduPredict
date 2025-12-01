import firebase_admin
from firebase_admin import credentials , firestore

cred = credentials.Certificate("edu.json")
firebase_admin.initialize_app(cred)

database = firestore.client()