import os
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional, Dict
import json

class FirebaseAuthService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            # Check if service account key exists
            service_account_key = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            
            if service_account_key:
                try:
                    # Parse the service account key JSON
                    service_account_info = json.loads(service_account_key)
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin initialized with service account")
                except Exception as e:
                    print(f"❌ Firebase initialization error: {e}")
                    # Fallback to default credentials
                    firebase_admin.initialize_app()
            else:
                # Use default credentials (for local development)
                firebase_admin.initialize_app()
                print("⚠️ Firebase Admin initialized with default credentials")
    
    def verify_firebase_token(self, id_token: str) -> Optional[Dict]:
        """Verify Firebase ID token and return user info"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            return {
                'firebase_uid': decoded_token['uid'],
                'email': decoded_token.get('email', ''),
                'name': decoded_token.get('name', ''),
                'picture': decoded_token.get('picture', ''),
                'email_verified': decoded_token.get('email_verified', False),
                'provider': decoded_token.get('firebase', {}).get('sign_in_provider', 'google.com')
            }
            
        except auth.InvalidIdTokenError:
            print("Invalid Firebase ID token")
            return None
        except auth.ExpiredIdTokenError:
            print("Expired Firebase ID token")
            return None
        except Exception as e:
            print(f"Firebase token verification error: {e}")
            return None

firebase_auth = FirebaseAuthService()
