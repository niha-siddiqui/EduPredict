import firebase_admin
from firebase_admin import credentials , firestore

cred = credentials.Certificate("edupredict.json")
firebase_admin.initialize_app(cred)

database = firestore.client()