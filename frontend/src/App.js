import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useTheme } from './contexts/ThemeContext';
import { useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Initialize Stripe with LIVE keys
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Global Styles
import './styles/globals.css';

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
import AppShell from './layouts/AppShell';
import DashboardHome from './pages/dashboard/DashboardHome';
import SocialMediaPage from './pages/dashboard/SocialMediaPage';
import EcommercePage from './pages/dashboard/EcommercePage';
import SettingsPage from './pages/dashboard/SettingsPage';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const { theme } = useTheme();
  const { loading } = useAuth();

  console.log('App: loading state:', loading);

  if (loading) {
    console.log('App: Showing loading spinner');
    return (
      <div className="min-h-screen bg-app flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  console.log('App: Rendering main app');

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
            <Route path="/onboarding" element={
              <Elements stripe={stripePromise}>
                <OnboardingWizard />
              </Elements>
            } />
            
            {/* Legal Pages */}
            <Route path="/terms-of-service" element={<TermsOfServicePage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="/cookie-policy" element={<CookiePolicyPage />} />
            
            {/* Protected Dashboard Routes */}
            <Route path="/dashboard" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
              <Route index element={<DashboardHome />} />
              <Route path="social-media" element={<SocialMediaPage />} />
              <Route path="ecommerce" element={<EcommercePage />} />
              <Route path="settings" element={<SettingsPage />} />
              
              {/* Temporary placeholder routes - will be rebuilt */}
              <Route path="*" element={<div className="p-8 text-center">
                <h2 className="text-2xl font-bold mb-4">🚧 Under Construction</h2>
                <p>This feature is being rebuilt with our new design system. Coming soon!</p>
              </div>} />
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