import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export { AuthContext };

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
  const [token, setToken] = useState(() => {
    // Initialize token from localStorage with fallback
    const storedToken = localStorage.getItem('auth_token');
  console.log('AuthContext: Initial token from localStorage:', storedToken ? 'present' : 'missing');
    return storedToken;
  });
  const [currentWorkspace, setCurrentWorkspace] = useState(null);

  useEffect(() => {
    console.log('AuthContext: useEffect triggered, token:', token);
    
    // Add timeout to prevent infinite loading 
    const timeout = setTimeout(() => {
      console.log('AuthContext: Timeout reached, setting loading to false');
      setLoading(false);
    }, 10000); // Increased timeout to 10 seconds

    if (token && token !== 'null' && token !== 'undefined') {
      console.log('AuthContext: Valid token exists, fetching user');
      fetchUser().finally(() => {
        clearTimeout(timeout);
      });
    } else {
      console.log('AuthContext: No valid token, setting loading to false');
      setLoading(false);
      clearTimeout(timeout);
    }

    return () => clearTimeout(timeout);
  }, []);

  const fetchUser = async () => {
    console.log('AuthContext: fetchUser called');
    try {
      // Check if token exists in localStorage again (in case it was set after initial load)
      const currentToken = localStorage.getItem('auth_token');
      if (!currentToken || currentToken === 'null' || currentToken === 'undefined') {
        console.log('AuthContext: No valid token in localStorage during fetchUser');
        setToken(null);
        setUser(null);
        setLoading(false);
        return;
      }

      console.log('AuthContext: Making API call to getProfile with token:', currentToken.substring(0, 20) + '...');
      const response = await authAPI.getProfile();
      console.log('AuthContext: API call successful', response.data);
      setUser(response.data.user);
      setToken(currentToken); // Ensure token state is in sync
    } catch (error) {
      console.error('AuthContext: Failed to fetch user:', error);
      // Clear invalid token and reset state
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      console.log('AuthContext: Setting loading to false');
      setLoading(false);  
    }
  };

  const login = async (credentials) => {
    try {
      console.log('AuthContext: Attempting login with:', credentials.email);
      const response = await authAPI.login(credentials);
      console.log('AuthContext: Login response:', response);
      
      const { access_token: newToken, user: userData } = response.data;
      
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('auth_token', newToken);
      
      console.log('AuthContext: Login successful, user set:', userData);
      toast.success('Welcome back!');
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login failed:', error);
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      return { success: false, message };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { access_token: newToken, user: newUser } = response.data;
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('auth_token', newToken);
      
      toast.success('Account created successfully!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.message || 'Registration failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    token,
    currentWorkspace,
    setCurrentWorkspace,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};