import React from 'react';
import { signInWithPopup, signInWithRedirect, getRedirectResult } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { useAuth } from '../contexts/AuthContext';

const GoogleOAuth = ({ userType = 'user', onSuccess, onError, buttonText }) => {
  const { firebaseAuth } = useAuth();

  // Configure Google provider to request additional user information
  React.useEffect(() => {
    googleProvider.addScope('profile');
    googleProvider.addScope('email');
    googleProvider.setCustomParameters({
      prompt: 'select_account'
    });
  }, []);

  const handleGoogleLogin = async () => {
    try {
      // Try popup first, fallback to redirect on mobile
      let result;
      try {
        result = await signInWithPopup(auth, googleProvider);
      } catch (popupError) {
        if (popupError.code === 'auth/popup-blocked') {
          // Fallback to redirect if popup is blocked
          await signInWithRedirect(auth, googleProvider);
          return;
        }
        throw popupError;
      }

      // Get Firebase ID token
      const idToken = await result.user.getIdToken();
      
      // Log user details for debugging
      console.log('Google user details:', {
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
        emailVerified: result.user.emailVerified,
        metadata: result.user.metadata
      });
      
      // Try as user first, then as admin if that fails and userType allows it
      let authResult = await firebaseAuth(idToken, 'user');
      
      // If user authentication fails and we're looking for admin, try admin auth
      if (!authResult.success && userType === 'admin') {
        authResult = await firebaseAuth(idToken, 'admin');
      }
      
      if (authResult.success) {
        console.log('✅ Google OAuth successful:', authResult.user?.email);
        if (onSuccess) {
          onSuccess(authResult);
        }
      } else {
        // Handle specific error messages from backend
        const errorMessage = authResult.error || 'Authentication failed';
        console.error('❌ Firebase auth failed:', errorMessage);
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Firebase OAuth error:', error);
      
      // Provide user-friendly error messages
      let userMessage = 'Authentication failed. Please try again.';
      
      if (error.code === 'auth/popup-closed-by-user') {
        userMessage = 'Sign-in was cancelled. Please try again.';
      } else if (error.code === 'auth/network-request-failed') {
        userMessage = 'Network error. Please check your connection and try again.';
      } else if (error.code === 'auth/too-many-requests') {
        userMessage = 'Too many sign-in attempts. Please wait a moment and try again.';
      } else if (error.message) {
        // Use backend error messages if available
        userMessage = error.message;
      }
      
      if (onError) {
        onError(userMessage);
      }
    }
  };

  // Handle redirect result on component mount
  React.useEffect(() => {
    const handleRedirectResult = async () => {
      try {
        const result = await getRedirectResult(auth);
        if (result) {
          const idToken = await result.user.getIdToken();
          
          // Log user details for debugging
          console.log('Google redirect user details:', {
            uid: result.user.uid,
            email: result.user.email,
            displayName: result.user.displayName,
            photoURL: result.user.photoURL,
            emailVerified: result.user.emailVerified
          });
          
          // Try as user first, then as admin if that fails and userType allows it
          let authResult = await firebaseAuth(idToken, 'user');
          
          // If user authentication fails and we're looking for admin, try admin auth
          if (!authResult.success && userType === 'admin') {
            authResult = await firebaseAuth(idToken, 'admin');
          }
          
          if (authResult.success) {
            if (onSuccess) {
              onSuccess(authResult);
            }
          } else {
            throw new Error(authResult.error);
          }
        }
      } catch (error) {
        console.error('Redirect result error:', error);
        if (onError) {
          onError(error.message || 'Authentication failed');
        }
      }
    };

    handleRedirectResult();
  }, [userType, onSuccess, onError, firebaseAuth]);

  return (
    <button
      onClick={handleGoogleLogin}
      className="google-oauth-btn"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '10px',
        padding: '12px 20px',
        backgroundColor: '#fff',
        border: '1px solid #dadce0',
        borderRadius: '6px',
        color: '#3c4043',
        fontSize: '14px',
        fontWeight: '500',
        cursor: 'pointer',
        minWidth: '200px',
        transition: 'all 0.2s',
        width: '100%'
      }}
      onMouseEnter={(e) => {
        e.target.style.backgroundColor = '#f8f9fa';
        e.target.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
      }}
      onMouseLeave={(e) => {
        e.target.style.backgroundColor = '#fff';
        e.target.style.boxShadow = 'none';
      }}
    >
      <svg width="18" height="18" viewBox="0 0 24 24">
        <path
          fill="#4285f4"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="#34a853"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="#fbbc05"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="#ea4335"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
      {buttonText || (userType === 'admin' ? 'Sign in with Google (Admin)' : 'Sign in with Google')}
    </button>
  );
};

export default GoogleOAuth;
