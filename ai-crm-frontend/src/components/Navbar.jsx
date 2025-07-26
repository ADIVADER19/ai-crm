import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <Link to="/chat" className="brand-link">
            <span className="brand-icon">🏢</span>
            RentRadar
          </Link>
        </div>

        <div className="navbar-menu">
          <div className="navbar-nav">
            <Link 
              to="/chat" 
              className={`nav-link ${isActive('/chat') ? 'active' : ''}`}
            >
              💬 Chat
            </Link>
            <Link 
              to="/profile" 
              className={`nav-link ${isActive('/profile') ? 'active' : ''}`}
            >
              👤 Profile
            </Link>
            {user?.role === 'admin' && (
              <Link 
                to="/admin" 
                className={`nav-link admin-link ${isActive('/admin') ? 'active' : ''}`}
              >
                🛠️ Admin
              </Link>
            )}
          </div>

          <div className="navbar-user">
            <div className="user-info">
              <span className="user-name">
                {user?.name || user?.email}
              </span>
              {user?.company && (
                <span className="user-company">{user.company}</span>
              )}
            </div>
            <button onClick={handleLogout} className="logout-button">
              🚪 Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
