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
      const mobile = window.innerWidth < 768;
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
        { label: 'Overview', icon: '🏠', route: '/dashboard', badge: null },
        { label: 'Social Media', icon: '📱', route: '/dashboard/social-media', badge: '3' },
        { label: 'E-commerce', icon: '🛍️', route: '/dashboard/ecommerce', badge: null },
        { label: 'Content & Courses', icon: '🎓', route: '/dashboard/courses', badge: null },
        { label: 'CRM & Contacts', icon: '👥', route: '/dashboard/crm', badge: '12' },
        { label: 'Analytics', icon: '📊', route: '/dashboard/analytics', badge: null },
      ]
    },
    {
      section: 'tools',
      title: 'Tools & Features',
      items: [
        { label: 'Website Builder', icon: '🌐', route: '/dashboard/website-builder' },
        { label: 'Bio Links', icon: '🔗', route: '/dashboard/bio-sites' },
        { label: 'Email Marketing', icon: '📧', route: '/dashboard/email-marketing' },
        { label: 'Booking System', icon: '📅', route: '/dashboard/advanced-booking' },
        { label: 'Financial', icon: '💳', route: '/dashboard/financial-management' },
        { label: 'AI Features', icon: '🤖', route: '/dashboard/ai-features' },
      ]
    },
    {
      section: 'workspace',
      title: 'Workspace',
      items: [
        { label: 'Settings', icon: '⚙️', route: '/dashboard/settings' },
        { label: 'Team', icon: '👨‍👩‍👧‍👦', route: '/dashboard/team-management' },
        { label: 'Subscription', icon: '💎', route: '/dashboard/subscription' },
      ]
    }
  ];

  const adminItems = [
    { label: 'Admin Dashboard', icon: '👑', route: '/dashboard/admin' },
    { label: 'Plan Management', icon: '📋', route: '/dashboard/admin/plans' },
    { label: 'User Management', icon: '👤', route: '/dashboard/admin/users' },
    { label: 'System Settings', icon: '🔧', route: '/dashboard/admin/system' },
  ];

  const quickActions = [
    { label: 'Create Post', icon: '📝', action: 'create_post' },
    { label: 'Add Contact', icon: '👤', action: 'add_contact' },
    { label: 'New Campaign', icon: '📢', action: 'new_campaign' },
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
                      <span className="nav-icon">{item.icon}</span>
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
                      <span className="nav-icon">{item.icon}</span>
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
              <span className="search-icon">🔍</span>
            </div>
          </div>

          <div className="header-right">
            <button className="header-btn">
              <span className="notification-icon">🔔</span>
              <span className="notification-badge">3</span>
            </button>
            
            <button onClick={toggleTheme} className="header-btn theme-toggle">
              <span>{theme === 'dark' ? '🌙' : '☀️'}</span>
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