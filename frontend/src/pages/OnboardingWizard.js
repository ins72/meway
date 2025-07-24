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
    primaryGoal: '',
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

  const pricingPlans = [
    {
      id: 'starter',
      name: 'Starter',
      description: 'Perfect for individuals and small projects',
      monthlyPrice: 29,
      yearlyPrice: 290,
      features: [
        'Up to 3 social media accounts',
        '1,000 AI-generated posts per month',
        'Basic analytics dashboard',
        'Email support',
        '5GB storage',
        'Basic templates'
      ],
      limits: {
        socialAccounts: 3,
        aiPosts: 1000,
        storage: '5GB',
        users: 1
      },
      badge: null
    },
    {
      id: 'professional',
      name: 'Professional',
      description: 'Ideal for growing businesses and teams',
      monthlyPrice: 79,
      yearlyPrice: 790,
      features: [
        'Up to 10 social media accounts',
        '5,000 AI-generated posts per month',
        'Advanced analytics & reporting',
        'Priority support',
        '50GB storage',
        'Premium templates',
        'Team collaboration (up to 5 users)',
        'Custom branding'
      ],
      limits: {
        socialAccounts: 10,
        aiPosts: 5000,
        storage: '50GB',
        users: 5
      },
      badge: 'Most Popular'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large organizations with advanced needs',
      monthlyPrice: 199,
      yearlyPrice: 1990,
      features: [
        'Unlimited social media accounts',
        'Unlimited AI-generated posts',
        'Enterprise analytics & insights',
        'Dedicated account manager',
        '500GB storage',
        'White-label solution',
        'Unlimited team members',
        'Advanced integrations',
        'Custom workflows'
      ],
      limits: {
        socialAccounts: 'Unlimited',
        aiPosts: 'Unlimited',
        storage: '500GB',
        users: 'Unlimited'
      },
      badge: 'Best Value'
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

  const primaryGoals = [
    { value: 'social_media', label: 'Social Media Management' },
    { value: 'ecommerce', label: 'E-commerce & Online Sales' },
    { value: 'lead_generation', label: 'Lead Generation' },
    { value: 'content_creation', label: 'Content Creation' },
    { value: 'analytics', label: 'Analytics & Reporting' },
    { value: 'team_collaboration', label: 'Team Collaboration' }
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
    return pricingPlans.find(plan => plan.id === formData.selectedPlan);
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.workspaceName.trim() !== '';
      case 2:
        return formData.industry && formData.teamSize && formData.primaryGoal;
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
                    <label className="form-label">Primary Goal *</label>
                    <div className="goal-options">
                      {primaryGoals.map((goal) => (
                        <label key={goal.value} className="goal-option">
                          <input
                            type="radio"
                            name="primaryGoal"
                            value={goal.value}
                            checked={formData.primaryGoal === goal.value}
                            onChange={handleInputChange}
                            className="goal-radio"
                          />
                          <span className="goal-label">{goal.label}</span>
                        </label>
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
                {pricingPlans.map((plan) => (
                  <div 
                    key={plan.id}
                    onClick={() => handlePlanSelect(plan.id)}
                    className={`pricing-card ${formData.selectedPlan === plan.id ? 'selected' : ''}`}
                  >
                    {plan.badge && (
                      <div className="plan-badge">{plan.badge}</div>
                    )}
                    
                    <div className="plan-header">
                      <h3 className="plan-name">{plan.name}</h3>
                      <p className="plan-description">{plan.description}</p>
                      <div className="plan-price">
                        <span className="price-amount">
                          ${formData.paymentMethod === 'monthly' ? plan.monthlyPrice : Math.floor(plan.yearlyPrice / 12)}
                        </span>
                        <span className="price-period">
                          /{formData.paymentMethod === 'monthly' ? 'month' : 'month (billed yearly)'}
                        </span>
                      </div>
                      {formData.paymentMethod === 'yearly' && (
                        <div className="yearly-savings">
                          Save ${(plan.monthlyPrice * 12) - plan.yearlyPrice} per year
                        </div>
                      )}
                    </div>

                    <div className="plan-features">
                      <h4>What's included:</h4>
                      <ul className="features-list">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="feature-item">
                            <span className="feature-check">✓</span>
                            <span className="feature-text">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="plan-limits">
                      <div className="limits-grid">
                        <div className="limit-item">
                          <span className="limit-label">Social Accounts</span>
                          <span className="limit-value">{plan.limits.socialAccounts}</span>
                        </div>
                        <div className="limit-item">
                          <span className="limit-label">AI Posts</span>
                          <span className="limit-value">{plan.limits.aiPosts}</span>
                        </div>
                        <div className="limit-item">
                          <span className="limit-label">Storage</span>
                          <span className="limit-value">{plan.limits.storage}</span>
                        </div>
                        <div className="limit-item">
                          <span className="limit-label">Team Members</span>
                          <span className="limit-value">{plan.limits.users}</span>
                        </div>
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