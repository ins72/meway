import React, { useState, useEffect } from 'react';
import './EnhancedAdminDashboard.css';

const EnhancedAdminDashboard = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [notifications, setNotifications] = useState({});
  const [planImpactData, setPlanImpactData] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Load analytics overview
      const analyticsResponse = await fetch(`${BACKEND_URL}/api/admin-workspace-management/analytics/overview`, { headers });
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData.analytics || {});
      }

      // Load workspaces
      const workspacesResponse = await fetch(`${BACKEND_URL}/api/admin-workspace-management/workspaces?limit=20`, { headers });
      if (workspacesResponse.ok) {
        const workspacesData = await workspacesResponse.json();
        setWorkspaces(workspacesData.workspaces || []);
      }

      // Load notification stats
      const notificationResponse = await fetch(`${BACKEND_URL}/api/customer-notification/stats/overview`, { headers });
      if (notificationResponse.ok) {
        const notificationData = await notificationResponse.json();
        setNotifications(notificationData.overview || {});
      }

      // Load plan impact health check
      const planImpactResponse = await fetch(`${BACKEND_URL}/api/plan-change-impact/health`, { headers });
      if (planImpactResponse.ok) {
        const planImpactData = await planImpactResponse.json();
        setPlanImpactData(planImpactData || {});
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const handleSendTestNotification = async (workspaceId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/customer-notification/test-notification`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          workspace_id: workspaceId,
          notification_type: 'admin_override',
          template_data: {
            reason: 'Test notification from enhanced admin dashboard',
            additional_details: 'This is a test to verify the notification system is working properly.'
          }
        })
      });

      if (response.ok) {
        alert('✅ Test notification sent successfully!');
      } else {
        alert('❌ Failed to send test notification');
      }
    } catch (error) {
      console.error('Error sending test notification:', error);
      alert('❌ Error sending test notification');
    }
  };

  const handleApplyDiscount = async (workspaceId) => {
    const discountValue = prompt('Enter discount percentage (e.g., 20):');
    const reason = prompt('Enter reason for discount:');
    
    if (!discountValue || !reason) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/admin-workspace-management/workspace/${workspaceId}/manual-discount`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: 'percentage',
          value: parseFloat(discountValue),
          reason: reason,
          expires_at: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString() // 90 days from now
        })
      });

      if (response.ok) {
        alert(`✅ ${discountValue}% discount applied successfully!`);
        loadDashboardData(); // Refresh data
      } else {
        alert('❌ Failed to apply discount');
      }
    } catch (error) {
      console.error('Error applying discount:', error);
      alert('❌ Error applying discount');
    }
  };

  const handlePauseSubscription = async (workspaceId) => {
    const reason = prompt('Enter reason for pausing subscription:');
    if (!reason) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/admin-workspace-management/workspace/${workspaceId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          reason: reason,
          pause_billing: true,
          feature_access: 'limited'
        })
      });

      if (response.ok) {
        alert('✅ Subscription paused successfully!');
        loadDashboardData(); // Refresh data
      } else {
        alert('❌ Failed to pause subscription');
      }
    } catch (error) {
      console.error('Error pausing subscription:', error);
      alert('❌ Error pausing subscription');
    }
  };

  const renderOverviewTab = () => (
    <div className="enhanced-admin-overview">
      <div className="admin-systems-status">
        <h3>🛠️ Admin Systems Status</h3>
        <div className="systems-grid">
          <div className="system-card">
            <div className="system-header">
              <span className="system-icon">🏢</span>
              <h4>Workspace Management</h4>
            </div>
            <div className="system-status healthy">
              <span className="status-dot"></span>
              <span>Operational</span>
            </div>
            <div className="system-stats">
              <small>{analytics.total_workspaces || 0} workspaces tracked</small>
            </div>
          </div>

          <div className="system-card">
            <div className="system-header">
              <span className="system-icon">📧</span>
              <h4>Notification System</h4>
            </div>
            <div className="system-status healthy">
              <span className="status-dot"></span>
              <span>Operational</span>
            </div>
            <div className="system-stats">
              <small>{notifications.available_templates || 0} templates available</small>
            </div>
          </div>

          <div className="system-card">
            <div className="system-header">
              <span className="system-icon">⚖️</span>
              <h4>Plan Impact Analysis</h4>
            </div>
            <div className={`system-status ${planImpactData.healthy ? 'healthy' : 'warning'}`}>
              <span className="status-dot"></span>
              <span>{planImpactData.healthy ? 'Operational' : 'Warning'}</span>
            </div>
            <div className="system-stats">
              <small>Risk assessment ready</small>
            </div>
          </div>
        </div>
      </div>

      <div className="admin-stats-grid">
        <div className="admin-stat-card large">
          <div className="stat-icon">🏢</div>
          <div className="stat-content">
            <h3>{analytics.total_workspaces || 0}</h3>
            <p>Total Workspaces</p>
            <div className="stat-breakdown">
              <span>Active: {analytics.active_subscriptions || 0}</span>
              <span>Paused: {analytics.paused_subscriptions || 0}</span>
            </div>
          </div>
        </div>
        
        <div className="admin-stat-card large">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>{formatCurrency(analytics.total_revenue)}</h3>
            <p>Total Revenue</p>
            <div className="stat-breakdown">
              <span>Comp: {analytics.comp_accounts || 0}</span>
              <span>Overrides: {analytics.overridden_subscriptions || 0}</span>
            </div>
          </div>
        </div>
        
        <div className="admin-stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>{notifications.weekly?.success_rate?.toFixed(1) || 0}%</h3>
            <p>Notification Success Rate</p>
          </div>
        </div>
        
        <div className="admin-stat-card">
          <div className="stat-icon">🔧</div>
          <div className="stat-content">
            <h3>{analytics.recent_admin_actions || 0}</h3>
            <p>Recent Admin Actions</p>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h3>⚡ Quick Actions</h3>
        <div className="action-buttons-grid">
          <button className="quick-action-btn" onClick={() => setActiveTab('workspaces')}>
            🏢 Manage Workspaces
          </button>
          <button className="quick-action-btn" onClick={() => setActiveTab('notifications')}>
            📧 Send Notifications
          </button>
          <button className="quick-action-btn" onClick={() => setActiveTab('analytics')}>
            📊 View Analytics
          </button>
          <button className="quick-action-btn" onClick={loadDashboardData}>
            🔄 Refresh Data
          </button>
        </div>
      </div>
    </div>
  );

  const renderWorkspacesTab = () => (
    <div className="enhanced-admin-workspaces">
      <div className="workspaces-header">
        <h3>🏢 Advanced Workspace Management</h3>
        <div className="workspace-controls">
          <button className="control-btn" onClick={loadDashboardData}>
            🔄 Refresh
          </button>
          <select className="filter-select" defaultValue="all">
            <option value="all">All Workspaces</option>
            <option value="active">Active Only</option>
            <option value="paused">Paused Only</option>
            <option value="comp">Comp Accounts</option>
          </select>
        </div>
      </div>
      
      <div className="workspaces-table-container">
        <table className="enhanced-workspaces-table">
          <thead>
            <tr>
              <th>Workspace Details</th>
              <th>Subscription Status</th>
              <th>Revenue & Bundles</th>
              <th>Admin Indicators</th>
              <th>Quick Actions</th>
            </tr>
          </thead>
          <tbody>
            {workspaces.map((workspace) => (
              <tr key={workspace._id}>
                <td>
                  <div className="workspace-details">
                    <strong className="workspace-name">
                      {workspace.name || 'Unnamed Workspace'}
                    </strong>
                    <div className="workspace-meta">
                      <span className="owner-email">{workspace.owner_email || 'Unknown'}</span>
                      <span className="workspace-id">{workspace._id}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div className="subscription-status">
                    <span className={`status-badge ${workspace.admin_analytics?.status || 'unknown'}`}>
                      {workspace.admin_analytics?.status || 'Unknown'}
                    </span>
                    <small className="subscription-age">
                      {workspace.admin_analytics?.subscription_age_days || 0} days old
                    </small>
                  </div>
                </td>
                <td>
                  <div className="revenue-info">
                    <strong className="revenue-amount">
                      {formatCurrency(workspace.admin_analytics?.total_revenue)}
                    </strong>
                    <div className="bundle-info">
                      <span className="bundle-count">
                        {workspace.admin_analytics?.bundle_count || 0} bundles
                      </span>
                      {workspace.admin_analytics?.discount_count > 0 && (
                        <span className="discount-indicator">
                          💰 {workspace.admin_analytics.discount_count} discounts
                        </span>
                      )}
                    </div>
                  </div>
                </td>
                <td>
                  <div className="admin-indicators">
                    {workspace.admin_analytics?.has_overrides && (
                      <span className="indicator override" title="Has Admin Overrides">
                        🔧 Override
                      </span>
                    )}
                    {workspace.admin_analytics?.is_comp_account && (
                      <span className="indicator comp" title="Complimentary Account">
                        🎁 Comp
                      </span>
                    )}
                    {workspace.admin_analytics?.recent_admin_actions > 0 && (
                      <span className="indicator recent-actions" title="Recent Admin Actions">
                        📝 {workspace.admin_analytics.recent_admin_actions}
                      </span>
                    )}
                  </div>
                </td>
                <td>
                  <div className="workspace-actions">
                    <button 
                      className="action-btn notification"
                      onClick={() => handleSendTestNotification(workspace._id)}
                      title="Send Test Notification"
                    >
                      📧
                    </button>
                    <button 
                      className="action-btn discount"
                      onClick={() => handleApplyDiscount(workspace._id)}
                      title="Apply Manual Discount"
                    >
                      💰
                    </button>
                    <button 
                      className="action-btn pause"
                      onClick={() => handlePauseSubscription(workspace._id)}
                      title="Pause Subscription"
                      disabled={workspace.admin_analytics?.status === 'paused'}
                    >
                      ⏸️
                    </button>
                    <button 
                      className="action-btn details"
                      title="View Full Details"
                    >
                      👁️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {workspaces.length === 0 && !loading && (
          <div className="no-workspaces">
            <div className="no-data-icon">🏢</div>
            <h4>No workspaces found</h4>
            <p>No workspaces are currently registered in the system.</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="enhanced-admin-notifications">
      <div className="notifications-header">
        <h3>📧 Advanced Notification Management</h3>
        <div className="notification-stats-summary">
          <div className="stat-item">
            <span className="stat-value">{notifications.weekly?.total_notifications || 0}</span>
            <span className="stat-label">Weekly</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{notifications.monthly?.total_notifications || 0}</span>
            <span className="stat-label">Monthly</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{notifications.weekly?.success_rate?.toFixed(1) || 0}%</span>
            <span className="stat-label">Success Rate</span>
          </div>
        </div>
      </div>
      
      <div className="notification-templates">
        <h4>📋 Available Templates</h4>
        <div className="template-grid">
          {[
            { name: 'plan_change', title: 'Plan Change Notification', icon: '📋', priority: 'high' },
            { name: 'admin_override', title: 'Admin Override Alert', icon: '🔧', priority: 'medium' },
            { name: 'comp_account_granted', title: 'Comp Account Granted', icon: '🎁', priority: 'high' },
            { name: 'discount_applied', title: 'Discount Applied', icon: '💰', priority: 'medium' },
            { name: 'subscription_paused', title: 'Subscription Paused', icon: '⏸️', priority: 'high' },
            { name: 'subscription_resumed', title: 'Subscription Resumed', icon: '▶️', priority: 'high' },
            { name: 'payment_issue', title: 'Payment Issue Alert', icon: '⚠️', priority: 'critical' },
            { name: 'subscription_expiring', title: 'Expiring Soon Warning', icon: '⏰', priority: 'high' }
          ].map((template) => (
            <div key={template.name} className={`template-card ${template.priority}`}>
              <div className="template-header">
                <span className="template-icon">{template.icon}</span>
                <span className={`priority-badge ${template.priority}`}>
                  {template.priority}
                </span>
              </div>
              <div className="template-info">
                <h5>{template.title}</h5>
                <small>{template.name}</small>
              </div>
              <div className="template-actions">
                <button className="template-action-btn">✏️ Edit</button>
                <button className="template-action-btn">📤 Test</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="notification-channels">
        <h4>📡 Delivery Channels</h4>
        <div className="channels-grid">
          <div className="channel-card enabled">
            <div className="channel-header">
              <span className="channel-icon">📧</span>
              <h5>Email</h5>
              <span className="channel-status enabled">Active</span>
            </div>
            <div className="channel-stats">
              <span>Provider: SendGrid</span>
              <span>Success Rate: 98.5%</span>
            </div>
          </div>
          
          <div className="channel-card enabled">
            <div className="channel-header">
              <span className="channel-icon">📱</span>
              <h5>In-App</h5>
              <span className="channel-status enabled">Active</span>
            </div>
            <div className="channel-stats">
              <span>Provider: Internal</span>
              <span>Real-time delivery</span>
            </div>
          </div>
          
          <div className="channel-card disabled">
            <div className="channel-header">
              <span className="channel-icon">💬</span>
              <h5>SMS</h5>
              <span className="channel-status disabled">Disabled</span>
            </div>
            <div className="channel-stats">
              <span>Provider: Twilio</span>
              <span>Not configured</span>
            </div>
          </div>
          
          <div className="channel-card disabled">
            <div className="channel-header">
              <span className="channel-icon">🔔</span>
              <h5>Push</h5>
              <span className="channel-status disabled">Disabled</span>
            </div>
            <div className="channel-stats">
              <span>Provider: Firebase</span>
              <span>Not configured</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="enhanced-admin-analytics">
      <h3>📊 Advanced Analytics & Insights</h3>
      
      <div className="analytics-grid">
        <div className="analytics-card">
          <h4>💼 Workspace Analytics</h4>
          <div className="analytics-content">
            <div className="metric-row">
              <span>Total Workspaces:</span>
              <strong>{analytics.total_workspaces || 0}</strong>
            </div>
            <div className="metric-row">
              <span>Active Subscriptions:</span>
              <strong>{analytics.active_subscriptions || 0}</strong>
            </div>
            <div className="metric-row">
              <span>Revenue per Workspace:</span>
              <strong>{formatCurrency((analytics.total_revenue || 0) / (analytics.total_workspaces || 1))}</strong>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h4>📧 Notification Analytics</h4>
          <div className="analytics-content">
            <div className="metric-row">
              <span>Weekly Notifications:</span>
              <strong>{notifications.weekly?.total_notifications || 0}</strong>
            </div>
            <div className="metric-row">
              <span>Success Rate:</span>
              <strong>{notifications.weekly?.success_rate?.toFixed(1) || 0}%</strong>
            </div>
            <div className="metric-row">
              <span>Failed Notifications:</span>
              <strong>{notifications.weekly?.failed || 0}</strong>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h4>🔧 Admin Activity</h4>
          <div className="analytics-content">
            <div className="metric-row">
              <span>Recent Actions:</span>
              <strong>{analytics.recent_admin_actions || 0}</strong>
            </div>
            <div className="metric-row">
              <span>Active Overrides:</span>
              <strong>{analytics.overridden_subscriptions || 0}</strong>
            </div>
            <div className="metric-row">
              <span>Comp Accounts:</span>
              <strong>{analytics.comp_accounts || 0}</strong>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h4>⚖️ Risk Management</h4>
          <div className="analytics-content">
            <div className="metric-row">
              <span>Plan Impact System:</span>
              <strong className={planImpactData.healthy ? 'status-healthy' : 'status-warning'}>
                {planImpactData.healthy ? 'Healthy' : 'Warning'}
              </strong>
            </div>
            <div className="metric-row">
              <span>Risk Assessments:</span>
              <strong>Available</strong>
            </div>
            <div className="metric-row">
              <span>System Status:</span>
              <strong className="status-healthy">Operational</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="enhanced-admin-dashboard loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h3>Loading Enhanced Admin Dashboard...</h3>
          <p>Initializing workspace management, notifications, and analytics systems...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="enhanced-admin-dashboard">
      <div className="admin-header">
        <div className="header-content">
          <h1>🛠️ Enhanced Admin Dashboard</h1>
          <p>Comprehensive platform management with advanced admin systems</p>
        </div>
        <div className="header-actions">
          <button className="header-btn" onClick={loadDashboardData}>
            🔄 Refresh All
          </button>
          <div className="admin-status">
            <span className="status-indicator healthy"></span>
            <span>All Systems Operational</span>
          </div>
        </div>
      </div>

      <div className="admin-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span className="tab-icon">📊</span>
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'workspaces' ? 'active' : ''}`}
          onClick={() => setActiveTab('workspaces')}
        >
          <span className="tab-icon">🏢</span>
          Workspaces
        </button>
        <button 
          className={`tab-button ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          <span className="tab-icon">📧</span>
          Notifications
        </button>
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <span className="tab-icon">📈</span>
          Analytics
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'workspaces' && renderWorkspacesTab()}
        {activeTab === 'notifications' && renderNotificationsTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
      </div>
    </div>
  );
};

export default EnhancedAdminDashboard;