import React
import ApiService from '../../services/apiService';, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  GlobeAltIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  EyeIcon,
  CogIcon,
  PhotoIcon,
  DocumentTextIcon,
  PaintBrushIcon,
  CodeBracketIcon,
  ArrowTopRightOnSquareIcon,
  ChartBarIcon,
  FolderIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline';
import Button from '../../components/Button';

const WebsiteBuilderPage = () => {
  const [websites, setWebsites] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [components, setComponents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadWebsiteBuilderData();
  }, []);

  const loadWebsiteBuilderData = async () => {
    try {
      // Real API data
      const websites = await ApiService.getWebsites();
      setWebsites(websites);
        {
          id: 1,
          name: 'My Business Website',
          domain: 'mybusiness.mewayz.com',
          customDomain: 'www.mybusiness.com',
          status: 'published',
          template: 'Business Pro',
          pages: 5,
          visitors: 2340,
          lastModified: '2025-07-19',
          screenshot: '/api/placeholder/300/200'
        },
        {
          id: 2,
          name: 'Portfolio Site',
          domain: 'portfolio.mewayz.com',
          customDomain: null,
          status: 'draft',
          template: 'Creative Portfolio',
          pages: 3,
          visitors: 0,
          lastModified: '2025-07-18',
          screenshot: '/api/placeholder/300/200'
        },
        {
          id: 3,
          name: 'Online Store',
          domain: 'store.mewayz.com',
          customDomain: 'shop.example.com',
          status: 'published',
          template: 'E-commerce Pro',
          pages: 8,
          visitors: 1890,
          lastModified: '2025-07-17',
          screenshot: '/api/placeholder/300/200'
        }
      ]);

      const templates = await ApiService.getTemplates();
      setTemplates(templates);
        { id: 1, name: 'Business Professional', category: 'Business', price: 'Free', features: ['Responsive', 'SEO Optimized', 'Contact Forms'] },
        { id: 2, name: 'Creative Portfolio', category: 'Portfolio', price: '$29', features: ['Gallery', 'Animations', 'Blog'] },
        { id: 3, name: 'E-commerce Store', category: 'E-commerce', price: '$49', features: ['Shopping Cart', 'Payment Integration', 'Inventory'] },
        { id: 4, name: 'Restaurant & Food', category: 'Restaurant', price: '$39', features: ['Menu Display', 'Reservations', 'Gallery'] }
      ]);

      setComponents([
        { id: 1, name: 'Hero Section', category: 'Headers', type: 'layout' },
        { id: 2, name: 'Image Gallery', category: 'Media', type: 'widget' },
        { id: 3, name: 'Contact Form', category: 'Forms', type: 'functional' },
        { id: 4, name: 'Testimonials', category: 'Social Proof', type: 'content' },
        { id: 5, name: 'Pricing Table', category: 'Commerce', type: 'widget' },
        { id: 6, name: 'Blog Feed', category: 'Content', type: 'dynamic' }
      ]);

      setAnalytics({
        totalWebsites: 3,
        publishedSites: 2,
        totalPageViews: 4230,
        totalVisitors: 2890,
        averageTimeOnSite: '3:45',
        bounceRate: 32.5
      });
    } catch (error) {
      console.error('Failed to load website builder data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'primary' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary">{title}</p>
          <p className="text-3xl font-bold text-primary mt-2">{value}</p>
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

  const WebsiteCard = ({ website }) => (
    <div className="card-elevated p-6">
      <div className="aspect-video bg-gradient-surface rounded-lg mb-4 flex items-center justify-center">
        <GlobeAltIcon className="w-16 h-16 text-accent-primary" />
      </div>
      
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-primary">{website.name}</h3>
            <p className="text-sm text-secondary">{website.domain}</p>
            {website.customDomain && (
              <p className="text-sm text-accent-primary">{website.customDomain}</p>
            )}
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            website.status === 'published'
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {website.status}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-secondary">Template</p>
            <p className="font-medium text-primary">{website.template}</p>
          </div>
          <div>
            <p className="text-secondary">Pages</p>
            <p className="font-medium text-primary">{website.pages}</p>
          </div>
          <div>
            <p className="text-secondary">Visitors</p>
            <p className="font-medium text-primary">{website.visitors.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-secondary">Modified</p>
            <p className="font-medium text-primary">{website.lastModified}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-default">
          <div className="flex items-center space-x-2">
            <button className="p-2 text-secondary hover:text-primary">
              <EyeIcon className="w-4 h-4" />
            </button>
            <button className="p-2 text-secondary hover:text-primary">
              <PencilIcon className="w-4 h-4" />
            </button>
            <button className="p-2 text-secondary hover:text-primary">
              <CogIcon className="w-4 h-4" />
            </button>
            <button className="p-2 text-secondary hover:text-primary">
              <ChartBarIcon className="w-4 h-4" />
            </button>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="secondary" size="small">
              <ArrowTopRightOnSquareIcon className="w-4 h-4 mr-1" />
              Visit
            </Button>
            <Button size="small">
              <PencilIcon className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  const TemplateCard = ({ template }) => (
    <div className="card-elevated p-6 hover-surface transition-colors cursor-pointer">
      <div className="aspect-video bg-gradient-surface rounded-lg mb-4 flex items-center justify-center">
        <PaintBrushIcon className="w-12 h-12 text-accent-primary" />
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-primary">{template.name}</h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            template.price === 'Free' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
          }`}>
            {template.price}
          </span>
        </div>
        
        <p className="text-sm text-secondary">{template.category}</p>
        
        <div className="space-y-1">
          {template.features.map((feature, index) => (
            <div key={index} className="flex items-center space-x-2 text-sm">
              <div className="w-1.5 h-1.5 bg-accent-primary rounded-full"></div>
              <span className="text-secondary">{feature}</span>
            </div>
          ))}
        </div>
        
        <div className="pt-3 border-t border-default">
          <Button size="small" fullWidth>
            Use Template
          </Button>
        </div>
      </div>
    </div>
  );

  const ComponentCard = ({ component }) => (
    <div className="card p-4 hover-surface transition-colors cursor-pointer">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
          <CodeBracketIcon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h4 className="font-medium text-primary">{component.name}</h4>
          <p className="text-sm text-secondary">{component.category}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          component.type === 'layout' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
          component.type === 'widget' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
          component.type === 'functional' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' :
          'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
        }`}>
          {component.type}
        </span>
      </div>
    </div>
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
          <h1 className="text-3xl font-bold text-primary">Website Builder</h1>
          <p className="text-secondary mt-1">Create stunning websites with drag & drop builder</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary">
            <FolderIcon className="w-4 h-4 mr-2" />
            Import Site
          </Button>
          <Button variant="secondary">
            <ClipboardDocumentIcon className="w-4 h-4 mr-2" />
            Templates
          </Button>
          <Button>
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Website
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-default">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'websites', name: 'My Websites' },
            { id: 'templates', name: 'Templates' },
            { id: 'components', name: 'Components' }
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
          {/* Analytics Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Websites"
              value={analytics.totalWebsites.toString()}
              icon={GlobeAltIcon}
              color="primary"
            />
            <StatCard
              title="Published Sites"
              value={analytics.publishedSites.toString()}
              icon={ArrowTopRightOnSquareIcon}
              color="success"
            />
            <StatCard
              title="Total Visitors"
              value={analytics.totalVisitors.toLocaleString()}
              change={15.2}
              icon={EyeIcon}
              color="warning"
            />
            <StatCard
              title="Page Views"
              value={analytics.totalPageViews.toLocaleString()}
              change={8.5}
              icon={ChartBarIcon}
              color="primary"
            />
          </div>

          {/* Recent Websites */}
          <div>
            <h2 className="text-xl font-semibold text-primary mb-4">Recent Websites</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {websites.slice(0, 3).map((website) => (
                <WebsiteCard key={website.id} website={website} />
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <PlusIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Create New Website</h3>
              <p className="text-secondary">Start building with our drag & drop editor</p>
            </button>
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <PaintBrushIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Browse Templates</h3>
              <p className="text-secondary">Choose from professional pre-designed templates</p>
            </button>
            <button className="card-elevated p-6 text-left hover-surface transition-colors">
              <DocumentTextIcon className="w-8 h-8 text-accent-primary mb-4" />
              <h3 className="font-semibold text-primary mb-2">Import Content</h3>
              <p className="text-secondary">Import from existing websites or platforms</p>
            </button>
          </div>
        </div>
      )}

      {activeTab === 'websites' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">My Websites</h2>
            <div className="flex items-center space-x-3">
              <select className="input px-3 py-2 rounded-md">
                <option>All Websites</option>
                <option>Published</option>
                <option>Draft</option>
                <option>Archived</option>
              </select>
              <select className="input px-3 py-2 rounded-md">
                <option>Sort by Modified</option>
                <option>Sort by Name</option>
                <option>Sort by Visitors</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {websites.map((website) => (
              <WebsiteCard key={website.id} website={website} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">Website Templates</h2>
            <div className="flex items-center space-x-3">
              <select className="input px-3 py-2 rounded-md">
                <option>All Categories</option>
                <option>Business</option>
                <option>Portfolio</option>
                <option>E-commerce</option>
                <option>Restaurant</option>
              </select>
              <select className="input px-3 py-2 rounded-md">
                <option>All Prices</option>
                <option>Free</option>
                <option>Premium</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {templates.map((template) => (
              <TemplateCard key={template.id} template={template} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'components' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-primary">Website Components</h2>
            <div className="flex items-center space-x-3">
              <select className="input px-3 py-2 rounded-md">
                <option>All Categories</option>
                <option>Headers</option>
                <option>Media</option>
                <option>Forms</option>
                <option>Social Proof</option>
                <option>Commerce</option>
              </select>
              <select className="input px-3 py-2 rounded-md">
                <option>All Types</option>
                <option>Layout</option>
                <option>Widget</option>
                <option>Functional</option>
                <option>Dynamic</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {components.map((component) => (
              <ComponentCard key={component.id} component={component} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WebsiteBuilderPage;