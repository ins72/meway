import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './DashboardHome.css';

const DashboardHome = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    revenue: { value: '$12,450', change: '+18.3%', period: 'vs last month' },
    contacts: { value: '247', change: '+25.1%', period: 'this week' },
    performance: { value: '94.2%', change: '+5.7%', period: 'open rate' },
    views: { value: '8,945', change: '+12.4%', period: 'this month' }
  });

  const [recentActivity] = useState([
    { type: 'sale', title: 'New order received', time: '2 minutes ago', icon: '🛍️' },
    { type: 'contact', title: '3 new contacts added', time: '1 hour ago', icon: '👤' },
    { type: 'campaign', title: 'Email campaign sent', time: '3 hours ago', icon: '📧' },
    { type: 'content', title: 'New course published', time: '5 hours ago', icon: '🎓' },
    { type: 'payment', title: 'Payment received: $299', time: '1 day ago', icon: '💳' }
  ]);

  const [goals] = useState([
    { label: 'Revenue Target', current: 8450, target: 10000, unit: '$' },
    { label: 'New Contacts', current: 247, target: 300, unit: '' },
    { label: 'Content Published', current: 12, target: 20, unit: ' posts' }
  ]);

  const [teamActivity] = useState([
    { name: 'Sarah Chen', action: 'Added 5 new products', time: '30m ago', avatar: 'SC' },
    { name: 'Mike Johnson', action: 'Completed email campaign', time: '2h ago', avatar: 'MJ' },
    { name: 'Emily Watson', action: 'Updated course content', time: '4h ago', avatar: 'EW' }
  ]);

  const quickActions = [
    { label: 'Create Social Post', icon: '📝', action: 'social_post', gradient: 'var(--gradient-primary)' },
    { label: 'Send Email Campaign', icon: '📧', action: 'email_campaign', gradient: 'var(--gradient-accent)' },
    { label: 'Add New Product', icon: '🛍️', action: 'add_product', gradient: 'var(--gradient-warm)' },
    { label: 'Schedule Meeting', icon: '📅', action: 'schedule_meeting', gradient: 'var(--gradient-cool)' }
  ];

  const handleQuickAction = (action) => {
    console.log(`Quick action: ${action}`);
    // TODO: Implement quick action modals
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="dashboard-home">
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
        </div>
      </div>

      {/* Header Section */}
      <div className="dashboard-header">
        <div className="greeting-section">
          <h1 className="greeting-title">
            {getGreeting()}, <span className="gradient-text">{user?.name || 'User'}</span>
          </h1>
          <p className="greeting-subtitle">
            Here's what's happening with {user?.workspace?.name || 'your workspace'} today
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.revenue.value}</h3>
            <p className="stat-label">Total Revenue</p>
            <div className="stat-change positive">
              <span className="change-value">{stats.revenue.change}</span>
              <span className="change-period">{stats.revenue.period}</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.contacts.value}</h3>
            <p className="stat-label">New Contacts</p>
            <div className="stat-change positive">
              <span className="change-value">{stats.contacts.change}</span>
              <span className="change-period">{stats.contacts.period}</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.performance.value}</h3>
            <p className="stat-label">Campaign Performance</p>
            <div className="stat-change positive">
              <span className="change-value">{stats.performance.change}</span>
              <span className="change-period">{stats.performance.period}</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👁️</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.views.value}</h3>
            <p className="stat-label">Content Views</p>
            <div className="stat-change positive">
              <span className="change-value">{stats.views.change}</span>
              <span className="change-period">{stats.views.period}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="main-content-grid">
        {/* Left Column */}
        <div className="content-left">
          {/* Recent Activity */}
          <div className="card activity-card">
            <div className="card-header">
              <h2 className="card-title">Recent Activity</h2>
              <button className="card-action">View All</button>
            </div>
            <div className="activity-timeline">
              {recentActivity.map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-content">
                    <p className="activity-title">{activity.title}</p>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Chart Placeholder */}
          <div className="card chart-card">
            <div className="card-header">
              <h2 className="card-title">Revenue Trends</h2>
              <div className="chart-controls">
                <select className="period-selector">
                  <option>Last 30 days</option>
                  <option>Last 7 days</option>
                  <option>Last 90 days</option>
                </select>
              </div>
            </div>
            <div className="chart-placeholder">
              <div className="chart-mockup">
                <div className="chart-bars">
                  {[40, 65, 35, 80, 45, 75, 60, 90].map((height, index) => (
                    <div 
                      key={index} 
                      className="chart-bar" 
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
                <p className="chart-label">📈 Revenue increasing steadily</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="content-right">
          {/* Goals Progress */}
          <div className="card goals-card">
            <div className="card-header">
              <h2 className="card-title">Monthly Goals</h2>
            </div>
            <div className="goals-content">
              {goals.map((goal, index) => {
                const progress = (goal.current / goal.target) * 100;
                return (
                  <div key={index} className="goal-item">
                    <div className="goal-header">
                      <span className="goal-label">{goal.label}</span>
                      <span className="goal-value">
                        {goal.unit}{goal.current} / {goal.unit}{goal.target}
                      </span>
                    </div>
                    <div className="goal-progress">
                      <div 
                        className="goal-progress-bar" 
                        style={{ width: `${Math.min(progress, 100)}%` }}
                      ></div>
                    </div>
                    <span className="goal-percentage">{progress.toFixed(0)}%</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card quick-actions-card">
            <div className="card-header">
              <h2 className="card-title">Quick Actions</h2>
            </div>
            <div className="quick-actions-grid">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.action)}
                  className="quick-action-button"
                  style={{ '--action-gradient': action.gradient }}
                >
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-label">{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Team Activity */}
          <div className="card team-card">
            <div className="card-header">
              <h2 className="card-title">Team Activity</h2>
            </div>
            <div className="team-activity">
              {teamActivity.map((member, index) => (
                <div key={index} className="team-member">
                  <div className="member-avatar">{member.avatar}</div>
                  <div className="member-content">
                    <p className="member-name">{member.name}</p>
                    <p className="member-action">{member.action}</p>
                    <span className="member-time">{member.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;