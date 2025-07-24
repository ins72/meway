import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { useTheme } from './contexts/ThemeContext';
import { useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Public pages
import LandingPage from './pages/LandingPage';
import MEWAYZ_V2_LandingPage from './pages/MEWAYZ_V2_LandingPage.jsx';
import AboutPage from './pages/AboutPage';
import ContactUsPage from './pages/ContactUsPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import OnboardingWizard from './pages/OnboardingWizard';
import NotFoundPage from './pages/NotFoundPage';

// Legal pages
import TermsOfServicePage from './pages/legal/TermsOfServicePage';
import PrivacyPolicyPage from './pages/legal/PrivacyPolicyPage';
import CookiePolicyPage from './pages/legal/CookiePolicyPage';

// Protected pages
import DashboardLayout from './layouts/DashboardLayout';
import DashboardHome from './pages/dashboard/DashboardHome';
import SocialMediaPage from './pages/dashboard/SocialMediaPage';
import InstagramManagementPage from './pages/dashboard/InstagramManagementPage';
import EcommercePage from './pages/dashboard/EcommercePage';
import CoursesPage from './pages/dashboard/CoursesPage';
import CRMPage from './pages/dashboard/CRMPage';
import AnalyticsPage from './pages/dashboard/AnalyticsPage';
import BioSitesPage from './pages/dashboard/BioSitesPage';
import EmailMarketingPage from './pages/dashboard/EmailMarketingPage';
import PaymentsPage from './pages/dashboard/PaymentsPage';
import AIFeaturesPageV2 from './pages/dashboard/AIFeaturesPageV2';
import WorkspacePage from './pages/dashboard/WorkspacePage';
import WebsiteBuilderPage from './pages/dashboard/WebsiteBuilderPage';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import AdvancedBookingPage from './pages/dashboard/AdvancedBookingPage';
import FinancialManagementPage from './pages/dashboard/FinancialManagementPage';
import EscrowSystemPage from './pages/dashboard/EscrowSystemPage';
import RealtimeCollaborationPage from './pages/dashboard/RealtimeCollaborationPage';
import IntegrationHubPage from './pages/dashboard/IntegrationHubPage';
import ReferralSystemPage from './pages/dashboard/ReferralSystemPage';
import UserSettingsPage from './pages/dashboard/UserSettingsPage';
import TemplateMarketplaceV2Page from './pages/dashboard/TemplateMarketplaceV2Page';
import EnhancedTemplateMarketplace from './pages/dashboard/EnhancedTemplateMarketplace';
import GamifiedAnalyticsPage from './pages/dashboard/GamifiedAnalyticsPage';
import SimpleAdminDashboard from './pages/dashboard/SimpleAdminDashboard';
import AdvancedAdminDashboard from './pages/dashboard/AdvancedAdminDashboard';
import ComprehensiveAdminDashboard from './pages/dashboard/ComprehensiveAdminDashboard';
import AdvancedLinkInBioBuilder from './pages/dashboard/AdvancedLinkInBioBuilder';
import ProfessionalCourseBuilder from './pages/dashboard/ProfessionalCourseBuilder';
import EnhancedSocialMediaManager from './pages/dashboard/EnhancedSocialMediaManager';
import InstagramDatabasePage from './pages/dashboard/InstagramDatabasePage';
import AdvancedWebsiteBuilder from './pages/dashboard/AdvancedWebsiteBuilder';
import ComprehensiveBookingSystem from './pages/dashboard/ComprehensiveBookingSystem';

// New enhanced pages
import UltraAdvancedAIFeaturesPage from './pages/dashboard/UltraAdvancedAIFeaturesPage';
import UltraAdvancedWorkspaceManagement from './pages/dashboard/UltraAdvancedWorkspaceManagement';
import UltraAdvancedSubscriptionManager from './pages/dashboard/UltraAdvancedSubscriptionManager';
import UltraAdvancedInstagramManager from './pages/dashboard/UltraAdvancedInstagramManager';
import UltraAdvancedSocialMediaScheduler from './pages/dashboard/UltraAdvancedSocialMediaScheduler';

// Professional comprehensive pages
import ProfessionalLinkInBioBuilder from './pages/dashboard/ProfessionalLinkInBioBuilder';
import ComprehensiveMarketplace from './pages/dashboard/ComprehensiveMarketplace';
import ProfessionalBookingSystem from './pages/dashboard/ProfessionalBookingSystem';
import AdvancedWorkspaceSettings from './pages/dashboard/AdvancedWorkspaceSettings';
import ProfessionalOnboardingWizard from './pages/onboarding/ProfessionalOnboardingWizard';
import UltraAdvancedAdminDashboard from './pages/dashboard/UltraAdvancedAdminDashboard';
import ComprehensiveCRMSystem from './pages/dashboard/ComprehensiveCRMSystem';
import ComprehensiveCoursesSystem from './pages/dashboard/ComprehensiveCoursesSystem';
import AmazonStyleMarketplace from './pages/dashboard/AmazonStyleMarketplace';

// New pages
import LinkShortenerPage from './pages/dashboard/LinkShortenerPage';
import TeamManagementPage from './pages/dashboard/TeamManagementPage';
import FormTemplatesPage from './pages/dashboard/FormTemplatesPage';
import DiscountCodesPage from './pages/dashboard/DiscountCodesPage';
import TokenManagementPage from './pages/dashboard/TokenManagementPage';
import InstagramLeadGeneration from './pages/dashboard/InstagramLeadGeneration';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import LoadingSpinner from './components/LoadingSpinner';
import AdvancedAIFeatures from './components/ai/AdvancedAIFeatures';
import WorkspaceManager from './components/workspace/WorkspaceManager';
import SubscriptionManager from './components/subscription/SubscriptionManager';
import TemplateMarketplace from './components/templates/TemplateMarketplace';
import AdvancedAnalytics from './components/analytics/AdvancedAnalytics';
import RealtimeCollaboration from './components/realtime/RealtimeCollaboration';
import IntegrationHub from './components/integrations/IntegrationHub';
import ReferralSystem from './components/growth/ReferralSystem';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const { theme } = useTheme();
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-app flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      <div className={theme} data-theme={theme}>
        <ErrorBoundary>
          <NotificationProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<MEWAYZ_V2_LandingPage />} />
            <Route path="/legacy-landing" element={<LandingPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactUsPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/onboarding" element={<ProfessionalOnboardingWizard />} />
            
            {/* Legal Pages */}
            <Route path="/terms-of-service" element={<TermsOfServicePage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="/cookie-policy" element={<CookiePolicyPage />} />
            
            {/* Protected Dashboard Routes */}
            <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              <Route index element={<DashboardHome />} />
              <Route path="social-media" element={<UltraAdvancedSocialMediaScheduler />} />
              <Route path="instagram" element={<UltraAdvancedInstagramManager />} />
              <Route path="instagram-leads" element={<InstagramLeadGeneration />} />
              <Route path="bio-sites" element={<ProfessionalLinkInBioBuilder />} />
              <Route path="crm" element={<ComprehensiveCRMSystem />} />
              <Route path="workspace-settings" element={<AdvancedWorkspaceSettings />} />
              <Route path="link-shortener" element={<LinkShortenerPage />} />
              <Route path="referrals" element={<ReferralSystemPage />} />
              
              <Route path="website-builder" element={<WebsiteBuilderPage />} />
              <Route path="team-management" element={<TeamManagementPage />} />
              <Route path="form-templates" element={<FormTemplatesPage />} />
              <Route path="discount-codes" element={<DiscountCodesPage />} />
              <Route path="token-management" element={<TokenManagementPage />} />
              <Route path="financial-management" element={<FinancialManagementPage />} />
              
              <Route path="courses" element={<CoursesPage />} />
              <Route path="ecommerce" element={<ComprehensiveMarketplace />} />
              <Route path="templates" element={<TemplateMarketplace />} />
              <Route path="template-marketplace" element={<TemplateMarketplaceV2Page />} />
              <Route path="escrow-system" element={<EscrowSystemPage />} />
              <Route path="analytics" element={<AdvancedAnalytics />} />
              <Route path="gamified-analytics" element={<GamifiedAnalyticsPage />} />
              
              <Route path="ai-features" element={<UltraAdvancedAIFeaturesPage />} />
              <Route path="email-marketing" element={<EmailMarketingPage />} />
              <Route path="advanced-booking" element={<ProfessionalBookingSystem />} />
              <Route path="realtime-collaboration" element={<RealtimeCollaborationPage />} />
              <Route path="integrations" element={<IntegrationHubPage />} />
              <Route path="workspaces" element={<UltraAdvancedWorkspaceManagement />} />
              <Route path="subscription" element={<UltraAdvancedSubscriptionManager />} />
              <Route path="settings" element={<UserSettingsPage />} />
              
              {/* Legacy routes for backward compatibility */}
              <Route path="workspace" element={<WorkspacePage />} />
              <Route path="payments" element={<PaymentsPage />} />
              <Route path="advanced-analytics" element={<AnalyticsPage />} />
              
              {/* Admin Routes */}
              <Route path="admin" element={<UltraAdvancedAdminDashboard />} />
              <Route path="admin/comprehensive" element={<ComprehensiveAdminDashboard />} />
              <Route path="admin/simple" element={<SimpleAdminDashboard />} />
              <Route path="admin/users" element={<div className="p-8 text-center">User management coming soon...</div>} />
              <Route path="admin/system" element={<div className="p-8 text-center">System settings coming soon...</div>} />
              
              {/* Enhanced Template Marketplace */}
              <Route path="marketplace" element={<EnhancedTemplateMarketplace />} />
              <Route path="marketplace/enhanced" element={<EnhancedTemplateMarketplace />} />
              
              {/* Advanced Builders */}
              <Route path="bio-builder" element={<AdvancedLinkInBioBuilder />} />
              <Route path="course-builder" element={<ProfessionalCourseBuilder />} />
              <Route path="social-enhanced" element={<EnhancedSocialMediaManager />} />
              <Route path="admin/security" element={<div className="p-8 text-center">Security center coming soon...</div>} />
            </Route>

            {/* 404 Page */}
            <Route path="/404" element={<NotFoundPage />} />
            
            {/* Catch all - redirect to 404 */}
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </NotificationProvider>
      </ErrorBoundary>
    </div>
    </GoogleOAuthProvider>
  );
}

export default App;