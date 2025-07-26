import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { crmAPI } from '../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [updatingRole, setUpdatingRole] = useState(null);

  // Redirect if not admin
  if (user?.role !== 'admin') {
    return (
      <div className="admin-dashboard">
        <div className="access-denied">
          <h2>Access Denied</h2>
          <p>You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.name) params.append('name', filters.name);
      if (filters.email) params.append('email', filters.email);
      if (filters.phone) params.append('phone', filters.phone);
      
      const response = await crmAPI.getAllUsers(params.toString());
      setUsers(response);
      setError('');
    } catch (err) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleUpdate = async (userId, newRole) => {
    try {
      setUpdatingRole(userId);
      await crmAPI.updateUserRole(userId, newRole);
      
      // Update the user in local state
      setUsers(users.map(user => 
        user.user_id === userId ? { ...user, role: newRole } : user
      ));
      
    } catch (err) {
      setError('Failed to update user role');
      console.error('Error updating role:', err);
    } finally {
      setUpdatingRole(null);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const clearFilters = () => {
    setFilters({ name: '', email: '', phone: '' });
  };

  useEffect(() => {
    fetchUsers();
  }, [filters]);

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Manage users and system settings</p>
      </div>

      <div className="dashboard-content">
        {/* Filters Section */}
        <div className="filters-section">
          <h3>Filter Users</h3>
          <div className="filters-grid">
            <div className="filter-group">
              <label htmlFor="name-filter">Name:</label>
              <input
                id="name-filter"
                type="text"
                value={filters.name}
                onChange={(e) => handleFilterChange('name', e.target.value)}
                placeholder="Search by name..."
              />
            </div>
            <div className="filter-group">
              <label htmlFor="email-filter">Email:</label>
              <input
                id="email-filter"
                type="text"
                value={filters.email}
                onChange={(e) => handleFilterChange('email', e.target.value)}
                placeholder="Search by email..."
              />
            </div>
            <div className="filter-group">
              <label htmlFor="phone-filter">Phone:</label>
              <input
                id="phone-filter"
                type="text"
                value={filters.phone}
                onChange={(e) => handleFilterChange('phone', e.target.value)}
                placeholder="Search by phone..."
              />
            </div>
            <div className="filter-actions">
              <button onClick={clearFilters} className="clear-filters-btn">
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="users-section">
          <h3>Users ({users.length})</h3>
          
          {error && <div className="error-message">{error}</div>}
          
          {loading ? (
            <div className="loading">Loading users...</div>
          ) : (
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Company</th>
                    <th>Phone</th>
                    <th>Role</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((userData) => (
                    <tr key={userData.user_id}>
                      <td>{userData.name || 'N/A'}</td>
                      <td>{userData.email}</td>
                      <td>{userData.company || 'N/A'}</td>
                      <td>{userData.phone || 'N/A'}</td>
                      <td>
                        <span className={`role-badge ${userData.role}`}>
                          {userData.role}
                        </span>
                      </td>
                      <td>
                        <div className="user-actions">
                          {userData.role === 'user' ? (
                            <button
                              onClick={() => handleRoleUpdate(userData.user_id, 'admin')}
                              disabled={updatingRole === userData.user_id}
                              className="make-admin-btn"
                            >
                              {updatingRole === userData.user_id ? 'Updating...' : 'Make Admin'}
                            </button>
                          ) : (
                            <button
                              onClick={() => handleRoleUpdate(userData.user_id, 'user')}
                              disabled={updatingRole === userData.user_id}
                              className="remove-admin-btn"
                            >
                              {updatingRole === userData.user_id ? 'Updating...' : 'Remove Admin'}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {users.length === 0 && !loading && (
                <div className="no-users">
                  No users found matching your filters.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
