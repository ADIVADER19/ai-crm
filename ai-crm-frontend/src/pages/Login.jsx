import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase';
import { useAuth } from '../contexts/AuthContext';
import GoogleOAuth from '../components/GoogleOAuth';
import './Auth.css';

const Login = () => {
  const navigate = useNavigate();
  const { login, firebaseAuth } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [firebaseLoading, setFirebaseLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      navigate('/chat');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  // Firebase Email/Password Login
  const handleFirebaseLogin = async (e) => {
    e.preventDefault();
    setFirebaseLoading(true);
    setError('');

    try {
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(
        auth, 
        formData.email, 
        formData.password
      );

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();

      // Authenticate with backend
      const authResult = await firebaseAuth(idToken, 'user');

      if (authResult.success) {
        // Navigate based on user role
        if (authResult.user?.role === 'admin') {
          navigate('/admin');
        } else {
          navigate('/chat');
        }
      } else {
        throw new Error(authResult.error);
      }
    } catch (error) {
      console.error('Firebase login error:', error);
      setError(error.message || 'Failed to sign in with Firebase');
    } finally {
      setFirebaseLoading(false);
    }
  };

  const handleGoogleSuccess = (result) => {
    // Navigate based on user role
    if (result.user?.role === 'admin') {
      navigate('/admin');
    } else {
      navigate('/chat');
    }
  };

  const handleGoogleError = (error) => {
    setError(error);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Sign in to your RentRadar account</p>
        </div>

        {/* Google OAuth for Users */}
        <div className="oauth-section">
          <div className="oauth-buttons">
            <GoogleOAuth
              userType="user"
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              buttonText="Continue with Google"
            />
          </div>
          
          <div className="divider">
            <span>OR</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>

          {/* Firebase Email/Password Login */}
          <button 
            type="button"
            onClick={handleFirebaseLogin}
            className="auth-button"
            disabled={firebaseLoading}
            style={{
              backgroundColor: '#4285f4',
              color: 'white',
              marginTop: '10px'
            }}
          >
            {firebaseLoading ? 'Firebase Signing In...' : 'Sign In with Firebase'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? 
            <Link to="/signup" className="auth-link"> Sign Up</Link>
          </p>
        </div>

        <div className="demo-credentials">
          <h4>Demo Credentials:</h4>
          <p><strong>Email:</strong> soham@example.com</p>
          <p><strong>Password:</strong> 123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
