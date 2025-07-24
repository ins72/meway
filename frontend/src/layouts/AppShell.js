import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import LoadingSpinner from '../components/LoadingSpinner';
import './AppShell.css';

const AppShell = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navigationItems = [
    {
      section: 'main',
      items: [
        { label: 'Overview', icon: 'overview', route: '/dashboard', badge: null },
        { label: 'Social Media', icon: 'social', route: '/dashboard/social-media', badge: '3' },
        { label: 'E-commerce', icon: 'store', route: '/dashboard/ecommerce', badge: null },
        { label: 'Content & Courses', icon: 'education', route: '/dashboard/courses', badge: null },
        { label: 'CRM & Contacts', icon: 'contacts', route: '/dashboard/crm', badge: '12' },
        { label: 'Analytics', icon: 'analytics', route: '/dashboard/analytics', badge: null },
      ]
    },
    {
      section: 'tools',
      title: 'Tools & Features',
      items: [
        { label: 'Website Builder', icon: 'website', route: '/dashboard/website-builder' },
        { label: 'Bio Links', icon: 'links', route: '/dashboard/bio-sites' },
        { label: 'Email Marketing', icon: 'email', route: '/dashboard/email-marketing' },
        { label: 'Booking System', icon: 'calendar', route: '/dashboard/advanced-booking' },
        { label: 'Financial', icon: 'finance', route: '/dashboard/financial-management' },
        { label: 'AI Features', icon: 'ai', route: '/dashboard/ai-features' },
      ]
    },
    {
      section: 'workspace',
      title: 'Workspace',
      items: [
        { label: 'Settings', icon: 'settings', route: '/dashboard/settings' },
        { label: 'Team', icon: 'team', route: '/dashboard/team-management' },
        { label: 'Subscription', icon: 'subscription', route: '/dashboard/subscription' },
      ]
    }
  ];

  const adminItems = [
    { label: 'Admin Dashboard', icon: 'admin', route: '/dashboard/admin' },
    { label: 'Plan Management', icon: 'plans', route: '/dashboard/admin/plans' },
    { label: 'User Management', icon: 'users', route: '/dashboard/admin/users' },
    { label: 'System Settings', icon: 'system', route: '/dashboard/admin/system' },
  ];

  const quickActions = [
    { label: 'Create Post', icon: 'create', action: 'create_post' },
    { label: 'Add Contact', icon: 'add-user', action: 'add_contact' },
    { label: 'New Campaign', icon: 'campaign', action: 'new_campaign' },
  ];

  const handleNavigation = (route) => {
    navigate(route);
    if (isMobile) {
      setIsSidebarOpen(false);
    }
  };

  const handleQuickAction = (action) => {
    console.log(`Quick action: ${action}`);
    // TODO: Implement quick action modals
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-app flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="app-shell" data-theme={theme}>
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {isMobile && isSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <span className="gradient-text">Mewayz</span>
          </div>
          {!isMobile && (
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="sidebar-toggle"
            >
              {isSidebarOpen ? '←' : '→'}
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((section, sectionIndex) => (
            <div key={sectionIndex} className="nav-section">
              {section.title && (
                <h3 className="nav-section-title">{section.title}</h3>
              )}
              <ul className="nav-items">
                {section.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="nav-item">
                    <button
                      onClick={() => handleNavigation(item.route)}
                      className={`nav-link ${location.pathname === item.route ? 'active' : ''}`}
                    >
                      <span className="nav-icon-professional">{item.icon}</span>
                      {isSidebarOpen && (
                        <>
                          <span className="nav-label">{item.label}</span>
                          {item.badge && (
                            <span className="nav-badge">{item.badge}</span>
                          )}
                        </>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Admin Section (if user is admin) */}
          {user?.role === 'admin' && (
            <div className="nav-section admin-section">
              <h3 className="nav-section-title">Admin</h3>
              <ul className="nav-items">
                {adminItems.map((item, itemIndex) => (
                  <li key={itemIndex} className="nav-item">
                    <button
                      onClick={() => handleNavigation(item.route)}
                      className={`nav-link ${location.pathname === item.route ? 'active' : ''}`}
                    >
                      <span className="nav-icon-professional">{item.icon}</span>
                      {isSidebarOpen && (
                        <span className="nav-label">{item.label}</span>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Quick Actions */}
          {isSidebarOpen && (
            <div className="nav-section quick-actions">
              <h3 className="nav-section-title">Quick Actions</h3>
              <div className="quick-action-buttons">
                {quickActions.map((action, actionIndex) => (
                  <button
                    key={actionIndex}
                    onClick={() => handleQuickAction(action.action)}
                    className="quick-action-btn"
                  >
                    <span className="action-icon">{action.icon}</span>
                    <span className="action-label">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            {isMobile && (
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="mobile-menu-toggle"
              >
                ☰
              </button>
            )}
            
            <div className="workspace-selector">
              <div className="workspace-avatar">
                {user?.workspace?.name?.charAt(0) || 'W'}
              </div>
              <div className="workspace-info">
                <span className="workspace-name">{user?.workspace?.name || 'Default Workspace'}</span>
                <span className="workspace-role">{user?.role || 'Member'}</span>
              </div>
            </div>
          </div>

          <div className="header-center">
            <div className="global-search">
              <input
                type="text"
                placeholder="Search features, content, people... (⌘K)"
                className="search-input"
              />
              <div className="search-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
              </div>
            </div>
          </div>

          <div className="header-right">
            <button className="header-btn">
              <span className="notification-icon">🔔</span>
              <span className="notification-badge">3</span>
            </button>
            
            <button onClick={toggleTheme} className="header-btn theme-toggle">
              <span>
                {theme === 'dark' ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
                )}
              </span>
            </button>

            <div className="user-menu">
              <button className="user-avatar">
                {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </button>
              <div className="user-dropdown">
                <div className="user-info">
                  <span className="user-name">{user?.name || 'User'}</span>
                  <span className="user-email">{user?.email}</span>
                </div>
                <hr className="dropdown-divider" />
                <button className="dropdown-item">Profile Settings</button>
                <button className="dropdown-item">Workspace Settings</button>
                <button className="dropdown-item">Help & Support</button>
                <hr className="dropdown-divider" />
                <button onClick={logout} className="dropdown-item logout">
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppShell;