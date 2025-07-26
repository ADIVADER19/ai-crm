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
        """Verify Firebase ID token and return comprehensive user info"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract comprehensive user information
            user_info = {
                'firebase_uid': decoded_token['uid'],
                'email': decoded_token.get('email', ''),
                'name': decoded_token.get('name', ''),
                'picture': decoded_token.get('picture', ''),
                'email_verified': decoded_token.get('email_verified', False),
                'provider': decoded_token.get('firebase', {}).get('sign_in_provider', 'google.com'),
                'auth_time': decoded_token.get('auth_time'),
                'iss': decoded_token.get('iss'),
                'aud': decoded_token.get('aud'),
                'exp': decoded_token.get('exp'),
                'iat': decoded_token.get('iat'),
            }
            
            # Add additional Google-specific information if available
            firebase_data = decoded_token.get('firebase', {})
            if 'identities' in firebase_data:
                identities = firebase_data['identities']
                if 'google.com' in identities:
                    user_info['google_id'] = identities['google.com'][0] if identities['google.com'] else None
                    
            print(f"🔍 Firebase token verified for user: {user_info['email']}")
            return user_info
            
        except auth.InvalidIdTokenError as e:
            print(f"❌ Invalid Firebase ID token: {e}")
            return None
        except auth.ExpiredIdTokenError as e:
            print(f"❌ Expired Firebase ID token: {e}")
            return None
        except Exception as e:
            print(f"❌ Firebase token verification error: {e}")
            return None
        except Exception as e:
            print(f"Firebase token verification error: {e}")
            return None

firebase_auth = FirebaseAuthService()
