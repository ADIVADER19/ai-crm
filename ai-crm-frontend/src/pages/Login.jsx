import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import GoogleOAuth from '../components/GoogleOAuth';
import './Auth.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
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
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? 
            <Link to="/signup" className="auth-link"> Sign Up</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
