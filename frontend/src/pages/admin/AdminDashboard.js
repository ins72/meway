import React
import ApiService from '../../services/apiService';, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  UserGroupIcon, 
  CurrencyDollarIcon,
  ChartBarIcon,
  ServerIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CogIcon,
  BellIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import Button from '../../components/Button';

const AdminDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [users, setUsers] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      // Real API data
      const loadAdminData = async () => {
    try {
      const metrics = await ApiService.getAdminStats();
      setMetrics(metrics);
        totalUsers: 12450,
        userGrowth: 15.2,
        totalRevenue: 89750,
        revenueGrowth: 23.5,
        activeSubscriptions: 8320,
        subscriptionGrowth: 18.9,
        systemUptime: 99.9,
        apiRequests: 2456789,
        errorRate: 0.2,
        avgResponseTime: 125
      });

      const health = await ApiService.getSystemHealth();
      setSystemHealth(health);
        status: 'healthy',
        database: 'healthy',
        redis: 'healthy',
        storage: 'healthy',
        api: 'healthy',
        queue: 'warning',
        memory: 68,
        cpu: 42,
        disk: 34
      });

      const users = await ApiService.getUsers();
      setUsers(users);
        { id: 1, name: 'John Smith', email: 'john@example.com', status: 'active', plan: 'Premium', joined: '2025-01-15' },
        { id: 2, name: 'Sarah Johnson', email: 'sarah@company.com', status: 'active', plan: 'Enterprise', joined: '2025-01-14' },
        { id: 3, name: 'Mike Chen', email: 'mike@startup.com', status: 'suspended', plan: 'Starter', joined: '2025-01-13' },
        { id: 4, name: 'Emily Davis', email: 'emily@creative.com', status: 'active', plan: 'Premium', joined: '2025-01-12' }
      ]);

      const activity = await ApiService.getAdminStats();
      setRecentActivity(activity.recent || []);
        { id: 1, action: 'User registered', details: 'New user: alex@example.com', time: '2 minutes ago', type: 'user' },
        { id: 2, action: 'Payment processed', details: '$299 for Premium plan', time: '5 minutes ago', type: 'payment' },
        { id: 3, action: 'System alert', details: 'Queue processing delay detected', time: '10 minutes ago', type: 'system' },
        { id: 4, action: 'Feature activated', details: 'AI content generation enabled', time: '15 minutes ago', type: 'feature' },
        { id: 5, action: 'Support ticket', details: 'High priority ticket #1234', time: '20 minutes ago', type: 'support' }
      ]);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, change, icon: Icon, color = 'primary', subtitle = '' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary">{title}</p>
          <p className="text-3xl font-bold text-primary mt-2">{value}</p>
          {subtitle && (
            <p className="text-sm text-secondary mt-1">{subtitle}</p>
          )}
          {change && (
            <p className={`text-sm mt-2 ${change > 0 ? 'text-accent-success' : 'text-accent-danger'}`}>
              {change > 0 ? '+' : ''}{change}% vs last month
            </p>
          )}
        </div>
        <div className={`bg-gradient-${color} p-3 rounded-lg`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </motion.div>
  );

  const SystemHealthCard = ({ title, status, value, icon: Icon }) => (
    <div className="card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Icon className="w-6 h-6 text-accent-primary" />
          <div>
            <h4 className="font-medium text-primary">{title}</h4>
            {value && <p className="text-sm text-secondary">{value}%</p>}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {status === 'healthy' && <CheckCircleIcon className="w-5 h-5 text-accent-success" />}
          {status === 'warning' && <ExclamationTriangleIcon className="w-5 h-5 text-accent-warning" />}
          {status === 'error' && <ExclamationTriangleIcon className="w-5 h-5 text-accent-danger" />}
          <span className={`text-sm font-medium ${
            status === 'healthy' ? 'text-accent-success' :
            status === 'warning' ? 'text-accent-warning' : 'text-accent-danger'
          }`}>
            {status}
          </span>
        </div>
      </div>
    </div>
  );

  const UserRow = ({ user }) => (
    <tr className="hover-surface">
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">{user.name.charAt(0)}</span>
          </div>
          <div className="ml-3">
            <p className="font-medium text-primary">{user.name}</p>
            <p className="text-sm text-secondary">{user.email}</p>
          </div>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          user.status === 'active' 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {user.status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-primary">{user.plan}</td>
      <td className="px-6 py-4 whitespace-nowrap text-secondary">{user.joined}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <Button variant="secondary" size="small">Manage</Button>
      </td>
    </tr>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8 text-accent-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary">Admin Dashboard</h1>
          <p className="text-secondary mt-1">Monitor and manage your Mewayz platform</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary">
            <BellIcon className="w-4 h-4 mr-2" />
            Notifications
          </Button>
          <Button variant="secondary">
            <DocumentTextIcon className="w-4 h-4 mr-2" />
            Reports
          </Button>
          <Button>
            <CogIcon className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* System Status Alert */}
      {systemHealth?.queue === 'warning' && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4"
        >
          <div className="flex items-center space-x-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
            <div>
              <h4 className="font-medium text-yellow-800 dark:text-yellow-200">System Alert</h4>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">Queue processing is experiencing delays. Monitoring the situation.</p>
            </div>
            <Button variant="secondary" size="small">
              View Details
            </Button>
          </div>
        </motion.div>
      )}

      {/* Tabs */}
      <div className="border-b border-default">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'users', name: 'Users' },
            { id: 'system', name: 'System Health' },
            { id: 'activity', name: 'Activity' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-accent-primary text-accent-primary'
                  : 'border-transparent text-secondary hover:text-primary hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Users"
              value={metrics.totalUsers.toLocaleString()}
              change={metrics.userGrowth}
              icon={UserGroupIcon}
              color="primary"
            />
            <MetricCard
              title="Total Revenue"
              value={`$${metrics.totalRevenue.toLocaleString()}`}
              change={metrics.revenueGrowth}
              icon={CurrencyDollarIcon}
              color="success"
            />
            <MetricCard
              title="Active Subscriptions"
              value={metrics.activeSubscriptions.toLocaleString()}
              change={metrics.subscriptionGrowth}
              icon={ChartBarIcon}
              color="warning"
            />
            <MetricCard
              title="System Uptime"
              value={`${metrics.systemUptime}%`}
              icon={ServerIcon}
              color="primary"
            />
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-primary mb-4">API Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-secondary">Total Requests</span>
                  <span className="font-medium text-primary">{metrics.apiRequests.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary">Error Rate</span>
                  <span className="font-medium text-primary">{metrics.errorRate}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary">Avg Response Time</span>
                  <span className="font-medium text-primary">{metrics.avgResponseTime}ms</span>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-lg font-semibold text-primary mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button variant="secondary" size="small" fullWidth>
                  <UserGroupIcon className="w-4 h-4 mr-2" />
                  Manage Users
                </Button>
                <Button variant="secondary" size="small" fullWidth>
                  <ShieldCheckIcon className="w-4 h-4 mr-2" />
                  Security Settings
                </Button>
                <Button variant="secondary" size="small" fullWidth>
                  <GlobeAltIcon className="w-4 h-4 mr-2" />
                  Platform Settings
                </Button>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-lg font-semibold text-primary mb-4">System Overview</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-secondary">Database</span>
                  <CheckCircleIcon className="w-5 h-5 text-accent-success" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary">Cache</span>
                  <CheckCircleIcon className="w-5 h-5 text-accent-success" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary">Queue</span>
                  <ExclamationTriangleIcon className="w-5 h-5 text-accent-warning" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">User Management</h2>
            <div className="flex items-center space-x-3">
              <input 
                type="text" 
                placeholder="Search users..."
                className="input px-3 py-2 rounded-md"
              />
              <select className="input px-3 py-2 rounded-md">
                <option>All Users</option>
                <option>Active</option>
                <option>Suspended</option>
                <option>Premium</option>
              </select>
              <Button>Export</Button>
            </div>
          </div>
          
          <div className="card-elevated overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Plan
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Joined
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {users.map((user) => (
                    <UserRow key={user.id} user={user} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-primary">System Health</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <SystemHealthCard
              title="Database"
              status={systemHealth.database}
              icon={ServerIcon}
            />
            <SystemHealthCard
              title="Redis Cache"
              status={systemHealth.redis}
              icon={ChartBarIcon}
            />
            <SystemHealthCard
              title="Storage"
              status={systemHealth.storage}
              icon={ServerIcon}
            />
            <SystemHealthCard
              title="API Gateway"
              status={systemHealth.api}
              icon={GlobeAltIcon}
            />
            <SystemHealthCard
              title="Queue System"
              status={systemHealth.queue}
              icon={ClockIcon}
            />
            <SystemHealthCard
              title="Memory Usage"
              status="healthy"
              value={systemHealth.memory}
              icon={ChartBarIcon}
            />
          </div>
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-primary">Recent Activity</h2>
          
          <div className="card-elevated">
            <div className="p-6">
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3 p-3 hover-surface rounded-lg transition-colors">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      activity.type === 'user' ? 'bg-blue-500' :
                      activity.type === 'payment' ? 'bg-green-500' :
                      activity.type === 'system' ? 'bg-yellow-500' :
                      activity.type === 'feature' ? 'bg-purple-500' : 'bg-red-500'
                    }`}></div>
                    <div className="flex-1">
                      <p className="font-medium text-primary">{activity.action}</p>
                      <p className="text-secondary text-sm">{activity.details}</p>
                      <p className="text-secondary text-xs mt-1">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;