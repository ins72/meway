import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};

// Onboarding API endpoints
export const onboardingAPI = {
  completeOnboarding: (data) => api.post('/complete-onboarding', data),
  createWorkspace: (data) => api.post('/workspace', data),
  getBundles: () => api.get('/workspace-subscription/bundles/available'),
  calculatePricing: (params) => api.get('/workspace-subscription/pricing/calculate', { params }),
};

// Google OAuth API endpoints  
export const googleAuthAPI = {
  verifyToken: (tokenData) => api.post('/google-oauth/google/verify', tokenData),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: () => api.get('/dashboard/activity'),
};

export const socialMediaAPI = {
  getAccounts: () => api.get('/social-media/accounts'),
  connectAccount: (platform, data) => api.post(`/social-media/accounts/${platform}`, data),
  getPosts: () => api.get('/social-media/posts'),
  createPost: (data) => api.post('/social-media/posts', data),
  getAnalytics: () => api.get('/social-media/analytics'),
};

export const ecommerceAPI = {
  getProducts: (params) => api.get('/ecommerce/products', { params }),
  createProduct: (data) => api.post('/ecommerce/products', data),
  updateProduct: (id, data) => api.put(`/ecommerce/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/ecommerce/products/${id}`),
  getOrders: (params) => api.get('/ecommerce/orders', { params }),
  updateOrder: (id, data) => api.put(`/ecommerce/orders/${id}`, data),
};

export const coursesAPI = {
  getCourses: () => api.get('/courses'),
  createCourse: (data) => api.post('/courses', data),
  updateCourse: (id, data) => api.put(`/courses/${id}`, data),
  deleteCourse: (id) => api.delete(`/courses/${id}`),
  getEnrollments: (courseId) => api.get(`/courses/${courseId}/enrollments`),
};

export const crmAPI = {
  getContacts: (params) => api.get('/crm/contacts', { params }),
  createContact: (data) => api.post('/crm/contacts', data),
  updateContact: (id, data) => api.put(`/crm/contacts/${id}`, data),
  deleteContact: (id) => api.delete(`/crm/contacts/${id}`),
  getLeads: (params) => api.get('/crm/leads', { params }),
  createLead: (data) => api.post('/crm/leads', data),
};

export const analyticsAPI = {
  getOverview: () => api.get('/analytics/overview'),
  getReports: (type, params) => api.get(`/analytics/reports/${type}`, { params }),
  getSocialMediaAnalytics: () => api.get('/analytics/social-media'),
  getBusinessIntelligence: () => api.get('/analytics/business-intelligence'),
  getRealtimeMetrics: () => api.get('/analytics/realtime-metrics'),
};

export const bioSitesAPI = {
  getBioSites: () => api.get('/bio-sites'),
  createBioSite: (data) => api.post('/bio-sites', data),
  updateBioSite: (id, data) => api.put(`/bio-sites/${id}`, data),
  deleteBioSite: (id) => api.delete(`/bio-sites/${id}`),
  getThemes: () => api.get('/bio-sites/themes'),
  getAnalytics: (id) => api.get(`/bio-sites/${id}/analytics`),
};

export const emailMarketingAPI = {
  getCampaigns: () => api.get('/email-marketing/campaigns'),
  createCampaign: (data) => api.post('/email-marketing/campaigns', data),
  updateCampaign: (id, data) => api.put(`/email-marketing/campaigns/${id}`, data),
  deleteCampaign: (id) => api.delete(`/email-marketing/campaigns/${id}`),
  getTemplates: () => api.get('/email-marketing/templates'),
  getSubscribers: () => api.get('/email-marketing/subscribers'),
};

export const bookingAPI = {
  getServices: () => api.get('/booking/services'),
  createService: (data) => api.post('/booking/services', data),
  updateService: (id, data) => api.put(`/booking/services/${id}`, data),
  deleteService: (id) => api.delete(`/booking/services/${id}`),
  getAppointments: () => api.get('/booking/appointments'),
  createAppointment: (data) => api.post('/booking/appointments', data),
  getAnalytics: () => api.get('/booking/analytics'),
};

export const paymentsAPI = {
  getPackages: () => api.get('/payments/packages'),
  getTransactions: () => api.get('/payments/transactions'),
  createPaymentIntent: (data) => api.post('/payments/create-intent', data),
  getPaymentMethods: () => api.get('/payments/methods'),
};

export const websiteBuilderAPI = {
  getWebsites: () => api.get('/websites'),
  createWebsite: (data) => api.post('/websites', data),
  updateWebsite: (id, data) => api.put(`/websites/${id}`, data),
  deleteWebsite: (id) => api.delete(`/websites/${id}`),
  getTemplates: () => api.get('/websites/templates'),
  getComponents: () => api.get('/websites/components'),
};

export const aiAPI = {
  getServices: () => api.get('/ai/services'),
  generateContent: (data) => api.post('/ai/content/generate', data),
  optimizeSEO: (data) => api.post('/ai/seo/optimize', data),
  analyzeCompetitor: (data) => api.post('/ai/competitor/analyze', data),
  analyzeSentiment: (data) => api.post('/ai/sentiment/analyze', data),
  scoreLeads: (data) => api.post('/ai/leads/score', data),
};

export const teamAPI = {
  getMembers: () => api.get('/team'),
  inviteMember: (data) => api.post('/team/invite', data),
  updateMember: (id, data) => api.put(`/team/${id}`, data),
  removeMember: (id) => api.delete(`/team/${id}`),
  getRoles: () => api.get('/team/roles'),
};

export const workspaceAPI = {
  getWorkspaces: () => api.get('/workspaces'),
  createWorkspace: (data) => api.post('/workspaces', data),
  updateWorkspace: (id, data) => api.put(`/workspaces/${id}`, data),
  deleteWorkspace: (id) => api.delete(`/workspaces/${id}`),
  getCurrentStep: () => api.get('/workspace-setup/current-step'),
  updateSetupStep: (data) => api.post('/workspace-setup/update', data),
};

export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: (params) => api.get('/admin/users', { params }),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  getSystemSettings: () => api.get('/admin/settings'),
  updateSystemSettings: (data) => api.put('/admin/settings', data),
  getSubscriptionPlans: () => api.get('/admin/subscription-plans'),
  updateSubscriptionPlan: (id, data) => api.put(`/admin/subscription-plans/${id}`, data),
};

export const healthAPI = {
  checkHealth: () => api.get('/health'),
};

export default api;