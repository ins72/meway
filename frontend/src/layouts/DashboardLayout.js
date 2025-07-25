import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useNotification } from '../contexts/NotificationContext';
import WorkspaceSelector from '../components/WorkspaceSelector';
import GlobalSearch from '../components/GlobalSearch';
import HelpSupportCenter from '../components/HelpSupportCenter';
import Breadcrumb from '../components/Breadcrumb';
import {
  HomeIcon,
  SparklesIcon,
  BuildingOffice2Icon,
  BuildingOfficeIcon,
  CreditCardIcon,
  DocumentTextIcon,
  ChartBarIcon,
  GlobeAltIcon,
  ShoppingBagIcon,
  AcademicCapIcon,
  UserIcon,
  UsersIcon,
  EnvelopeIcon,
  WrenchScrewdriverIcon,
  CalendarIcon,
  BanknotesIcon,
  ShieldCheckIcon,
  CogIcon,
  LockClosedIcon,
  ChatBubbleLeftRightIcon,
  PuzzlePieceIcon,
  UserPlusIcon,
  Bars3Icon,
  XMarkIcon,
  SunIcon,
  MoonIcon,
  MagnifyingGlassIcon,
  QuestionMarkCircleIcon,
  BellIcon,
  UserCircleIcon,
  LinkIcon,
  TicketIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

const DashboardLayout = ({ isAdmin = false }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { success } = useNotification();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const navigation = [
    // Core Navigation
    { name: 'Console', href: '/dashboard', icon: HomeIcon, description: 'Dashboard Overview' },
    { name: 'Socials', href: '/dashboard/social-media', icon: ChartBarIcon, description: 'Social Media Management' },
    { name: 'Instagram Leads', href: '/dashboard/instagram-leads', icon: UserIcon, description: 'Instagram Lead Generation' },
    { name: 'Link in Bio', href: '/dashboard/bio-sites', icon: GlobeAltIcon, description: 'Bio Link Pages' },
    { name: 'Leads', href: '/dashboard/crm', icon: EnvelopeIcon, description: 'CRM & Email Marketing' },
    { name: 'Link Shortener', href: '/dashboard/link-shortener', icon: LinkIcon, description: 'URL Shortening Service' },
    { name: 'Referral System', href: '/dashboard/referrals', icon: UserPlusIcon, description: 'Referral Program' },
    
    // Business Tools
    { name: 'Website Builder', href: '/dashboard/website-builder', icon: WrenchScrewdriverIcon, description: 'Build Websites' },
    { name: 'Users', href: '/dashboard/team-management', icon: UsersIcon, description: 'Team Management' },
    { name: 'Form Templates', href: '/dashboard/form-templates', icon: DocumentTextIcon, description: 'Form Builder' },
    { name: 'Discount Codes', href: '/dashboard/discount-codes', icon: TicketIcon, description: 'Promotional Codes' },
    { name: 'Finance', href: '/dashboard/financial-management', icon: BanknotesIcon, description: 'Payments & Invoicing' },
    
    // Content & Education
    { name: 'Courses & Community', href: '/dashboard/courses', icon: AcademicCapIcon, description: 'Education Platform' },
    { name: 'Marketplace & Stores', href: '/dashboard/ecommerce', icon: ShoppingBagIcon, description: 'E-commerce Platform' },
    { name: 'Template Library', href: '/dashboard/template-marketplace', icon: DocumentTextIcon, description: 'Template Marketplace' },
    { name: 'Escrow System', href: '/dashboard/escrow-system', icon: ShieldCheckIcon, description: 'Secure Transactions' },
    { name: 'Analytics & Reporting', href: '/dashboard/gamified-analytics', icon: ChartBarIcon, description: 'Business Intelligence' },
    
    // Additional Features
    { name: 'AI Features', href: '/dashboard/ai-features', icon: SparklesIcon, description: 'AI Tools' },
    { name: 'Token Management', href: '/dashboard/token-management', icon: BoltIcon, description: 'AI Token System' },
    { name: 'Email Marketing', href: '/dashboard/email-marketing', icon: EnvelopeIcon, description: 'Email Campaigns' },
    { name: 'Advanced Booking', href: '/dashboard/advanced-booking', icon: CalendarIcon, description: 'Appointment Scheduling' },
    { name: 'Realtime Collaboration', href: '/dashboard/realtime-collaboration', icon: ChatBubbleLeftRightIcon, description: 'Team Collaboration' },
    { name: 'Integrations', href: '/dashboard/integrations', icon: PuzzlePieceIcon, description: 'Third-party Integrations' },
    { name: 'Workspaces', href: '/dashboard/workspaces', icon: BuildingOffice2Icon, description: 'Workspace Management' },
    { name: 'Workspace Settings', href: '/dashboard/workspace-settings', icon: CogIcon, description: 'Team & Configuration' },
    { name: 'Subscription', href: '/dashboard/subscription', icon: CreditCardIcon, description: 'Billing & Plans' },
    { name: 'Settings', href: '/dashboard/settings', icon: UserCircleIcon, description: 'Account Settings' },
  ];

  // Admin-only navigation items
  const adminNavigation = user?.role === 'admin' ? [
    { name: 'Admin Dashboard', href: '/dashboard/admin', icon: ShieldCheckIcon, isAdmin: true },
    { name: 'User Management', href: '/dashboard/admin/users', icon: UsersIcon, isAdmin: true },
    { name: 'System Settings', href: '/dashboard/admin/system', icon: CogIcon, isAdmin: true },
    { name: 'Security Center', href: '/dashboard/admin/security', icon: LockClosedIcon, isAdmin: true },
  ] : [];

  // Support navigation items
  const supportNavigation = [
    { name: 'Contact Us', href: '/contact', icon: EnvelopeIcon, external: true },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-app">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed inset-y-0 left-0 z-50 w-64 bg-surface shadow-xl lg:hidden"
          >
            <div className="flex items-center h-16 px-4 border-b border-default">
              <h1 className="text-xl font-bold text-primary">
                {isAdmin ? 'Admin' : 'Mewayz'}
              </h1>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-2 text-secondary hover:text-primary rounded-lg hover:bg-surface-hover"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <nav className="mt-4">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center px-4 py-3 text-sm font-medium transition-colors ${
                      isActive
                        ? 'nav-active'
                        : 'text-secondary hover-surface hover:text-primary'
                    }`}
                    title={item.description}
                  >
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-surface shadow-default border-default">
          <div className="flex items-center flex-shrink-0 px-4 mb-6">
            <WorkspaceSelector />
          </div>
          <nav className="flex-1 mt-4">
            {/* Regular Navigation */}
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 text-sm font-medium transition-colors ${
                    isActive
                      ? 'nav-active'
                      : 'text-secondary hover-surface hover:text-primary'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
            
            {/* Admin Section */}
            {user?.role === 'admin' && adminNavigation.length > 0 && (
              <>
                <div className="pt-6 pb-2">
                  <h3 className="px-3 text-xs font-semibold text-secondary uppercase tracking-wide">
                    Admin Panel
                  </h3>
                </div>
                {adminNavigation.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center px-4 py-3 text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-red-500/10 text-red-400 border-l-4 border-red-400'
                          : 'text-secondary hover:bg-red-500/5 hover:text-red-300'
                      }`}
                    >
                      <item.icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </Link>
                  );
                })}
              </>
            )}

            {/* Support Section */}
            <div className="pt-6 pb-2">
              <h3 className="px-3 text-xs font-semibold text-secondary uppercase tracking-wide">
                Support
              </h3>
            </div>
            {supportNavigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center px-4 py-3 text-sm font-medium text-secondary hover:bg-surface-hover hover:text-primary transition-colors"
                target={item.external ? '_blank' : undefined}
                rel={item.external ? 'noopener noreferrer' : undefined}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </a>
            ))}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="nav-bg shadow-sm">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 text-secondary hover:text-primary lg:hidden"
              >
                <Bars3Icon className="w-5 h-5" />
              </button>
              
              <div className="flex-1 max-w-md ml-4">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                  <input
                    type="text"
                    placeholder="Search..."
                    className="w-full pl-10 pr-4 py-2 text-sm input rounded-lg focus-ring"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSearchOpen(true)}
                className="p-2 text-secondary hover:text-primary transition-colors"
                title="Search"
              >
                <MagnifyingGlassIcon className="w-5 h-5" />
              </button>

              <button
                onClick={() => setHelpOpen(true)}
                className="p-2 text-secondary hover:text-primary transition-colors"
                title="Help & Support"
              >
                <QuestionMarkCircleIcon className="w-5 h-5" />
              </button>

              <button
                onClick={toggleTheme}
                className="p-2 text-secondary hover:text-primary transition-colors"
                title="Toggle Theme"
              >
                {theme === 'dark' ? (
                  <SunIcon className="w-5 h-5" />
                ) : (
                  <MoonIcon className="w-5 h-5" />
                )}
              </button>

              <button 
                className="p-2 text-secondary hover:text-primary transition-colors relative"
                title="Notifications"
              >
                <BellIcon className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>

              <div className="flex items-center space-x-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-primary">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-secondary">
                    {user?.email}
                  </p>
                </div>

                <Link
                  to="/dashboard/settings"
                  className="flex-shrink-0 w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center shadow-default"
                  title="User Settings"
                >
                  <UserCircleIcon className="w-4 h-4 text-white" />
                </Link>

                <button
                  onClick={handleLogout}
                  className="p-2 text-secondary hover:text-primary transition-colors"
                  title="Logout"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            <div className="px-4 sm:px-6 lg:px-8">
              {/* Breadcrumb */}
              <div className="mb-6">
                <Breadcrumb />
              </div>
              
              <Outlet />
            </div>
          </div>
        </main>
      </div>
      
      {/* Global Search Modal */}
      <GlobalSearch 
        isOpen={searchOpen} 
        onClose={() => setSearchOpen(false)} 
      />
      
      {/* Help & Support Modal */}
      <HelpSupportCenter 
        isOpen={helpOpen} 
        onClose={() => setHelpOpen(false)} 
      />
    </div>
  );
};

export default DashboardLayout;