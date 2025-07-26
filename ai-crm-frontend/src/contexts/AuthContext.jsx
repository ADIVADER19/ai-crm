import React, { createContext, useContext, useState, useEffect } from 'react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '../firebase';
import { authAPI, crmAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [firebaseUser, setFirebaseUser] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authAPI.getMe();
          setUser({
            ...userData,
            role: userData.role || 'user' // Ensure role is included
          });
        } catch (error) {
          console.error('Auth initialization failed:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  // Listen for Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setFirebaseUser(firebaseUser);
    });

    return unsubscribe;
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token } = response;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      const userData = await authAPI.getMe();
      setUser({
        ...userData,
        role: userData.role || 'user' // Ensure role is included
      });
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await crmAPI.createUser(userData);
      return { success: true, data: response };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      // Also sign out from Firebase
      if (firebaseUser) {
        await signOut(auth);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setToken(null);
      setUser(null);
      setFirebaseUser(null);
    }
  };

  // Firebase authentication with backend integration
  const firebaseAuth = async (idToken, userType = 'user') => {
    try {
      const response = await authAPI.firebaseAuth(idToken, userType);
      const { access_token } = response;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      setToken(access_token);
      setUser({
        ...response.user,
        role: response.user.role || 'user'
      });
      
      return { success: true, user: response.user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Firebase authentication failed' 
      };
    }
  };

  const value = {
    user,
    token,
    firebaseUser,
    login,
    signup,
    logout,
    firebaseAuth,
    loading,
    isAuthenticated: !!token && !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
