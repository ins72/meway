import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './SocialMediaPage.css';

const SocialMediaPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [platforms, setPlatforms] = useState([
    {
      name: 'Instagram',
      connected: true,
      followers: '12.5K',
      engagement: '4.8%',
      icon: '📸',
      gradient: 'var(--gradient-primary)',
      posts: 145,
      reach: '89.2K'
    },
    {
      name: 'Twitter',
      connected: true,
      followers: '8.2K',
      engagement: '3.2%',
      icon: '🐦',
      gradient: 'var(--gradient-accent)',
      posts: 89,
      reach: '45.8K'
    },
    {
      name: 'TikTok',
      connected: false,
      followers: '25.1K',
      engagement: '7.1%',
      icon: '🎵',
      gradient: 'var(--gradient-warm)',
      posts: 67,
      reach: '125.4K'
    },
    {
      name: 'LinkedIn',
      connected: true,
      followers: '3.4K',
      engagement: '5.9%',
      icon: '💼',
      gradient: 'var(--gradient-cool)',
      posts: 23,
      reach: '18.7K'
    }
  ]);

  const [recentPosts] = useState([
    {
      id: 1,
      platform: 'Instagram',
      content: 'Just launched our new product line! 🚀 #innovation',
      image: '🖼️',
      likes: 234,
      comments: 45,
      shares: 12,
      time: '2 hours ago',
      performance: 'high'
    },
    {
      id: 2,
      platform: 'Twitter',
      content: 'Excited to announce our partnership with @TechCorp',
      image: null,
      likes: 89,
      comments: 23,
      shares: 34,
      time: '4 hours ago',
      performance: 'medium'
    },
    {
      id: 3,
      platform: 'LinkedIn',
      content: 'Industry insights: The future of digital marketing',
      image: '📊',
      likes: 156,
      comments: 67,
      shares: 23,
      time: '1 day ago',
      performance: 'high'
    }
  ]);

  const [scheduledPosts] = useState([
    {
      id: 1,
      platform: 'Instagram',
      content: 'Behind the scenes of our creative process ✨',
      scheduledFor: 'Today 6:00 PM',
      status: 'scheduled'
    },
    {
      id: 2,
      platform: 'Twitter',
      content: 'Join us for our live Q&A session tomorrow!',
      scheduledFor: 'Tomorrow 2:00 PM',
      status: 'scheduled'
    }
  ]);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: 'overview' },
    { id: 'content', label: 'Content', icon: 'content' },
    { id: 'analytics', label: 'Analytics', icon: 'chart' },
    { id: 'leads', label: 'Lead Database', icon: 'database' }
  ];

  const handleCreatePost = () => {
    console.log('Opening create post modal');
    // TODO: Implement create post modal
  };

  const handleScheduleCampaign = () => {
    console.log('Opening schedule campaign modal');
    // TODO: Implement schedule campaign modal
  };

  const handleConnectPlatform = (platform) => {
    console.log(`Connecting to ${platform}`);
    // TODO: Implement platform connection
  };

  return (
    <div className="social-media-page">
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
            Social Media <span className="gradient-text">Management</span>
          </h1>
          <p className="page-subtitle">
            Grow your audience across all platforms with unified management
          </p>
        </div>
        <div className="header-actions">
          <button onClick={handleCreatePost} className="btn btn-primary">
            <span className="btn-icon">+</span>
            Create Post
          </button>
          <button onClick={handleScheduleCampaign} className="btn btn-secondary">
            <span className="btn-icon">📅</span>
            Schedule Campaign
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              <span className="tab-icon-professional">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-tab">
            {/* Platform Cards */}
            <div className="platforms-grid">
              {platforms.map((platform, index) => (
                <div key={index} className="platform-card card">
                  <div className="platform-header">
                    <div className="platform-info">
                      <span className="platform-icon">{platform.icon}</span>
                      <div>
                        <h3 className="platform-name">{platform.name}</h3>
                        <span className={`connection-status ${platform.connected ? 'connected' : 'disconnected'}`}>
                          {platform.connected ? '🟢 Connected' : '🔴 Not Connected'}
                        </span>
                      </div>
                    </div>
                    {!platform.connected && (
                      <button 
                        onClick={() => handleConnectPlatform(platform.name)}
                        className="btn btn-secondary btn-sm"
                      >
                        Connect
                      </button>
                    )}
                  </div>
                  
                  <div className="platform-stats">
                    <div className="stat-item">
                      <span className="stat-value">{platform.followers}</span>
                      <span className="stat-label">Followers</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{platform.engagement}</span>
                      <span className="stat-label">Engagement</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{platform.posts}</span>
                      <span className="stat-label">Posts</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{platform.reach}</span>
                      <span className="stat-label">Reach</span>
                    </div>
                  </div>

                  <div 
                    className="platform-accent" 
                    style={{ background: platform.gradient }}
                  ></div>
                </div>
              ))}
            </div>

            {/* Content Grid */}
            <div className="content-grid">
              {/* Recent Posts */}
              <div className="card recent-posts-card">
                <div className="card-header">
                  <h2 className="card-title">Recent Posts</h2>
                  <button className="card-action">View All</button>
                </div>
                <div className="posts-list">
                  {recentPosts.map((post) => (
                    <div key={post.id} className="post-item">
                      <div className="post-header">
                        <span className="post-platform">{post.platform}</span>
                        <span className={`post-performance ${post.performance}`}>
                          {post.performance === 'high' ? '📈' : '📊'} {post.performance}
                        </span>
                      </div>
                      <p className="post-content">{post.content}</p>
                      {post.image && (
                        <div className="post-image">{post.image}</div>
                      )}
                      <div className="post-stats">
                        <span className="stat">❤️ {post.likes}</span>
                        <span className="stat">💬 {post.comments}</span>
                        <span className="stat">🔄 {post.shares}</span>
                        <span className="post-time">{post.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Scheduled Posts */}
              <div className="card scheduled-posts-card">
                <div className="card-header">
                  <h2 className="card-title">Scheduled Posts</h2>
                  <button className="card-action">Schedule New</button>
                </div>
                <div className="scheduled-list">
                  {scheduledPosts.map((post) => (
                    <div key={post.id} className="scheduled-item">
                      <div className="scheduled-header">
                        <span className="scheduled-platform">{post.platform}</span>
                        <span className="scheduled-time">{post.scheduledFor}</span>
                      </div>
                      <p className="scheduled-content">{post.content}</p>
                      <div className="scheduled-actions">
                        <button className="btn btn-ghost btn-sm">Edit</button>
                        <button className="btn btn-ghost btn-sm">Delete</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="card quick-actions-card">
                <div className="card-header">
                  <h2 className="card-title">Quick Actions</h2>
                </div>
                <div className="quick-actions-grid">
                  <button className="quick-action-btn">
                    <span className="action-icon">🔍</span>
                    <span className="action-label">Find Influencers</span>
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">📊</span>
                    <span className="action-label">Analytics Report</span>
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">🎯</span>
                    <span className="action-label">Create Campaign</span>
                  </button>
                  <button className="quick-action-btn">
                    <span className="action-icon">📈</span>
                    <span className="action-label">Growth Tips</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'content' && (
          <div className="content-tab">
            <div className="content-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">📝</span>
                <h3>Content Library</h3>
                <p>Upload and manage your social media content</p>
                <button className="btn btn-primary">Upload Content</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="analytics-tab">
            <div className="analytics-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">📊</span>
                <h3>Analytics Dashboard</h3>
                <p>Track your social media performance across all platforms</p>
                <button className="btn btn-primary">View Analytics</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'leads' && (
          <div className="leads-tab">
            <div className="leads-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">👥</span>
                <h3>Lead Database</h3>
                <p>50M+ Instagram profiles with advanced filtering</p>
                <button className="btn btn-primary">Explore Database</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialMediaPage;