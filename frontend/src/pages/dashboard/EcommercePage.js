import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './EcommercePage.css';

const EcommercePage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalRevenue: { value: '$24,580', change: '+12.5%', period: 'this month' },
    orders: { value: '143', change: '+18.2%', period: 'this week' },
    products: { value: '89', change: '+5', period: 'active' },
    conversionRate: { value: '3.4%', change: '+0.8%', period: 'vs last month' }
  });

  const [recentOrders] = useState([
    {
      id: 'ORD-001',
      customer: 'Sarah Johnson',
      amount: '$299.99',
      status: 'shipped',
      date: '2 hours ago',
      items: 3
    },
    {
      id: 'ORD-002',
      customer: 'Mike Chen',
      amount: '$149.50',
      status: 'processing',
      date: '4 hours ago',
      items: 2
    },
    {
      id: 'ORD-003',
      customer: 'Emily Davis',
      amount: '$89.99',
      status: 'delivered',
      date: '6 hours ago',
      items: 1
    },
    {
      id: 'ORD-004',
      customer: 'James Wilson',
      amount: '$199.99',
      status: 'pending',
      date: '1 day ago',
      items: 2
    }
  ]);

  const [topProducts] = useState([
    {
      id: 1,
      name: 'Premium Wireless Headphones',
      image: '🎧',
      price: '$299.99',
      sales: 45,
      revenue: '$13,499.55',
      stock: 12,
      category: 'Electronics'
    },
    {
      id: 2,
      name: 'Organic Cotton T-Shirt',
      image: '👕',
      price: '$39.99',
      sales: 89,
      revenue: '$3,559.11',
      stock: 5,
      category: 'Clothing'
    },
    {
      id: 3,
      name: 'Smart Fitness Watch',
      image: '⌚',
      price: '$199.99',
      sales: 32,
      revenue: '$6,399.68',
      stock: 0,
      category: 'Electronics'
    }
  ]);

  const [inventoryAlerts] = useState([
    { product: 'Organic Cotton T-Shirt', stock: 5, level: 'low', color: 'orange' },
    { product: 'Smart Fitness Watch', stock: 0, level: 'out', color: 'red' },
    { product: 'Premium Headphones', stock: 3, level: 'critical', color: 'red' }
  ]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'products', label: 'Products', icon: '📦' },
    { id: 'orders', label: 'Orders', icon: '🛒' },
    { id: 'analytics', label: 'Analytics', icon: '📈' }
  ];

  const getStatusBadge = (status) => {
    const badges = {
      pending: { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', icon: '⏳' },
      processing: { color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)', icon: '⚙️' },
      shipped: { color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)', icon: '🚚' },
      delivered: { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', icon: '✅' }
    };
    return badges[status] || badges.pending;
  };

  const getStockLevel = (stock) => {
    if (stock === 0) return { text: 'Out of Stock', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
    if (stock <= 5) return { text: 'Low Stock', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' };
    return { text: 'In Stock', color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' };
  };

  const handleAddProduct = () => {
    console.log('Opening add product modal');
    // TODO: Implement add product modal
  };

  const handleViewStore = () => {
    console.log('Opening store preview');
    // TODO: Implement store preview
  };

  return (
    <div className="ecommerce-page">
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
            E-commerce <span className="gradient-text">Store</span>
          </h1>
          <p className="page-subtitle">
            Manage your online store, products, and orders
          </p>
        </div>
        <div className="header-actions">
          <button onClick={handleAddProduct} className="btn btn-primary">
            <span>➕</span>
            Add Product
          </button>
          <button onClick={handleViewStore} className="btn btn-secondary">
            <span>🔍</span>
            View Store
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
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Stats Cards */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <h3 className="stat-value">{stats.totalRevenue.value}</h3>
                  <p className="stat-label">Total Revenue</p>
                  <div className="stat-change positive">
                    <span className="change-value">{stats.totalRevenue.change}</span>
                    <span className="change-period">{stats.totalRevenue.period}</span>
                  </div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🛒</div>
                <div className="stat-content">
                  <h3 className="stat-value">{stats.orders.value}</h3>
                  <p className="stat-label">Orders</p>
                  <div className="stat-change positive">
                    <span className="change-value">{stats.orders.change}</span>
                    <span className="change-period">{stats.orders.period}</span>
                  </div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">📦</div>
                <div className="stat-content">
                  <h3 className="stat-value">{stats.products.value}</h3>
                  <p className="stat-label">Products</p>
                  <div className="stat-change positive">
                    <span className="change-value">{stats.products.change}</span>
                    <span className="change-period">{stats.products.period}</span>
                  </div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">📈</div>
                <div className="stat-content">
                  <h3 className="stat-value">{stats.conversionRate.value}</h3>
                  <p className="stat-label">Conversion Rate</p>
                  <div className="stat-change positive">
                    <span className="change-value">{stats.conversionRate.change}</span>
                    <span className="change-period">{stats.conversionRate.period}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="main-content-grid">
              {/* Recent Orders */}
              <div className="card recent-orders-card">
                <div className="card-header">
                  <h2 className="card-title">Recent Orders</h2>
                  <button className="card-action">View All</button>
                </div>
                <div className="orders-table">
                  <div className="table-header">
                    <span>Order ID</span>
                    <span>Customer</span>
                    <span>Amount</span>
                    <span>Status</span>
                    <span>Date</span>
                    <span>Actions</span>
                  </div>
                  {recentOrders.map((order) => {
                    const statusStyle = getStatusBadge(order.status);
                    return (
                      <div key={order.id} className="table-row">
                        <span className="order-id">{order.id}</span>
                        <span className="customer-name">{order.customer}</span>
                        <span className="order-amount">{order.amount}</span>
                        <span 
                          className="order-status"
                          style={{ 
                            color: statusStyle.color, 
                            background: statusStyle.bg 
                          }}
                        >
                          {statusStyle.icon} {order.status}
                        </span>
                        <span className="order-date">{order.date}</span>
                        <div className="order-actions">
                          <button className="btn btn-ghost btn-sm">View</button>
                          <button className="btn btn-ghost btn-sm">Update</button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Sidebar Content */}
              <div className="sidebar-content">
                {/* Inventory Alerts */}
                <div className="card inventory-alerts-card">
                  <div className="card-header">
                    <h2 className="card-title">Inventory Alerts</h2>
                  </div>
                  <div className="alerts-list">
                    {inventoryAlerts.map((alert, index) => (
                      <div key={index} className="alert-item">
                        <div className="alert-info">
                          <span className="alert-product">{alert.product}</span>
                          <span className="alert-stock">Stock: {alert.stock}</span>
                        </div>
                        <span 
                          className={`alert-level ${alert.level}`}
                          style={{ color: alert.color }}
                        >
                          {alert.level === 'out' ? '❌' : '⚠️'} {alert.level}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Products */}
                <div className="card top-products-card">
                  <div className="card-header">
                    <h2 className="card-title">Top Selling Products</h2>
                  </div>
                  <div className="products-list">
                    {topProducts.map((product) => {
                      const stockLevel = getStockLevel(product.stock);
                      return (
                        <div key={product.id} className="product-item">
                          <div className="product-info">
                            <span className="product-image">{product.image}</span>
                            <div className="product-details">
                              <span className="product-name">{product.name}</span>
                              <span className="product-category">{product.category}</span>
                            </div>
                          </div>
                          <div className="product-stats">
                            <span className="product-sales">{product.sales} sales</span>
                            <span className="product-revenue">{product.revenue}</span>
                            <span 
                              className="product-stock"
                              style={{ 
                                color: stockLevel.color, 
                                background: stockLevel.bg 
                              }}
                            >
                              {stockLevel.text}
                            </span>
                          </div>
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
                    <button className="quick-action-btn">
                      <span className="action-icon">📊</span>
                      <span className="action-label">Sales Report</span>
                    </button>
                    <button className="quick-action-btn">
                      <span className="action-icon">💳</span>
                      <span className="action-label">Payment Settings</span>
                    </button>
                    <button className="quick-action-btn">
                      <span className="action-icon">🚚</span>
                      <span className="action-label">Shipping Options</span>
                    </button>
                    <button className="quick-action-btn">
                      <span className="action-icon">🎨</span>
                      <span className="action-label">Store Design</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'products' && (
          <div className="products-tab">
            <div className="products-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">📦</span>
                <h3>Product Management</h3>
                <p>Add, edit, and organize your store products</p>
                <button className="btn btn-primary">Add First Product</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="orders-tab">
            <div className="orders-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">🛒</span>
                <h3>Order Management</h3>
                <p>Track and manage all your customer orders</p>
                <button className="btn btn-primary">View All Orders</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="analytics-tab">
            <div className="analytics-placeholder card">
              <div className="placeholder-content">
                <span className="placeholder-icon">📈</span>
                <h3>Store Analytics</h3>
                <p>Deep insights into your store performance</p>
                <button className="btn btn-primary">View Analytics</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EcommercePage;