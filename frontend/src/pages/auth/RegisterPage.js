import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../contexts/AuthContext';
import './AuthPages.css';

const RegisterPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Calculate password strength
    if (name === 'password') {
      calculatePasswordStrength(value);
    }
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    setPasswordStrength(strength);
  };

  const getPasswordStrengthText = (strength) => {
    switch (strength) {
      case 0:
      case 1: return { text: 'Weak', color: '#ef4444' };
      case 2:
      case 3: return { text: 'Medium', color: '#f97316' };
      case 4:
      case 5: return { text: 'Strong', color: '#22c55e' };
      default: return { text: 'Weak', color: '#ef4444' };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        name: formData.name,
        email: formData.email,
        password: formData.password
      });
      
      if (result.success) {
        setCurrentStep(2); // Move to verification step
      }
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignup = () => {
    console.log('Google signup clicked');
    // TODO: Implement Google OAuth
  };

  const handleAppleSignup = () => {
    console.log('Apple signup clicked');
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
            <h1 className="branding-title">Join thousands of creators</h1>
            <p className="branding-description">
              Start building your online empire with MEWAYZ
            </p>
            
            <div className="features-list">
              <div className="feature-item">
                <span className="feature-icon">⚡</span>
                <span className="feature-text">14-day free trial</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🚀</span>
                <span className="feature-text">All features included</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📞</span>
                <span className="feature-text">24/7 support</span>
              </div>
            </div>
            
            <div className="success-stats">
              <div className="stat-item">
                <span className="stat-number">10K+</span>
                <span className="stat-label">Active Users</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">$2.5M+</span>
                <span className="stat-label">Revenue Generated</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">99.9%</span>
                <span className="stat-label">Uptime</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Form */}
        <div className="auth-form-panel">
          <div className="auth-form-container">
            {currentStep === 1 && (
              <>
                <div className="form-header">
                  <h2 className="form-title">Create your account</h2>
                  <p className="form-subtitle">
                    Get started with your free trial today
                  </p>
                  <div className="progress-indicator">
                    <span className="progress-text">Step 1 of 3</span>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: '33%' }}></div>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                  <div className="form-group">
                    <div className="form-label-container">
                      <div className="label-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                          <circle cx="12" cy="7" r="4"/>
                        </svg>
                      </div>
                      <label htmlFor="name" className="form-label">
                        Full Name
                      </label>
                    </div>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Enter your full name"
                      className="form-input-clean"
                      required
                    />
                  </div>

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
                        placeholder="Create a password"
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
                    {formData.password && (
                      <div className="password-strength">
                        <div className="strength-bar">
                          <div 
                            className="strength-fill" 
                            style={{ 
                              width: `${(passwordStrength / 5) * 100}%`,
                              backgroundColor: getPasswordStrengthText(passwordStrength).color
                            }}
                          ></div>
                        </div>
                        <span 
                          className="strength-text"
                          style={{ color: getPasswordStrengthText(passwordStrength).color }}
                        >
                          {getPasswordStrengthText(passwordStrength).text}
                        </span>
                      </div>
                    )}
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
                      <label htmlFor="confirmPassword" className="form-label">
                        Confirm Password
                      </label>
                    </div>
                    <div className="password-input-container">
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm your password"
                        className="form-input-clean"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="password-toggle-external"
                      >
                        {showConfirmPassword ? (
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
                          Creating Account...
                        </>
                      ) : (
                        'Create Account'
                      )}
                    </button>
                  </div>
                </form>

                <div className="social-divider">
                  <span className="divider-line"></span>
                  <span className="divider-text">Or sign up with</span>
                  <span className="divider-line"></span>
                </div>

                <div className="social-login">
                  <button
                    onClick={handleGoogleSignup}
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
                    onClick={handleAppleSignup}
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
                    Already have an account?{' '}
                    <Link to="/login" className="footer-link">
                      Sign in
                    </Link>
                  </p>
                </div>
              </>
            )}

            {currentStep === 2 && (
              <div className="verification-step">
                <div className="verification-content">
                  <div className="success-icon">✅</div>
                  <h2 className="verification-title">Account Created Successfully!</h2>
                  <p className="verification-description">
                    Welcome to Mewayz! Your account has been created and you're ready to start building your business.
                  </p>
                  <button 
                    onClick={() => navigate('/onboarding')}
                    className="btn btn-primary btn-full"
                  >
                    Continue to Workspace Setup
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;