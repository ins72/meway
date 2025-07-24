import React, { useState, useEffect } from 'react';
import './MEWAYZ_V2_LANDING_PAGE.css';

const LandingPage = () => {
  const [theme, setTheme] = useState('dark');
  const [isLoading, setIsLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Loading screen
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="landing-page" data-theme={theme}>
      {/* Loading Screen */}
      {isLoading && (
        <div className="loading-screen">
          <div className="loading-spinner"></div>
        </div>
      )}

      {/* Background Effects */}
      <div className="bg-effects">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'active' : ''}`}>
        <button className="mobile-menu-close" onClick={toggleMobileMenu}>×</button>
        <a href="#about" onClick={() => scrollToSection('about')}>About</a>
        <a href="#features" onClick={() => scrollToSection('features')}>Features</a>
        <a href="#testimonials" onClick={() => scrollToSection('testimonials')}>Testimonials</a>
        <a href="#pricing" onClick={() => scrollToSection('pricing')}>Pricing</a>
        <a href="#contact" onClick={() => scrollToSection('contact')}>Contact</a>
      </div>

      {/* Header */}
      <Header 
        theme={theme}
        toggleTheme={toggleTheme}
        toggleMobileMenu={toggleMobileMenu}
        scrollToSection={scrollToSection}
      />

      {/* Hero Section */}
      <HeroSection />

      {/* Features Section */}
      <FeaturesSection />

      {/* Testimonials Section */}
      <TestimonialsSection />

      {/* Call to Action Section */}
      <CTASection />

      {/* Pricing Section - Moved above footer */}
      <PricingSection />

      {/* Footer */}
      <Footer />
    </div>
  );
};

const Header = ({ theme, toggleTheme, toggleMobileMenu, scrollToSection }) => {
  return (
    <header className="header">
      <nav className="nav">
        <div className="logo">Mewayz</div>
        <ul className="nav-links">
          <li><a href="#about" onClick={() => scrollToSection('about')}>About</a></li>
          <li><a href="#features" onClick={() => scrollToSection('features')}>Features</a></li>
          <li><a href="#testimonials" onClick={() => scrollToSection('testimonials')}>Testimonials</a></li>
          <li><a href="#pricing" onClick={() => scrollToSection('pricing')}>Pricing</a></li>
          <li><a href="#contact" onClick={() => scrollToSection('contact')}>Contact</a></li>
        </ul>
        <div className="nav-actions">
          <button className="theme-toggle" onClick={toggleTheme}>
            <span>{theme === 'dark' ? '🌙' : '☀️'}</span>
          </button>
          <button className="mobile-menu-toggle" onClick={toggleMobileMenu}>☰</button>
          <a href="#login" className="btn btn-secondary">Login</a>
          <a href="#signup" className="btn btn-primary">
            Get Started
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 17L17 7M17 7H7M17 7V17"/>
            </svg>
          </a>
        </div>
      </nav>
    </header>
  );
};

const HeroSection = () => {
  return (
    <section className="hero">
      <div className="hero-badge">
        <span className="emoji">🚀</span> 
        <span className="text-content">Trusted by 10,000+ Businesses Worldwide</span>
      </div>
      <h1>
        The Complete Creator<br />
        <span className="gradient-text">Economy Platform</span>
      </h1>
      <p>Everything you need to build, manage, and scale your online business. From Instagram lead generation to multi-vendor marketplaces, courses, and AI-powered automation - all in one powerful platform.</p>
      <div className="hero-actions">
        <a href="/register" className="btn btn-primary">
          Start Free Trial - 14 Days
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 17L17 7M17 7H7M17 7V17"/>
          </svg>
        </a>
        <a href="#demo" className="btn btn-secondary">
          Watch 2-Min Demo
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="5,3 19,12 5,21"/>
          </svg>
        </a>
      </div>
      <div className="hero-stats">
        <div className="stat">
          <span className="stat-number">10K+</span>
          <span className="stat-label">Active Users</span>
        </div>
        <div className="stat">
          <span className="stat-number">$2.5M+</span>
          <span className="stat-label">Revenue Generated</span>
        </div>
        <div className="stat">
          <span className="stat-number">99.9%</span>
          <span className="stat-label">Uptime SLA</span>
        </div>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      icon: '🔍',
      title: 'Instagram Database & Lead Generation',
      description: 'Advanced filtering system for Instagram profiles with follower count, engagement rate, location, and hashtag analysis. Export leads with email discovery.'
    },
    {
      icon: '🔗',
      title: 'Link in Bio Builder',
      description: 'Drag-and-drop bio link builder with custom domains, analytics tracking, dynamic content, and e-commerce integration for maximum conversions.'
    },
    {
      icon: '🎓',
      title: 'Courses & Community Platform',
      description: 'Complete Skool-like platform with video hosting, progress tracking, discussion forums, gamification, and live streaming capabilities.'
    },
    {
      icon: '🛍️',
      title: 'E-commerce & Marketplace',
      description: 'Multi-vendor marketplace with individual stores, payment processing, inventory management, review system, and order fulfillment.'
    },
    {
      icon: '👥',
      title: 'CRM & Email Marketing',
      description: 'Advanced CRM with lead scoring, pipeline management, automated email campaigns, A/B testing, and detailed analytics tracking.'
    },
    {
      icon: '📊',
      title: 'Analytics & Automation',
      description: 'Unified analytics dashboard with gamification, workflow automation, AI-powered insights, and customizable reporting tools.'
    },
    {
      icon: '🌐',
      title: 'Website Builder',
      description: 'No-code website builder with responsive templates, SEO optimization, custom domains, and integrated e-commerce capabilities.'
    },
    {
      icon: '📅',
      title: 'Booking System',
      description: 'Professional appointment scheduling with calendar integration, payment processing, automated reminders, and staff management.'
    },
    {
      icon: '💳',
      title: 'Financial Management',
      description: 'Complete invoicing system with payment processing, expense tracking, financial reporting, and multi-currency support.'
    },
    {
      icon: '🎨',
      title: 'Template Marketplace',
      description: 'Create, share, and monetize templates for websites, emails, and social media with rating system and revenue sharing.'
    },
    {
      icon: '🔐',
      title: 'Escrow System',
      description: 'Secure transaction platform for digital products and services with dispute resolution and milestone payment support.'
    },
    {
      icon: '🤖',
      title: 'AI Content Generation',
      description: 'AI-powered content creation for blogs, social media, and marketing with trend analysis and optimization suggestions.'
    }
  ];

  return (
    <section className="features" id="features">
      <div className="section-header">
        <div className="section-badge">
          <span className="emoji">🚀</span> 
          <span className="text-content">6 Main Goals + Advanced Features</span>
        </div>
        <h2>Everything You Need in One Platform</h2>
        <p className="features-subtitle">Complete business management solution with 15+ integrated systems, all backed by real database operations and 62 production-ready APIs.</p>
      </div>
      
      <div className="features-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card animate-on-scroll">
            <div className="feature-icon">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

const TestimonialsSection = () => {
  const testimonials = [
    {
      text: "Mewayz v2 is incredible! The Instagram database feature helped me find and connect with over 500 potential clients in my niche. The lead generation tools are game-changing.",
      author: "Sarah Johnson",
      role: "Digital Marketing Consultant",
      avatar: "SJ"
    },
    {
      text: "The all-in-one platform approach is exactly what I needed. From course creation to e-commerce, everything integrates seamlessly. My business has grown 300% since switching.",
      author: "Mike Chen",
      role: "Online Course Creator",
      avatar: "MC"
    },
    {
      text: "The workflow automation and CRM features have saved me countless hours. I can now focus on creating content while Mewayz handles the business operations automatically.",
      author: "Emily Rodriguez",
      role: "Content Creator & Entrepreneur",
      avatar: "ER"
    }
  ];

  return (
    <section className="testimonials" id="testimonials">
      <div className="section-header">
        <div className="section-badge">
          <span className="emoji">💬</span> 
          <span className="text-content">Success Stories</span>
        </div>
        <h2>What Our Users Are Saying</h2>
        <p className="features-subtitle">Real feedback from businesses using Mewayz v2 to scale their operations and increase revenue.</p>
      </div>
      <div className="testimonials-grid">
        {testimonials.map((testimonial, index) => (
          <div key={index} className="testimonial-card animate-on-scroll">
            <p>"{testimonial.text}"</p>
            <div className="testimonial-author">
              <div className="avatar">{testimonial.avatar}</div>
              <div className="author-info">
                <strong>{testimonial.author}</strong>
                <span>{testimonial.role}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

const CTASection = () => {
  return (
    <section className="cta-section animate-on-scroll">
      <h2>Ready to Transform Your Business?</h2>
      <p>Join the businesses already using Mewayz v2 to streamline operations, increase revenue, and scale efficiently. Start with 10 free features today.</p>
      <a href="#signup" className="btn btn-primary">
        Start Free Trial Now
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M7 17L17 7M17 7H7M17 7V17"/>
        </svg>
      </a>
    </section>
  );
};

const PricingSection = () => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      description: 'Perfect for getting started',
      features: [
        '10 features included',
        'Basic workspace access',
        'Community support',
        'Basic analytics',
        'Email support',
        'Mobile app access',
        'Basic templates',
        'Standard integrations'
      ],
      cta: 'Get Started Free',
      popular: false
    },
    {
      name: 'Pro',
      price: '$1',
      period: '/feature/month',
      yearly: '$10/feature/year',
      description: 'For growing businesses',
      features: [
        'All Free features',
        'Unlimited features available',
        'Priority support',
        'Advanced analytics',
        'Custom domains',
        'Team collaboration',
        'Premium templates',
        'API access',
        'Advanced integrations',
        'White-label options'
      ],
      cta: 'Choose Your Features',
      popular: true
    },
    {
      name: 'Enterprise',
      price: '$1.5',
      period: '/feature/month',
      yearly: '$15/feature/year',
      description: 'For large organizations',
      features: [
        'All Pro features',
        'Full white-label solution',
        'Custom branding',
        'Dedicated account manager',
        'Custom integrations',
        'Priority feature requests',
        'Advanced security',
        'SLA guarantee',
        'Custom development',
        '24/7 phone support'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  return (
    <section className="pricing" id="pricing">
      <div className="pricing-container">
        <div className="section-header">
          <div className="section-badge">
            <span className="emoji">💰</span> 
            <span className="text-content">Flexible Pricing</span>
          </div>
          <h2>Pay Only for What You Use</h2>
          <p className="pricing-subtitle">Start free with 10 features, then scale by adding only the features you need. No hidden fees, cancel anytime.</p>
        </div>
        
        <div className="pricing-grid">
          {plans.map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.popular ? 'popular' : ''} animate-on-scroll`}>
              <h3 className="plan-name">{plan.name}</h3>
              <div className="plan-price">
                {plan.price}
                <span>{plan.period}</span>
                {plan.yearly && <div className="yearly-price">or {plan.yearly}</div>}
              </div>
              <p className="plan-description">{plan.description}</p>
              <ul className="plan-features">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex}>{feature}</li>
                ))}
              </ul>
              <a href="#signup" className="btn btn-primary plan-cta">
                {plan.cta}
              </a>
            </div>
          ))}
        </div>
        
        <div className="pricing-note">
          <p>All plans include access to our 62 production-ready APIs, real-time analytics, and comprehensive documentation.</p>
        </div>
      </div>
    </section>
  );
};

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer" id="contact">
      <div className="footer-container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="logo">Mewayz</div>
            <p>The complete all-in-one business management platform. Built for creators, entrepreneurs, and businesses ready to scale with advanced tools and real-time analytics.</p>
            <div className="social-links">
              <a href="#twitter" className="social-link" aria-label="Twitter">𝕏</a>
              <a href="#instagram" className="social-link" aria-label="Instagram">📷</a>
              <a href="#linkedin" className="social-link" aria-label="LinkedIn">💼</a>
              <a href="#youtube" className="social-link" aria-label="YouTube">📺</a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Main Goals</h4>
            <ul>
              <li><a href="#instagram">Instagram Database</a></li>
              <li><a href="#linkinbio">Link in Bio Builder</a></li>
              <li><a href="#courses">Courses & Community</a></li>
              <li><a href="#ecommerce">E-commerce & Marketplace</a></li>
              <li><a href="#crm">CRM & Email Marketing</a></li>
              <li><a href="#analytics">Analytics & Automation</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li><a href="#website-builder">Website Builder</a></li>
              <li><a href="#booking">Booking System</a></li>
              <li><a href="#financial">Financial Management</a></li>
              <li><a href="#templates">Template Marketplace</a></li>
              <li><a href="#escrow">Escrow System</a></li>
              <li><a href="#ai-tools">AI Content Generation</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Platform</h4>
            <ul>
              <li><a href="#api-docs">API Documentation</a></li>
              <li><a href="#mobile">Mobile App (Flutter)</a></li>
              <li><a href="#pwa">Progressive Web App</a></li>
              <li><a href="#integrations">Integrations</a></li>
              <li><a href="#security">Security</a></li>
              <li><a href="#status">System Status</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li><a href="#help">Help Center</a></li>
              <li><a href="#docs">Documentation</a></li>
              <li><a href="#community">Community</a></li>
              <li><a href="mailto:support@mewayz.com">support@mewayz.com</a></li>
              <li><a href="#terms">Terms of Service</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>© {currentYear} Mewayz v2. All rights reserved. Built for the modern business. | 62 APIs • 15+ Systems • 100% Real Data</p>
        </div>
      </div>
    </footer>
  );
};

export default LandingPage;