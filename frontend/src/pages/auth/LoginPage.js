import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../contexts/AuthContext';
import { googleAuthAPI } from '../../services/api';
import './AuthPages.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(formData);
      if (result.success) {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (credentialResponse) => {
      try {
        console.log('✅ Google login success:', credentialResponse);
        
        if (!credentialResponse.access_token) {
          throw new Error('No access token received from Google');
        }
        
        // Send token to backend for verification and login
        const response = await googleAuthAPI.verifyToken({
          access_token: credentialResponse.access_token,
          intent: "login"  // Specify this is a login attempt
        });
        
        if (response.data.success) {
          const { user, access_token, message, redirect_to, is_new_user } = response.data;
          
          // Store authentication data
          localStorage.setItem('auth_token', access_token);
          localStorage.setItem('user', JSON.stringify(user));
          
          // Show appropriate success message
          alert(`✅ ${message}\nWelcome ${is_new_user ? 'to MEWAYZ' : 'back'}, ${user.name}!`);
          
          // Navigate based on backend recommendation and onboarding status
          if (redirect_to === "onboarding" || !user.onboarding_completed) {
            navigate('/onboarding');
          } else {
            navigate('/dashboard');
          }
        } else {
          throw new Error(response.data.message || 'Login failed');
        }
        
      } catch (error) {
        console.error('❌ Google login error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Google login failed';
        alert(`❌ Login failed: ${errorMessage}\n\nPlease try again or use email/password login.`);
      }
    },
    onError: (error) => {
      console.error('❌ Google login error:', error);
      alert('❌ Google authentication failed. Please try again.');
    },
    flow: 'implicit',
  });

  const handleAppleLogin = () => {
    console.log('Apple login clicked');
    // TODO: Implement Apple OAuth
  };

  return (
    <div className="auth-page">
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      <div className="auth-container">
        {/* Left Panel - Branding */}
        <div className="auth-branding">
          <div className="branding-content">
            <div className="logo-large">
              <span className="gradient-text">MEWAYZ</span>
            </div>
            <h1 className="branding-title">Welcome back to MEWAYZ</h1>
            <p className="branding-description">
              Access your all-in-one business platform with powerful tools for growth
            </p>
            
            <div className="features-list">
              <div className="feature-item">
                <span className="feature-icon">🚀</span>
                <span className="feature-text">146 Integrated APIs</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🏢</span>
                <span className="feature-text">Multi-workspace support</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span className="feature-text">Real-time analytics</span>
              </div>
            </div>
            
            <div className="testimonial">
              <p className="testimonial-text">
                "Mewayz transformed my business operations completely. The integrated platform saved me hours of work every week."
              </p>
              <div className="testimonial-author">
                <div className="author-avatar">SC</div>
                <div className="author-info">
                  <span className="author-name">Sarah Chen</span>
                  <span className="author-role">Marketing Director</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Form */}
        <div className="auth-form-panel">
          <div className="auth-form-container">
            <div className="form-header">
              <h2 className="form-title">Sign in to your account</h2>
              <p className="form-subtitle">
                Enter your credentials to access your dashboard
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <div className="form-label-container">
                  <div className="label-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2-2-2z"/>
                      <polyline points="22,6 12,13 2,6"/>
                    </svg>
                  </div>
                  <label htmlFor="email" className="form-label">
                    Email Address
                  </label>
                </div>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email"
                  className="form-input-clean"
                  required
                />
              </div>

              <div className="form-group">
                <div className="form-label-container">
                  <div className="label-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <circle cx="12" cy="16" r="1"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                  </div>
                  <label htmlFor="password" className="form-label">
                    Password
                  </label>
                </div>
                <div className="password-input-container">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    className="form-input-clean"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="password-toggle-external"
                  >
                    {showPassword ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary btn-full"
                >
                  {loading ? (
                    <>
                      <div className="loading-spinner"></div>
                      Signing In...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
                
                <Link to="/forgot-password" className="forgot-password-link">
                  Forgot your password?
                </Link>
              </div>
            </form>

            <div className="social-divider">
              <span className="divider-line"></span>
              <span className="divider-text">Or continue with</span>
              <span className="divider-line"></span>
            </div>

            <div className="social-login">
              <button
                onClick={handleGoogleLogin}
                className="social-btn google-btn"
              >
                <div className="social-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                </div>
                <span className="social-text">Continue with Google</span>
              </button>
              <button
                onClick={handleAppleLogin}
                className="social-btn apple-btn"
              >
                <div className="social-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                  </svg>
                </div>
                <span className="social-text">Continue with Apple</span>
              </button>
            </div>

            <div className="form-footer">
              <p className="footer-text">
                Don't have an account?{' '}
                <Link to="/register" className="footer-link">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;