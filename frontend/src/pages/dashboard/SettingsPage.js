import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import './SettingsPage.css';

const SettingsPage = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('general');
  const [formData, setFormData] = useState({
    workspaceName: user?.workspace?.name || 'My Workspace',
    description: '',
    industry: 'technology',
    website: '',
    profileName: user?.name || '',
    email: user?.email || '',
    phone: '',
    timezone: 'UTC',
    language: 'english',
    emailNotifications: true,
    pushNotifications: false,
    marketingEmails: true
  });

  const tabs = [
    { id: 'general', label: 'General', icon: 'settings' },
    { id: 'profile', label: 'Profile', icon: 'user' },
    { id: 'notifications', label: 'Notifications', icon: 'bell' },
    { id: 'security', label: 'Security', icon: 'shield' },
    { id: 'billing', label: 'Billing', icon: 'credit-card' }
  ];

  const industries = [
    { value: 'technology', label: 'Technology' },
    { value: 'marketing', label: 'Marketing & Advertising' },
    { value: 'ecommerce', label: 'E-commerce' },
    { value: 'education', label: 'Education' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'finance', label: 'Finance' },
    { value: 'other', label: 'Other' }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSave = () => {
    console.log('Saving settings:', formData);
    // TODO: Implement save functionality
  };

  const handleLogoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('Logo uploaded:', file.name);
      // TODO: Implement logo upload
    }
  };

  return (
    <div className="settings-page">
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
        </div>
      </div>

      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">
            <span className="gradient-text">Settings</span>
          </h1>
          <p className="page-subtitle">
            Manage your workspace and account preferences
          </p>
        </div>
        <div className="header-actions">
          <button onClick={handleSave} className="btn btn-primary">
            <span>💾</span>
            Save Changes
          </button>
        </div>
      </div>

      <div className="settings-container">
        {/* Sidebar Navigation */}
        <div className="settings-sidebar">
          <div className="sidebar-content">
            <h3 className="sidebar-title">Settings</h3>
            <nav className="sidebar-nav">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                >
                  <span className="nav-icon-settings">{tab.icon}</span>
                  <span className="nav-label">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="settings-content">
          {activeTab === 'general' && (
            <div className="settings-section">
              <div className="section-header">
                <h2 className="section-title">Workspace Settings</h2>
                <p className="section-description">
                  Configure your workspace information and preferences
                </p>
              </div>

              <div className="settings-cards">
                <div className="card settings-card">
                  <div className="card-header">
                    <h3 className="card-title">Workspace Information</h3>
                  </div>
                  <div className="card-content">
                    <div className="form-grid">
                      <div className="form-group">
                        <label className="form-label">Workspace Name</label>
                        <input
                          type="text"
                          name="workspaceName"
                          value={formData.workspaceName}
                          onChange={handleInputChange}
                          className="form-input"
                          placeholder="Enter workspace name"
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Industry</label>
                        <select
                          name="industry"
                          value={formData.industry}
                          onChange={handleInputChange}
                          className="form-input"
                        >
                          {industries.map((industry) => (
                            <option key={industry.value} value={industry.value}>
                              {industry.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="form-group full-width">
                        <label className="form-label">Description</label>
                        <textarea
                          name="description"
                          value={formData.description}
                          onChange={handleInputChange}
                          className="form-input"
                          placeholder="Describe your workspace..."
                          rows="3"
                        />
                      </div>
                      <div className="form-group full-width">
                        <label className="form-label">Website</label>
                        <input
                          type="url"
                          name="website"
                          value={formData.website}
                          onChange={handleInputChange}
                          className="form-input"
                          placeholder="https://yourwebsite.com"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card settings-card">
                  <div className="card-header">
                    <h3 className="card-title">Visual Identity</h3>
                  </div>
                  <div className="card-content">
                    <div className="logo-section">
                      <div className="logo-preview">
                        <div className="logo-placeholder">
                          <span className="logo-text">
                            {formData.workspaceName.charAt(0)}
                          </span>
                        </div>
                        <div className="logo-info">
                          <h4>Workspace Logo</h4>
                          <p>Recommended: 200x200px, PNG or JPG</p>
                        </div>
                      </div>
                      <input
                        type="file"
                        id="logo-upload"
                        accept="image/*"
                        onChange={handleLogoUpload}
                        className="file-input"
                        hidden
                      />
                      <label htmlFor="logo-upload" className="btn btn-secondary">
                        Upload Logo
                      </label>
                    </div>

                    <div className="theme-section">
                      <h4 className="theme-title">Theme Preference</h4>
                      <div className="theme-options">
                        <button
                          onClick={toggleTheme}
                          className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
                        >
                          <span className="theme-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                            </svg>
                          </span>
                          <span className="theme-name">Dark</span>
                        </button>
                        <button
                          onClick={toggleTheme}
                          className={`theme-option ${theme === 'light' ? 'active' : ''}`}
                        >
                          <span className="theme-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <circle cx="12" cy="12" r="5"/>
                              <line x1="12" y1="1" x2="12" y2="3"/>
                              <line x1="12" y1="21" x2="12" y2="23"/>
                              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                              <line x1="1" y1="12" x2="3" y2="12"/>
                              <line x1="21" y1="12" x2="23" y2="12"/>
                              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                            </svg>
                          </span>
                          <span className="theme-name">Light</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="settings-section">
              <div className="section-header">
                <h2 className="section-title">Profile Settings</h2>
                <p className="section-description">
                  Manage your personal account information
                </p>
              </div>

              <div className="card settings-card">
                <div className="card-content">
                  <div className="form-grid">
                    <div className="form-group">
                      <label className="form-label">Full Name</label>
                      <input
                        type="text"
                        name="profileName"
                        value={formData.profileName}
                        onChange={handleInputChange}
                        className="form-input"
                        placeholder="Enter your full name"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Email Address</label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="form-input"
                        placeholder="Enter your email"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Phone Number</label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="form-input"
                        placeholder="Enter your phone number"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Timezone</label>
                      <select
                        name="timezone"
                        value={formData.timezone}
                        onChange={handleInputChange}
                        className="form-input"
                      >
                        <option value="UTC">UTC (Coordinated Universal Time)</option>
                        <option value="EST">EST (Eastern Standard Time)</option>
                        <option value="PST">PST (Pacific Standard Time)</option>
                        <option value="GMT">GMT (Greenwich Mean Time)</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Language</label>
                      <select
                        name="language"
                        value={formData.language}
                        onChange={handleInputChange}
                        className="form-input"
                      >
                        <option value="english">English</option>
                        <option value="spanish">Spanish</option>
                        <option value="french">French</option>
                        <option value="german">German</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="settings-section">
              <div className="section-header">
                <h2 className="section-title">Notification Preferences</h2>
                <p className="section-description">
                  Control how and when you receive notifications
                </p>
              </div>

              <div className="card settings-card">
                <div className="card-content">
                  <div className="notification-options">
                    <div className="notification-group">
                      <h4>Email Notifications</h4>
                      <div className="toggle-option">
                        <label className="toggle-label">
                          <input
                            type="checkbox"
                            name="emailNotifications"
                            checked={formData.emailNotifications}
                            onChange={handleInputChange}
                            className="toggle-input"
                          />
                          <span className="toggle-slider"></span>
                          <span className="toggle-text">General email notifications</span>
                        </label>
                      </div>
                      <div className="toggle-option">
                        <label className="toggle-label">
                          <input
                            type="checkbox"
                            name="marketingEmails"
                            checked={formData.marketingEmails}
                            onChange={handleInputChange}
                            className="toggle-input"
                          />
                          <span className="toggle-slider"></span>
                          <span className="toggle-text">Marketing and promotional emails</span>
                        </label>
                      </div>
                    </div>

                    <div className="notification-group">
                      <h4>Push Notifications</h4>
                      <div className="toggle-option">
                        <label className="toggle-label">
                          <input
                            type="checkbox"
                            name="pushNotifications"
                            checked={formData.pushNotifications}
                            onChange={handleInputChange}
                            className="toggle-input"
                          />
                          <span className="toggle-slider"></span>
                          <span className="toggle-text">Browser push notifications</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="settings-section">
              <div className="section-header">
                <h2 className="section-title">Security Settings</h2>
                <p className="section-description">
                  Manage your account security and privacy
                </p>
              </div>

              <div className="card settings-card">
                <div className="card-content">
                  <div className="security-options">
                    <div className="security-item">
                      <div className="security-info">
                        <h4>Change Password</h4>
                        <p>Update your account password</p>
                      </div>
                      <button className="btn btn-secondary">Change Password</button>
                    </div>
                    
                    <div className="security-item">
                      <div className="security-info">
                        <h4>Two-Factor Authentication</h4>
                        <p>Add an extra layer of security to your account</p>
                      </div>
                      <button className="btn btn-primary">Enable 2FA</button>
                    </div>
                    
                    <div className="security-item">
                      <div className="security-info">
                        <h4>Active Sessions</h4>
                        <p>Manage your active login sessions</p>
                      </div>
                      <button className="btn btn-secondary">View Sessions</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'billing' && (
            <div className="settings-section">
              <div className="section-header">
                <h2 className="section-title">Billing & Subscription</h2>
                <p className="section-description">
                  Manage your billing information and subscription
                </p>
              </div>

              <div className="card settings-card">
                <div className="card-content">
                  <div className="billing-placeholder">
                    <span className="billing-icon">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
                        <line x1="1" y1="10" x2="23" y2="10"/>
                      </svg>
                    </span>
                    <h3>Billing Management</h3>
                    <p>View and manage your subscription, payment methods, and billing history</p>
                    <button className="btn btn-primary">Manage Billing</button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;