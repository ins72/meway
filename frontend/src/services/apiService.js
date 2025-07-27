
// API Service for Real Data Integration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

class ApiService {
  static async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Workspace APIs
  static async getWorkspaces(limit = 50, offset = 0) {
    return this.request(`/api/workspace?limit=${limit}&offset=${offset}`);
  }

  static async getWorkspace(id) {
    return this.request(`/api/workspace/${id}`);
  }

  static async createWorkspace(data) {
    return this.request('/api/workspace', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateWorkspace(id, data) {
    return this.request(`/api/workspace/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteWorkspace(id) {
    return this.request(`/api/workspace/${id}`, {
      method: 'DELETE',
    });
  }

  // User APIs
  static async getUsers(limit = 50, offset = 0) {
    return this.request(`/api/user?limit=${limit}&offset=${offset}`);
  }

  static async getUser(id) {
    return this.request(`/api/user/${id}`);
  }

  static async createUser(data) {
    return this.request('/api/user', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateUser(id, data) {
    return this.request(`/api/user/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteUser(id) {
    return this.request(`/api/user/${id}`, {
      method: 'DELETE',
    });
  }

  // Blog APIs
  static async getBlogPosts(limit = 50, offset = 0) {
    return this.request(`/api/blog?limit=${limit}&offset=${offset}`);
  }

  static async getBlogPost(id) {
    return this.request(`/api/blog/${id}`);
  }

  static async createBlogPost(data) {
    return this.request('/api/blog', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateBlogPost(id, data) {
    return this.request(`/api/blog/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteBlogPost(id) {
    return this.request(`/api/blog/${id}`, {
      method: 'DELETE',
    });
  }

  // Dashboard APIs
  static async getDashboardStats() {
    return this.request('/api/dashboard/stats');
  }

  static async getAnalytics() {
    return this.request('/api/analytics');
  }

  // CRM APIs
  static async getContacts() {
    return this.request('/api/crm/contacts');
  }

  static async getDeals() {
    return this.request('/api/crm/deals');
  }

  // Booking APIs
  static async getBookings() {
    return this.request('/api/booking');
  }

  // Email Marketing APIs
  static async getCampaigns() {
    return this.request('/api/email-marketing/campaigns');
  }

  // Financial APIs
  static async getFinancialData() {
    return this.request('/api/financial');
  }

  // Subscription APIs
  static async getSubscriptions() {
    return this.request('/api/workspace-subscription');
  }

  // Admin APIs
  static async getAdminStats() {
    return this.request('/api/admin/stats');
  }

  static async getSystemHealth() {
    return this.request('/api/admin/health');
  }
}

export default ApiService;
