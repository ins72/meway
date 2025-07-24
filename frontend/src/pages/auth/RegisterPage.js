import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
              <span className="gradient-text">Mewayz</span>
            </div>
            <h1 className="branding-title">Join thousands of creators</h1>
            <p className="branding-description">
              Start your journey with the most comprehensive business platform
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
                    <label htmlFor="name" className="form-label">
                      Full Name
                    </label>
                    <div className="input-wrapper">
                      <span className="input-icon">👤</span>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Enter your full name"
                        className="form-input"
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="email" className="form-label">
                      Email Address
                    </label>
                    <div className="input-wrapper">
                      <span className="input-icon">📧</span>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Enter your email"
                        className="form-input"
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="password" className="form-label">
                      Password
                    </label>
                    <div className="input-wrapper">
                      <span className="input-icon">🔒</span>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Create a password"
                        className="form-input"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="password-toggle"
                      >
                        {showPassword ? '👁️' : '👁️‍🗨️'}
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
                    <label htmlFor="confirmPassword" className="form-label">
                      Confirm Password
                    </label>
                    <div className="input-wrapper">
                      <span className="input-icon">🔒</span>
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm your password"
                        className="form-input"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="password-toggle"
                      >
                        {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
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
                    <span className="social-icon">🔍</span>
                    <span className="social-text">Continue with Google</span>
                  </button>
                  <button
                    onClick={handleAppleSignup}
                    className="social-btn apple-btn"
                  >
                    <span className="social-icon">🍎</span>
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