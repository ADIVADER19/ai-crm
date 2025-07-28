import os
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional, Dict
import json
import requests

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
                    
                    # Fix the private key formatting if needed
                    if 'private_key' in service_account_info:
                        private_key = service_account_info['private_key']
                        # Ensure proper newline formatting for PEM
                        if '\\n' in private_key:
                            private_key = private_key.replace('\\n', '\n')
                            service_account_info['private_key'] = private_key
                    
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin initialized with service account")
                    self.use_admin_sdk = True
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON in service account key: {e}")
                    self.use_admin_sdk = False
                except Exception as e:
                    print(f"❌ Firebase initialization error: {e}")
                    # Fallback to REST API
                    self.use_admin_sdk = False
            else:
                # Try default credentials first
                try:
                    firebase_admin.initialize_app()
                    print("⚠️ Firebase Admin initialized with default credentials")
                    self.use_admin_sdk = True
                except Exception as e:
                    print(f"⚠️ Firebase Admin SDK failed, using REST API fallback: {e}")
                    self.use_admin_sdk = False
    
    def verify_firebase_token_rest(self, id_token: str) -> Optional[Dict]:
        """Verify Firebase token using REST API as fallback"""
        try:
            api_key = os.getenv("VITE_FIREBASE_API_KEY") or "AIzaSyCsFSNPAt6doEiiKGE2-IHMUbKvG29y3ow"
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
            
            payload = {"idToken": id_token}
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "users" in data and len(data["users"]) > 0:
                    user_data = data["users"][0]
                    
                    # Extract user information
                    user_info = {
                        'firebase_uid': user_data.get('localId', ''),
                        'email': user_data.get('email', ''),
                        'name': user_data.get('displayName', ''),
                        'picture': user_data.get('photoUrl', ''),
                        'email_verified': user_data.get('emailVerified', False),
                        'provider': 'google.com'
                    }
                    
                    print(f"✅ Token verified via REST API for: {user_info['email']}")
                    return user_info
                    
            print(f"❌ REST API verification failed: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ REST API verification error: {e}")
            return None
    
    def verify_firebase_token(self, id_token: str) -> Optional[Dict]:
        """Verify Firebase ID token and return comprehensive user info"""
        
        # Try Admin SDK first if available
        if self.use_admin_sdk:
            try:
                print("🔍 Attempting to verify Firebase token with Admin SDK...")
                decoded_token = auth.verify_id_token(id_token)
                print("✅ Token decoded successfully with Admin SDK")
                
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
                print(f"❌ Invalid Firebase ID token with Admin SDK: {e}")
                # Fall back to REST API
            except auth.ExpiredIdTokenError as e:
                print(f"❌ Expired Firebase ID token with Admin SDK: {e}")
                return None
            except Exception as e:
                print(f"❌ Firebase Admin SDK verification error: {e}")
                # Fall back to REST API
        
        # Fallback to REST API verification
        print("🔄 Falling back to REST API verification...")
        return self.verify_firebase_token_rest(id_token)

firebase_auth = FirebaseAuthService()
