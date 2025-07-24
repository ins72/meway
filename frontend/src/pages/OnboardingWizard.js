import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { onboardingAPI, adminSettingsAPI } from '../services/api';
import './OnboardingWizard.css';

const OnboardingWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    workspaceName: '',
    industry: '',
    teamSize: '',
    selectedGoals: [], // Changed to support multiple goals
    selectedBundles: [], // Changed to support multiple bundles
    paymentMethod: 'monthly',
    selectedPaymentType: null // Add payment type selection (credit_card, paypal)
  });
  const [loading, setLoading] = useState(false);
  const [paymentSettings, setPaymentSettings] = useState({
    paypal_enabled: false,
    credit_card_enabled: true,
    stripe_enabled: true
  });
  const { user } = useAuth();
  const navigate = useNavigate();

  // Fetch payment settings and onboarding progress on component mount
  useEffect(() => {
    const fetchPaymentSettings = async () => {
      try {
        const response = await adminSettingsAPI.getPaymentMethods();
        if (response.data.success) {
          setPaymentSettings(response.data.data);
        }
      } catch (error) {
        console.error('Failed to fetch payment settings:', error);
        // Use default settings on error
      }
    };
    
    const fetchOnboardingProgress = async () => {
      try {
        const response = await onboardingAPI.getProgress();
        if (response.data.success) {
          const progress = response.data.data;
          // Set current step based on saved progress
          setCurrentStep(progress.step);
          // Restore any saved data
          if (progress.data) {
            setFormData(prevData => ({
              ...prevData,
              ...progress.data
            }));
          }
        }
      } catch (error) {
        console.error('Failed to fetch onboarding progress:', error);
        // Continue with default step 1
      }
    };
    
    fetchPaymentSettings();
    if (user) {
      fetchOnboardingProgress();
    }
  }, [user]);

  const steps = [
    { id: 1, title: 'Workspace Setup', description: 'Set up your workspace' },
    { id: 2, title: 'Business Details', description: 'Tell us about your business' },
    { id: 3, title: 'Choose Bundles', description: 'Select your features' },
    { id: 4, title: 'Payment Setup', description: 'Complete subscription' },
    { id: 5, title: 'Complete Setup', description: 'Finalize your workspace' }
  ];

  // Bundle-to-goal mapping for filtering
  const bundleGoalMapping = {
    'free': ['social_media', 'ecommerce', 'content_creation', 'client_management', 'marketing', 'analytics'], // Free plan supports all goals at basic level
    'creator': ['content_creation', 'social_media', 'marketing'], // Bio links, website building, content creation
    'ecommerce': ['ecommerce', 'marketing', 'analytics'], // E-commerce focused
    'social_media': ['social_media', 'marketing', 'analytics'], // Social media focused  
    'education': ['content_creation', 'analytics', 'client_management'], // Course platform focused
    'business': ['client_management', 'marketing', 'analytics'], // CRM and business focused
    'operations': ['client_management', 'analytics', 'ecommerce'] // Booking and operations focused
  };

  // Get filtered bundles based on selected goals
  const getFilteredBundles = () => {
    if (formData.selectedGoals.length === 0) {
      return pricingBundles; // Show all bundles if no goals selected
    }
    
    return pricingBundles.filter(bundle => {
      const bundleGoals = bundleGoalMapping[bundle.id] || [];
      return formData.selectedGoals.some(goal => bundleGoals.includes(goal));
    });
  };

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

  const handleBundleSelect = (bundleId) => {
    const newBundles = formData.selectedBundles.includes(bundleId)
      ? formData.selectedBundles.filter(b => b !== bundleId)
      : [...formData.selectedBundles, bundleId];
    setFormData({
      ...formData,
      selectedBundles: newBundles
    });
  };

  const calculateBundleDiscount = () => {
    const bundleCount = formData.selectedBundles.length;
    if (bundleCount >= 4) return 0.40; // 40% discount for 4+ bundles
    if (bundleCount === 3) return 0.30; // 30% discount for 3 bundles
    if (bundleCount === 2) return 0.20; // 20% discount for 2 bundles
    return 0; // No discount for 1 bundle
  };

  const calculateTotalPrice = () => {
    const selectedBundles = pricingBundles.filter(bundle => 
      formData.selectedBundles.includes(bundle.id)
    );
    
    const basePrice = selectedBundles.reduce((total, bundle) => {
      return total + (formData.paymentMethod === 'monthly' ? bundle.monthlyPrice : bundle.yearlyPrice);
    }, 0);
    
    const discount = calculateBundleDiscount();
    const discountedPrice = basePrice * (1 - discount);
    
    return {
      basePrice,
      discount,
      discountedPrice,
      savings: basePrice - discountedPrice
    };
  };

  const handleNext = async () => {
    if (currentStep < steps.length) {
      try {
        // Save current step progress before moving to next step
        const nextStep = currentStep + 1;
        await onboardingAPI.saveProgress(nextStep, formData);
        
        setCurrentStep(nextStep);
      } catch (error) {
        console.error('Failed to save onboarding progress:', error);
        // Continue anyway - don't block user progress
        setCurrentStep(currentStep + 1);
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handlePaymentSetup = async () => {
    setLoading(true);
    try {
      // Check if user selected free plan only
      const hasFreePlanOnly = formData.selectedBundles.length === 1 && formData.selectedBundles.includes('free');
      
      if (hasFreePlanOnly) {
        console.log('Free plan selected - skipping payment setup');
        setCurrentStep(currentStep + 1);
        return;
      }
      
      // Validate payment method selection for paid plans
      if (!formData.selectedPaymentType) {
        alert('⚠️ Please select a payment method to continue with your subscription.');
        return;
      }
      
      console.log('Setting up payment with method:', formData.selectedPaymentType);
      console.log('Selected bundles:', formData.selectedBundles);
      console.log('Total amount:', calculateTotalPrice().discountedPrice);
      
      // TODO: Integrate with Stripe/PayPal for actual payment processing
      // For now, simulate payment setup based on selected method
      
      if (formData.selectedPaymentType === 'credit_card') {
        // Simulate Stripe integration
        console.log('Processing credit card payment with Stripe...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        alert('✅ Payment method verified!\nYour subscription will begin after the 14-day free trial.');
      } else if (formData.selectedPaymentType === 'paypal') {
        // Simulate PayPal integration  
        console.log('Processing PayPal payment...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        alert('✅ PayPal payment method verified!\nYour subscription will begin after the 14-day free trial.');
      }
      
      // Move to final step
      setCurrentStep(currentStep + 1);
    } catch (error) {
      console.error('Payment setup error:', error);
      alert('❌ Payment setup failed. Please try again or contact support.');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      // Step 1: Create workspace with onboarding data
      const workspaceData = {
        name: formData.workspaceName,
        industry: formData.industry,
        team_size: formData.teamSize,
        business_goals: formData.selectedGoals,
        selected_bundles: formData.selectedBundles,
        payment_method: formData.paymentMethod
      };

      console.log('Creating workspace:', workspaceData);
      
      // Create workspace
      const workspaceResponse = await onboardingAPI.createWorkspace(workspaceData);
      const workspaceId = workspaceResponse.data?.data?.id;
      
      if (!workspaceId) {
        throw new Error('Failed to create workspace');
      }

      // Step 2: Complete onboarding process
      const onboardingData = {
        workspace_id: workspaceId,
        workspace: {
          name: formData.workspaceName,
          industry: formData.industry,
          team_size: formData.teamSize
        },
        business_goals: formData.selectedGoals,
        selected_bundles: formData.selectedBundles,
        payment_method: formData.paymentMethod,
        pricing_details: calculateTotalPrice(),
        user_preferences: {
          notifications: true,
          marketing_emails: true,
          analytics_tracking: true
        },
        onboarding_step: "completed",
        completed_at: new Date().toISOString()
      };

      console.log('Completing onboarding:', onboardingData);
      
      // Complete onboarding
      await onboardingAPI.completeOnboarding(onboardingData);
      
      console.log('✅ Onboarding completed successfully');
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Onboarding error:', error);
      
      // Show specific error message
      let errorMessage = 'There was an error completing your setup. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Please log in to complete your setup.';
        navigate('/login');
        return;
      } else if (error.response?.status === 400) {
        errorMessage = 'Please check your information and try again.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getSelectedBundles = () => {
    return pricingBundles.filter(bundle => formData.selectedBundles.includes(bundle.id));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.workspaceName.trim() !== '';
      case 2:
        return formData.industry && formData.teamSize && formData.selectedGoals.length > 0;
      case 3:
        return formData.selectedBundles.length > 0;
      case 4:
        // Require payment method selection for paid plans
        const hasFreePlanOnly = formData.selectedBundles.length === 1 && formData.selectedBundles.includes('free');
        return hasFreePlanOnly || formData.selectedPaymentType !== null;
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
            <span className="gradient-text">MEWAYZ</span>
          </div>
          <div className="progress-info">
            <h1 className="wizard-title">Welcome to MEWAYZ</h1>
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
                <h2>Choose Your Bundles</h2>
                <p>Select the bundles that match your business goals. Multi-bundle discounts available!</p>
                
                {formData.selectedGoals.length > 0 && (
                  <div className="selected-goals-info">
                    <h4>✨ Recommended bundles for your goals:</h4>
                    <div className="goals-summary">
                      {formData.selectedGoals.map(goalId => {
                        const goal = businessGoals.find(g => g.id === goalId);
                        return goal ? (
                          <span key={goalId} className="goal-tag">
                            {goal.icon} {goal.title}
                          </span>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}
                
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

                {formData.selectedBundles.length > 1 && (
                  <div className="multi-bundle-discount">
                    <h4>🎉 Multi-Bundle Discount Applied!</h4>
                    <p>
                      {formData.selectedBundles.length === 2 && "20% discount for 2 bundles"}
                      {formData.selectedBundles.length === 3 && "30% discount for 3 bundles"}
                      {formData.selectedBundles.length >= 4 && "40% discount for 4+ bundles"}
                    </p>
                  </div>
                )}
              </div>

              <div className="pricing-plans">
                {getFilteredBundles().map((bundle) => (
                  <div 
                    key={bundle.id}
                    onClick={() => handleBundleSelect(bundle.id)}
                    className={`pricing-card ${formData.selectedBundles.includes(bundle.id) ? 'selected' : ''}`}
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
                <h2>Payment Setup</h2>
                <p>Complete your subscription to get started with your selected bundles</p>
              </div>

              <div className="payment-setup">
                <div className="payment-summary">
                  <h3>Order Summary</h3>
                  <div className="order-details">
                    {getSelectedBundles().map((bundle) => (
                      <div key={bundle.id} className="order-item">
                        <span className="item-name">{bundle.name}</span>
                        <span className="item-price">
                          ${formData.paymentMethod === 'monthly' 
                            ? bundle.monthlyPrice 
                            : bundle.yearlyPrice
                          }
                        </span>
                      </div>
                    ))}
                    
                    {formData.selectedBundles.length > 1 && (
                      <>
                        <div className="order-item subtotal">
                          <span>Subtotal:</span>
                          <span>${calculateTotalPrice().basePrice.toFixed(2)}</span>
                        </div>
                        <div className="order-item discount">
                          <span>Multi-bundle Discount ({(calculateBundleDiscount() * 100)}%):</span>
                          <span>-${calculateTotalPrice().savings.toFixed(2)}</span>
                        </div>
                      </>
                    )}
                    
                    <div className="order-item total">
                      <span>Total Amount:</span>
                      <span>${calculateTotalPrice().discountedPrice.toFixed(2)}</span>
                    </div>
                    
                    <div className="billing-period">
                      <small>Billed {formData.paymentMethod}</small>
                    </div>
                  </div>
                </div>

                <div className="payment-options">
                  <h3>Choose Payment Method</h3>
                  <div className="payment-methods">
                    {paymentSettings.credit_card_enabled && (
                      <div 
                        className={`payment-method card-payment ${formData.selectedPaymentType === 'credit_card' ? 'selected' : ''}`}
                        onClick={() => setFormData({...formData, selectedPaymentType: 'credit_card'})}
                      >
                        <div className="method-header">
                          <span className="method-icon">💳</span>
                          <span className="method-name">Credit Card</span>
                          <span className="method-badge">Recommended</span>
                        </div>
                        <div className="method-description">
                          Secure payment with Stripe. Start your 14-day free trial.
                        </div>
                      </div>
                    )}
                    
                    {paymentSettings.paypal_enabled && (
                      <div 
                        className={`payment-method paypal-payment ${formData.selectedPaymentType === 'paypal' ? 'selected' : ''}`}
                        onClick={() => setFormData({...formData, selectedPaymentType: 'paypal'})}
                      >
                        <div className="method-header">
                          <span className="method-icon">💰</span>
                          <span className="method-name">PayPal</span>
                        </div>
                        <div className="method-description">
                          Pay securely with your PayPal account.
                        </div>
                      </div>
                    )}
                    
                    {!paymentSettings.credit_card_enabled && !paymentSettings.paypal_enabled && (
                      <div className="no-payment-methods">
                        <p>Payment methods are currently being configured. Please try again later.</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="trial-notice">
                  <div className="notice-content">
                    <h4>🎉 14-Day Free Trial</h4>
                    <p>Start your free trial today. No charges for 14 days. Cancel anytime during the trial period.</p>
                    <ul className="trial-benefits">
                      <li>✓ Full access to all selected bundles</li>
                      <li>✓ No setup fees or hidden charges</li>
                      <li>✓ Cancel anytime before trial ends</li>
                      <li>✓ Keep all data if you decide to continue</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 5 && (
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
                    <span className="summary-label">Selected Goals:</span>
                    <span className="summary-value">
                      {formData.selectedGoals.map(goalId => {
                        const goal = businessGoals.find(g => g.id === goalId);
                        return goal ? goal.title : goalId;
                      }).join(', ')}
                    </span>
                  </div>
                </div>

                {formData.selectedBundles.length > 0 && (
                  <div className="summary-section">
                    <h3>Selected Bundles</h3>
                    {getSelectedBundles().map((bundle) => (
                      <div key={bundle.id} className="selected-bundle-item">
                        <div className="bundle-summary-header">
                          <span className="bundle-summary-name">{bundle.name}</span>
                          <span className="bundle-summary-price">
                            ${formData.paymentMethod === 'monthly' 
                              ? bundle.monthlyPrice 
                              : Math.floor(bundle.yearlyPrice / 12)
                            }/month
                          </span>
                        </div>
                      </div>
                    ))}
                    
                    {formData.selectedBundles.length > 1 && (
                      <div className="pricing-summary">
                        <div className="pricing-breakdown">
                          <div className="price-row">
                            <span>Subtotal:</span>
                            <span>${calculateTotalPrice().basePrice.toFixed(2)}</span>
                          </div>
                          <div className="price-row discount">
                            <span>Multi-bundle Discount ({(calculateBundleDiscount() * 100)}%):</span>
                            <span>-${calculateTotalPrice().savings.toFixed(2)}</span>
                          </div>
                          <div className="price-row total">
                            <span>Total:</span>
                            <span>${calculateTotalPrice().discountedPrice.toFixed(2)}/{formData.paymentMethod}</span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <p className="plan-summary-billing">
                      Billed {formData.paymentMethod === 'monthly' ? 'monthly' : 'yearly'}
                      {formData.paymentMethod === 'yearly' && ' (17% additional savings)'}
                    </p>
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
                onClick={currentStep === 4 ? handlePaymentSetup : handleNext} 
                disabled={!canProceed()}
                className="btn btn-primary"
              >
                {currentStep === 4 ? 'Start Free Trial' : 'Continue'}
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