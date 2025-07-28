import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
import { auth } from '../firebase';
import { useAuth } from '../contexts/AuthContext';
import { crmAPI } from '../services/api';
import GoogleOAuth from '../components/GoogleOAuth';
import './Auth.css';

const SignUp = () => {
  const navigate = useNavigate();
  const { firebaseAuth } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    company: '',
    preferences: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [firebaseLoading, setFirebaseLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
    setSuccess('');

    try {
      await crmAPI.createUser(formData);
      setSuccess('Account created successfully! Please login with your credentials.');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  // Firebase Email/Password Signup
  const handleFirebaseSignUp = async () => {
    if (!formData.email || !formData.password || !formData.name) {
      setError('Please fill in all required fields (name, email, password)');
      return;
    }

    setFirebaseLoading(true);
    setError('');
    setSuccess('');

    try {
      // Create Firebase user
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        formData.email, 
        formData.password
      );

      // Update Firebase profile with name
      await updateProfile(userCredential.user, {
        displayName: formData.name
      });

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();

      // Authenticate with backend and create user profile
      const authResult = await firebaseAuth(idToken, 'user');

      if (authResult.success) {
        // Create additional user profile data in CRM
        try {
          await crmAPI.createUser({
            name: formData.name,
            email: formData.email,
            company: formData.company || '',
            phone: formData.phone || '',
            preferences: formData.preferences || '',
            firebase_uid: userCredential.user.uid,
            auth_provider: 'firebase'
          });
        } catch (crmError) {
          console.warn('CRM profile creation failed:', crmError);
          // Continue anyway since the user is created in Firebase and backend
        }

        setSuccess('Firebase account created successfully!');
        setTimeout(() => {
          navigate('/login');
        }, 1500);
      } else {
        throw new Error(authResult.error);
      }
    } catch (error) {
      console.error('Firebase signup error:', error);
      setError(error.message || 'Failed to create Firebase account');
    } finally {
      setFirebaseLoading(false);
    }
  };

  const handleGoogleSuccess = (result) => {
    // Redirect to login page instead of auto-login
    setSuccess('Account created successfully! Please login with your credentials.');
    setTimeout(() => {
      navigate('/login');
    }, 2000);
  };

  const handleGoogleError = (error) => {
    // Check if user already exists
    if (error && error.includes('User already exists')) {
      setError('User already exists. Please proceed to login instead of signing up.');
      // Optionally redirect to login after showing the message
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } else {
      setError(error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Sign Up</h1>
          <p>Create your RentRadar account</p>
        </div>

        {/* Google OAuth for easy signup */}
        <div className="oauth-section">
          <div className="oauth-buttons">
            <GoogleOAuth
              userType="user"
              mode="signup"
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              buttonText="Sign up with Google"
            />
          </div>
          
          <div className="divider">
            <span>OR</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
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
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
              minLength="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="company">Company</label>
            <input
              type="text"
              id="company"
              name="company"
              value={formData.company}
              onChange={handleChange}
              placeholder="Enter your company name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="Enter your phone number"
            />
          </div>

          <div className="form-group">
            <label htmlFor="preferences">Preferences</label>
            <textarea
              id="preferences"
              name="preferences"
              value={formData.preferences}
              onChange={handleChange}
              placeholder="Describe your property preferences, budget, location preferences, etc."
              rows="4"
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>

          {/* Firebase Email Sign Up Option */}
          <button 
            type="button"
            onClick={handleFirebaseSignUp}
            className="auth-button"
            disabled={firebaseLoading}
            style={{
              backgroundColor: '#4285f4',
              color: 'white',
              marginTop: '10px'
            }}
          >
            {firebaseLoading ? 'Creating Firebase Account...' : 'Sign Up with Firebase'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account? 
            <Link to="/login" className="auth-link"> Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
