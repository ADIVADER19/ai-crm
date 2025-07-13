import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { crmAPI, chatAPI } from '../services/api';
import Spinner from '../components/Spinner';
import './Profile.css';

const Profile = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    company: '',
    preferences: ''
  });
  const [conversations, setConversations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [expandedConversations, setExpandedConversations] = useState([]);

  useEffect(() => {
    if (user) {
      loadUserData();
    }
  }, [user]);

  const loadUserData = async () => {
    setLoading(true);
    try {
      const userResponse = await crmAPI.getUser(user.user_id);
      if (userResponse.user) {
        setProfileData(userResponse.user);
      }

      const conversationsResponse = await crmAPI.getConversations(user.user_id);
      if (conversationsResponse.conversations) {
        setConversations(conversationsResponse.conversations);
      }

      const categoriesResponse = await chatAPI.getCategories();
      if (categoriesResponse.categories && Array.isArray(categoriesResponse.categories)) {
        setCategories(categoriesResponse.categories);
      } else {
        console.warn('Categories not found or not an array:', categoriesResponse);
        setCategories([]);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
      setMessage('Failed to load profile data');
      setCategories([]);
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      await crmAPI.updateUser(user.user_id, {
        company: profileData.company,
        preferences: profileData.preferences
      });
      setMessage('Profile updated successfully!');
    } catch (error) {
      setMessage('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      'property_search': '#3b82f6',
      'general_inquiry': '#10b981', 
      'pricing_inquiry': '#f59e0b',
      'default': '#6b7280'
    };
    return colors[category] || colors.default;
  };

  const toggleConversation = (index) => {
    setExpandedConversations(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  if (loading) {
    return (
      <div className="profile-container">
        <Spinner size="large" message="Loading your profile..." />
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>User Profile</h1>
        <p>Manage your account settings and preferences</p>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <div className="section-header">
            <h2>👤 Profile Information</h2>
          </div>
          
          <form onSubmit={handleSaveProfile} className="profile-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={profileData.name}
                  onChange={handleInputChange}
                  disabled
                  className="readonly-input"
                />
                <small>Name cannot be changed</small>
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleInputChange}
                  disabled
                  className="readonly-input"
                />
                <small>Email cannot be changed</small>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="company">Company</label>
              <input
                type="text"
                id="company"
                name="company"
                value={profileData.company}
                onChange={handleInputChange}
                placeholder="Enter your company name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="preferences">Preferences</label>
              <textarea
                id="preferences"
                name="preferences"
                value={profileData.preferences}
                onChange={handleInputChange}
                placeholder="Describe your property preferences, budget, location preferences, etc."
                rows="4"
              />
            </div>

            {message && (
              <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
                {message}
              </div>
            )}

            <button 
              type="submit" 
              className="save-button"
              disabled={saving}
            >
              {saving ? (
                <>
                  <Spinner size="small" message="" />
                  <span style={{ marginLeft: '8px' }}>Saving...</span>
                </>
              ) : (
                '💾 Save Changes'
              )}
            </button>
          </form>
        </div>

        <div className="profile-section">
          <div className="section-header">
            <h2>📊 Activity Overview</h2>
          </div>
          
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{conversations.length}</div>
              <div className="stat-label">Total Conversations</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-number">{categories.length}</div>
              <div className="stat-label">Categories Used</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-number">
                {categories.reduce((total, categoryObj) => total + (categoryObj.count || 0), 0)}
              </div>
              <div className="stat-label">Categorized Conversations</div>
            </div>
          </div>

          {categories.length > 0 && (
            <div className="categories-section">
              <h3>Your Conversation Categories</h3>
              <div className="category-tags">
                {categories.map((categoryObj, index) => (
                  <span 
                    key={index} 
                    className="category-tag"
                    style={{ backgroundColor: getCategoryColor(categoryObj.category) }}
                  >
                    {categoryObj.category.replace('_', ' ').toUpperCase()} ({categoryObj.count})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="profile-section">
          <div className="section-header">
            <h2>💬 Recent Conversations</h2>
          </div>
          
          {conversations.length > 0 ? (
            <div className="conversations-list">
              {conversations.map((conversation, index) => (
                <div key={index} className="conversation-card">
                  <div 
                    className="conversation-header clickable"
                    onClick={() => toggleConversation(index)}
                  >
                    <div className="conversation-info">
                      <span 
                        className="conversation-category"
                        style={{ backgroundColor: getCategoryColor(conversation.category) }}
                      >
                        {conversation.category?.replace('_', ' ') || 'General'}
                      </span>
                      <span className="conversation-date">
                        {formatDate(conversation.created_at)}
                      </span>
                    </div>
                    <span className="expand-icon">
                      {expandedConversations.includes(index) ? '▼' : '▶'}
                    </span>
                  </div>
                  
                  <div className="conversation-preview">
                    {expandedConversations.includes(index) ? (
                      <div className="all-messages">
                        {conversation.messages?.map((message, msgIndex) => (
                          <div key={msgIndex} className={`message-full ${message.role}`}>
                            <div className="message-header">
                              <strong>{message.role === 'user' ? 'You' : 'AI Assistant'}</strong>
                              <span className="message-time">
                                {formatDate(message.timestamp || conversation.created_at)}
                              </span>
                            </div>
                            <div className="message-content">
                              {message.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      conversation.messages?.slice(0, 2).map((message, msgIndex) => (
                        <div key={msgIndex} className={`message-preview ${message.role}`}>
                          <strong>{message.role === 'user' ? 'You' : 'AI'}:</strong>
                          <span>{message.content.substring(0, 100)}...</span>
                        </div>
                      ))
                    )}
                  </div>
                  
                  <div className="conversation-stats">
                    {conversation.messages?.length || 0} messages
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No conversations yet. Start chatting to see your history here!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
