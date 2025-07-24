import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './OnboardingWizard.css';

const OnboardingWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    workspaceName: '',
    industry: '',
    teamSize: '',
    selectedGoals: [], // Changed to support multiple goals
    selectedPlan: null,
    paymentMethod: 'monthly'
  });
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const steps = [
    { id: 1, title: 'Workspace Setup', description: 'Set up your workspace' },
    { id: 2, title: 'Business Details', description: 'Tell us about your business' },
    { id: 3, title: 'Choose Your Plan', description: 'Select the perfect plan' },
    { id: 4, title: 'Complete Setup', description: 'Finalize your workspace' }
  ];

  const pricingBundles = [
    {
      id: 'free',
      name: 'Free Starter',
      description: 'Perfect for testing the platform, personal use',
      monthlyPrice: 0,
      yearlyPrice: 0,
      features: [
        '1 Bio Link Page (with 5 external links)',
        'Basic Form Builder (1 form, 50 submissions/month)',
        'Simple Analytics (7 days data retention)',
        'Template Marketplace: Buy templates only',
        'Community support only'
      ],
      limits: {
        bioLinks: 1,
        forms: 1,
        submissions: 50,
        analytics: '7 days',
        branding: 'Mewayz Required'
      },
      badge: null,
      launchSpecial: null
    },
    {
      id: 'creator',
      name: 'Creator Bundle',
      description: 'Advanced Bio Link Builder, Website Builder, AI Content Creation',
      monthlyPrice: 19,
      yearlyPrice: 190,
      features: [
        'Advanced Bio Link Builder (unlimited links, custom domain)',
        'Professional Website Builder (10 pages, custom domain)',
        'SEO Optimization Suite (basic SEO tools)',
        'AI Content Creation (500 credits/month)',
        'Template Marketplace: Buy & sell templates',
        'Remove Mewayz Branding',
        'Email Support'
      ],
      limits: {
        bioLinks: 'Unlimited',
        websitePages: 10,
        aiCredits: 500,
        customDomain: true,
        templateSelling: true
      },
      badge: null,
      launchSpecial: 'First 1000 users get 3 months for $9/month'
    },
    {
      id: 'ecommerce',
      name: 'E-commerce Bundle',
      description: 'Complete E-commerce Store, Multi-vendor Marketplace',
      monthlyPrice: 24,
      yearlyPrice: 240,
      features: [
        'Complete E-commerce Store (unlimited products)',
        'Multi-vendor Marketplace (up to 10 vendors)',
        'Advanced Promotions (coupons, discounts, referrals)',
        'Payment Processing (Stripe/PayPal integration)',
        'Inventory Management',
        'Basic Analytics',
        'Priority Email Support'
      ],
      limits: {
        products: 'Unlimited',
        vendors: 10,
        promotions: true,
        paymentProcessing: true,
        analytics: 'Basic'
      },
      badge: null,
      launchSpecial: 'First 500 users get 2 months free'
    },
    {
      id: 'social_media',
      name: 'Social Media Bundle',
      description: 'Instagram Lead Database, Social Media Management',
      monthlyPrice: 29,
      yearlyPrice: 290,
      features: [
        'Instagram Lead Database (1000 searches/month)',
        'Social Media Scheduling (all major platforms)',
        'Twitter/TikTok Tools (advanced features)',
        'Social Analytics (detailed insights)',
        'Hashtag Research (trending hashtags)',
        'Priority Support'
      ],
      limits: {
        instagramSearches: 1000,
        platforms: 'All Major',
        socialAnalytics: 'Detailed',
        hashtagResearch: true
      },
      badge: null,
      launchSpecial: 'First 2 weeks free trial'
    },
    {
      id: 'education',
      name: 'Education Bundle',
      description: 'Complete Course Platform, Student Management',
      monthlyPrice: 29,
      yearlyPrice: 290,
      features: [
        'Complete Course Platform (unlimited students)',
        'Template Marketplace (create & sell course templates)',
        'Student Management (progress tracking, certificates)',
        'Live Streaming (basic streaming capabilities)',
        'Community Features (student discussions)',
        'Priority Support'
      ],
      limits: {
        students: 'Unlimited',
        courses: 'Unlimited',
        liveStreaming: 'Basic',
        community: true,
        certificates: true
      },
      badge: null,
      launchSpecial: 'First month free'
    },
    {
      id: 'business',
      name: 'Business Bundle',
      description: 'Advanced CRM System, Email Marketing, Lead Management',
      monthlyPrice: 39,
      yearlyPrice: 390,
      features: [
        'Advanced CRM System (unlimited contacts)',
        'Email Marketing (10,000 emails/month)',
        'Lead Management (advanced scoring & tracking)',
        'Workflow Automation (10 workflows)',
        'Campaign Management (multi-channel campaigns)',
        'Business Analytics (detailed reporting)',
        'Phone + Email Support'
      ],
      limits: {
        contacts: 'Unlimited',
        emails: 10000,
        workflows: 10,
        campaigns: 'Multi-channel',
        analytics: 'Business'
      },
      badge: 'Most Popular',
      launchSpecial: '50% off first 3 months'
    },
    {
      id: 'operations',
      name: 'Operations Bundle',
      description: 'Booking & Appointments, Financial Management',
      monthlyPrice: 24,
      yearlyPrice: 240,
      features: [
        'Booking & Appointments (unlimited bookings)',
        'Financial Management (invoicing, expenses)',
        'Advanced Form Builder (unlimited forms)',
        'Survey & Feedback Tools (advanced surveys)',
        'Basic Reporting',
        'Email Support'
      ],
      limits: {
        bookings: 'Unlimited',
        invoicing: true,
        forms: 'Unlimited',
        surveys: 'Advanced',
        reporting: 'Basic'
      },
      badge: null,
      launchSpecial: 'First month free'
    }
  ];

  const industries = [
    { value: 'technology', label: 'Technology & Software' },
    { value: 'marketing', label: 'Marketing & Advertising' },
    { value: 'ecommerce', label: 'E-commerce & Retail' },
    { value: 'education', label: 'Education & Training' },
    { value: 'healthcare', label: 'Healthcare & Wellness' },
    { value: 'finance', label: 'Finance & Insurance' },
    { value: 'realestate', label: 'Real Estate' },
    { value: 'consulting', label: 'Consulting & Services' },
    { value: 'nonprofit', label: 'Non-Profit' },
    { value: 'other', label: 'Other' }
  ];

  const teamSizes = [
    { value: 'solo', label: 'Just me' },
    { value: 'small', label: '2-10 people' },
    { value: 'medium', label: '11-50 people' },
    { value: 'large', label: '51-200 people' },
    { value: 'enterprise', label: '200+ people' }
  ];

  const businessGoals = [
    {
      id: 'social_media',
      title: 'Social Media Growth',
      description: 'Grow followers, engagement, and leads',
      icon: '👥',
      gradient: 'var(--gradient-primary)',
      features_preview: ['Instagram database', 'Content scheduling', 'Analytics']
    },
    {
      id: 'ecommerce',
      title: 'E-commerce Sales', 
      description: 'Sell products and manage inventory',
      icon: '🛒',
      gradient: 'var(--gradient-accent)',
      features_preview: ['Online store', 'Payment processing', 'Order management']
    },
    {
      id: 'content_creation',
      title: 'Content & Courses',
      description: 'Create and monetize educational content',
      icon: '🎥',
      gradient: 'var(--gradient-warm)',
      features_preview: ['Course builder', 'Student management', 'Content library']
    },
    {
      id: 'client_management',
      title: 'Client & CRM',
      description: 'Manage relationships and sales pipeline',
      icon: '🤝',
      gradient: 'var(--gradient-secondary)',
      features_preview: ['Contact management', 'Pipeline tracking', 'Task automation']
    },
    {
      id: 'marketing',
      title: 'Marketing Campaigns',
      description: 'Email, ads, and campaign management',
      icon: '📢',
      gradient: 'var(--gradient-cool)',
      features_preview: ['Email marketing', 'Campaign tracking', 'Lead generation']
    },
    {
      id: 'analytics',
      title: 'Business Analytics',
      description: 'Track performance and make data-driven decisions',
      icon: '📊',
      gradient: 'var(--gradient-primary)',
      features_preview: ['Revenue tracking', 'Performance metrics', 'Custom reports']
    }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handlePlanSelect = (planId) => {
    setFormData({
      ...formData,
      selectedPlan: planId
    });
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      // TODO: Submit onboarding data to backend
      console.log('Onboarding data:', formData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Onboarding error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSelectedPlan = () => {
    return pricingBundles.find(bundle => bundle.id === formData.selectedPlan);
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.workspaceName.trim() !== '';
      case 2:
        return formData.industry && formData.teamSize && formData.selectedGoals.length > 0;
      case 3:
        return formData.selectedPlan !== null;
      default:
        return true;
    }
  };

  return (
    <div className="onboarding-wizard">
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      <div className="wizard-container">
        {/* Header */}
        <div className="wizard-header">
          <div className="logo">
            <span className="gradient-text">Mewayz</span>
          </div>
          <div className="progress-info">
            <h1 className="wizard-title">Welcome to Mewayz</h1>
            <p className="wizard-subtitle">
              Let's set up your workspace in just a few steps
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(currentStep / steps.length) * 100}%` }}
            ></div>
          </div>
          <div className="progress-steps">
            {steps.map((step) => (
              <div 
                key={step.id} 
                className={`progress-step ${currentStep >= step.id ? 'completed' : ''}`}
              >
                <div className="step-circle">
                  {currentStep > step.id ? (
                    <span className="step-check">✓</span>
                  ) : (
                    <span className="step-number">{step.id}</span>
                  )}
                </div>
                <div className="step-info">
                  <span className="step-title">{step.title}</span>
                  <span className="step-description">{step.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="wizard-content">
          {currentStep === 1 && (
            <div className="step-content">
              <div className="step-header">
                <h2>Set Up Your Workspace</h2>
                <p>Give your workspace a name that represents your brand or business</p>
              </div>
              <div className="form-section">
                <div className="form-group">
                  <label className="form-label">Workspace Name *</label>
                  <input
                    type="text"
                    name="workspaceName"
                    value={formData.workspaceName}
                    onChange={handleInputChange}
                    placeholder="Enter your workspace name"
                    className="form-input"
                  />
                  <span className="form-hint">
                    This will be displayed across your dashboard and can be changed later
                  </span>
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="step-content">
              <div className="step-header">
                <h2>Tell Us About Your Business</h2>
                <p>Help us personalize your experience with relevant features and recommendations</p>
              </div>
              <div className="form-section">
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Industry *</label>
                    <select
                      name="industry"
                      value={formData.industry}
                      onChange={handleInputChange}
                      className="form-input"
                    >
                      <option value="">Select your industry</option>
                      {industries.map((industry) => (
                        <option key={industry.value} value={industry.value}>
                          {industry.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Team Size *</label>
                    <select
                      name="teamSize"
                      value={formData.teamSize}
                      onChange={handleInputChange}
                      className="form-input"
                    >
                      <option value="">Select team size</option>
                      {teamSizes.map((size) => (
                        <option key={size.value} value={size.value}>
                          {size.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group full-width">
                    <label className="form-label">Business Goals *</label>
                    <p className="form-hint">Select all that apply - we'll customize your experience</p>
                    <div className="business-goals-grid">
                      {businessGoals.map((goal) => (
                        <div 
                          key={goal.id} 
                          className={`goal-card ${formData.selectedGoals.includes(goal.id) ? 'selected' : ''}`}
                          onClick={() => {
                            const newGoals = formData.selectedGoals.includes(goal.id)
                              ? formData.selectedGoals.filter(g => g !== goal.id)
                              : [...formData.selectedGoals, goal.id];
                            setFormData({...formData, selectedGoals: newGoals});
                          }}
                        >
                          <div className="goal-icon">{goal.icon}</div>
                          <div className="goal-content">
                            <h4 className="goal-title">{goal.title}</h4>
                            <p className="goal-description">{goal.description}</p>
                            <div className="goal-features">
                              {goal.features_preview.map((feature, index) => (
                                <span key={index} className="goal-feature">{feature}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="step-content">
              <div className="step-header">
                <h2>Choose Your Plan</h2>
                <p>Select the plan that best fits your needs. You can upgrade or downgrade anytime.</p>
                
                <div className="billing-toggle">
                  <span className={`billing-option ${formData.paymentMethod === 'monthly' ? 'active' : ''}`}>
                    Monthly
                  </span>
                  <button
                    onClick={() => setFormData({...formData, paymentMethod: formData.paymentMethod === 'monthly' ? 'yearly' : 'monthly'})}
                    className="toggle-switch"
                  >
                    <div className={`toggle-slider ${formData.paymentMethod === 'yearly' ? 'active' : ''}`}></div>
                  </button>
                  <span className={`billing-option ${formData.paymentMethod === 'yearly' ? 'active' : ''}`}>
                    Yearly <span className="savings-badge">Save 17%</span>
                  </span>
                </div>
              </div>

              <div className="pricing-plans">
                {pricingBundles.map((bundle) => (
                  <div 
                    key={bundle.id}
                    onClick={() => handlePlanSelect(bundle.id)}
                    className={`pricing-card ${formData.selectedPlan === bundle.id ? 'selected' : ''}`}
                  >
                    {bundle.badge && (
                      <div className="plan-badge">{bundle.badge}</div>
                    )}
                    
                    <div className="plan-header">
                      <h3 className="plan-name">{bundle.name}</h3>
                      <p className="plan-description">{bundle.description}</p>
                      <div className="plan-price">
                        <span className="price-amount">
                          ${formData.paymentMethod === 'monthly' ? bundle.monthlyPrice : Math.floor(bundle.yearlyPrice / 12)}
                        </span>
                        <span className="price-period">
                          /{formData.paymentMethod === 'monthly' ? 'month' : 'month (billed yearly)'}
                        </span>
                      </div>
                      {formData.paymentMethod === 'yearly' && bundle.yearlyPrice > 0 && (
                        <div className="yearly-savings">
                          Save ${(bundle.monthlyPrice * 12) - bundle.yearlyPrice} per year
                        </div>
                      )}
                      {bundle.launchSpecial && (
                        <div className="launch-special">
                          🚀 Launch Special: {bundle.launchSpecial}
                        </div>
                      )}
                    </div>

                    <div className="plan-features">
                      <h4>What's included:</h4>
                      <ul className="features-list">
                        {bundle.features.map((feature, index) => (
                          <li key={index} className="feature-item">
                            <span className="feature-check">✓</span>
                            <span className="feature-text">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="plan-limits">
                      <div className="limits-grid">
                        {Object.entries(bundle.limits).map(([key, value]) => (
                          <div key={key} className="limit-item">
                            <span className="limit-label">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</span>
                            <span className="limit-value">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="step-content">
              <div className="step-header">
                <h2>Complete Your Setup</h2>
                <p>Review your selections and complete your workspace setup</p>
              </div>

              <div className="setup-summary">
                <div className="summary-section">
                  <h3>Workspace Details</h3>
                  <div className="summary-item">
                    <span className="summary-label">Name:</span>
                    <span className="summary-value">{formData.workspaceName}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Industry:</span>
                    <span className="summary-value">
                      {industries.find(i => i.value === formData.industry)?.label}
                    </span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Team Size:</span>
                    <span className="summary-value">
                      {teamSizes.find(s => s.value === formData.teamSize)?.label}
                    </span>
                  </div>
                </div>

                {formData.selectedPlan && (
                  <div className="summary-section">
                    <h3>Selected Plan</h3>
                    <div className="selected-plan-summary">
                      <div className="plan-summary-header">
                        <span className="plan-summary-name">{getSelectedPlan().name}</span>
                        <span className="plan-summary-price">
                          ${formData.paymentMethod === 'monthly' 
                            ? getSelectedPlan().monthlyPrice 
                            : Math.floor(getSelectedPlan().yearlyPrice / 12)
                          }/month
                        </span>
                      </div>
                      <p className="plan-summary-billing">
                        Billed {formData.paymentMethod === 'monthly' ? 'monthly' : 'yearly'}
                        {formData.paymentMethod === 'yearly' && ' (17% savings)'}
                      </p>
                    </div>
                  </div>
                )}

                <div className="setup-actions">
                  <div className="trial-info">
                    <h4>14-Day Free Trial</h4>
                    <p>Start your free trial today. No credit card required.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="wizard-navigation">
          <div className="nav-left">
            {currentStep > 1 && (
              <button onClick={handleBack} className="btn btn-secondary">
                Back
              </button>
            )}
          </div>
          <div className="nav-right">
            {currentStep < steps.length ? (
              <button 
                onClick={handleNext} 
                disabled={!canProceed()}
                className="btn btn-primary"
              >
                Continue
              </button>
            ) : (
              <button 
                onClick={handleComplete}
                disabled={loading || !canProceed()}
                className="btn btn-primary"
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Setting up workspace...
                  </>
                ) : (
                  'Complete Setup'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;