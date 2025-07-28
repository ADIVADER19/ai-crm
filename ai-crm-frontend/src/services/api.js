import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  firebaseAuth: async (idToken, userType = 'user') => {
    const response = await api.post('/auth/firebase-auth', { 
      id_token: idToken, 
      user_type: userType 
    });
    return response.data;
  },
  
  firebaseLogin: async (idToken, userType = 'user') => {
    const response = await api.post('/auth/firebase-login', { 
      id_token: idToken, 
      user_type: userType 
    });
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  verify: async () => {
    const response = await api.post('/auth/verify');
    return response.data;
  }
};

export const crmAPI = {
  createUser: async (userData) => {
    const response = await api.post('/crm/create_user', userData);
    return response.data;
  },
  
  updateUser: async (userId, userData) => {
    const response = await api.put(`/crm/update_user/${userId}`, userData);
    return response.data;
  },
  
  getUser: async (userId) => {
    const response = await api.get(`/crm/user/${userId}`);
    return response.data;
  },
  
  getConversations: async (userId) => {
    const response = await api.get(`/crm/conversations/${userId}`);
    return response.data;
  },

  // Admin endpoints
  getAllUsers: async (queryParams = '') => {
    const url = queryParams ? `/crm/admin/users?${queryParams}` : '/crm/admin/users';
    const response = await api.get(url);
    return response.data;
  },
  
  updateUserRole: async (userId, role) => {
    const response = await api.put(`/crm/admin/users/${userId}/role?role=${role}`);
    return response.data;
  },
  
  getUserById: async (userId) => {
    const response = await api.get(`/crm/admin/users/${userId}`);
    return response.data;
  }
};

export const chatAPI = {
  sendMessage: async (message) => {
    const response = await api.post('/chat/', { message });
    return response.data;
  },
  
  getCategories: async () => {
    const response = await api.get('/chat/categories');
    return response.data;
  }
};

export const uploadAPI = {
  uploadDocs: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload_docs/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};

export const resetAPI = {
  reset: async () => {
    const response = await api.put('/reset');
    return response.data;
  }
};

export default api;
