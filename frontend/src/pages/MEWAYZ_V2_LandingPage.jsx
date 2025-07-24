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

  // Animation on scroll functionality
  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    // Observe all elements with animate-on-scroll class
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    animateElements.forEach(el => observer.observe(el));

    return () => {
      animateElements.forEach(el => observer.unobserve(el));
    };
  }, [isLoading]); // Re-run after loading is complete

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
        <div className="mobile-menu-content">
          <div className="mobile-nav-links">
            <a href="#features" onClick={() => scrollToSection('features')}>Features</a>
            <a href="#pricing" onClick={() => scrollToSection('pricing')}>Pricing</a>
            <a href="#testimonials" onClick={() => scrollToSection('testimonials')}>Reviews</a>
            <a href="/help" target="_blank">Help</a>
            <a href="/contact">Contact</a>
          </div>
          <div className="mobile-auth-actions">
            <a href="/login" className="mobile-login-btn">Login</a>
            <a href="/register" className="mobile-signup-btn">
              Start Free Trial
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M7 17L17 7M17 7H7M17 7V17"/>
              </svg>
            </a>
          </div>
        </div>
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
        <div className="logo">MEWAYZ</div>
        <ul className="nav-links desktop-only">
          <li><a href="#features" onClick={() => scrollToSection('features')}>Features</a></li>
          <li><a href="#pricing" onClick={() => scrollToSection('pricing')}>Pricing</a></li>
          <li><a href="#testimonials" onClick={() => scrollToSection('testimonials')}>Reviews</a></li>
          <li><a href="/help" target="_blank">Help</a></li>
          <li><a href="/contact">Contact</a></li>
        </ul>
        <div className="nav-actions">
          <button className="theme-toggle desktop-only" onClick={toggleTheme}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {theme === 'dark' ? (
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              ) : (
                <>
                  <circle cx="12" cy="12" r="5"/>
                  <line x1="12" y1="1" x2="12" y2="3"/>
                  <line x1="12" y1="21" x2="12" y2="23"/>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                  <line x1="1" y1="12" x2="3" y2="12"/>
                  <line x1="21" y1="12" x2="23" y2="12"/>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </>
              )}
            </svg>
          </button>
          <a href="/login" className="btn btn-secondary desktop-only">Login</a>
          <a href="/register" className="btn btn-primary desktop-only">
            Start Free Trial
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 17L17 7M17 7H7M17 7V17"/>
            </svg>
          </a>
          <button className="mobile-menu-toggle mobile-tablet-only" onClick={toggleMobileMenu}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
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
      title: 'Instagram Lead Generation',
      description: 'Advanced Instagram database with 50M+ profiles. Filter by engagement rate, follower count, location, and hashtags. Export qualified leads with contact discovery.'
    },
    {
      icon: '🔗',
      title: 'Bio Link Builder',
      description: 'Create stunning bio link pages with custom domains, analytics tracking, payment integration, and unlimited links. Convert followers to customers instantly.'
    },
    {
      icon: '🎓',
      title: 'Course Platform',
      description: 'Complete learning management system with video hosting, progress tracking, certificates, live sessions, and community features. Monetize your expertise.'
    },
    {
      icon: '🛍️',
      title: 'Multi-Vendor Marketplace',
      description: 'Build your own marketplace like Amazon or Etsy. Vendor management, commission tracking, payment processing, and order fulfillment - all automated.'
    },
    {
      icon: '👥',
      title: 'CRM & Automation',
      description: 'Advanced customer relationship management with lead scoring, email sequences, SMS marketing, and AI-powered follow-ups. Never lose a lead again.'
    },
    {
      icon: '📊',
      title: 'Analytics Dashboard',
      description: 'Real-time insights across all your business channels. Track revenue, conversion rates, customer lifetime value, and ROI with beautiful visualizations.'
    },
    {
      icon: '🌐',
      title: 'Website Builder',
      description: 'Professional drag-and-drop website builder with e-commerce integration, SEO optimization, mobile responsiveness, and custom domains.'
    },
    {
      icon: '📅',
      title: 'Booking System',
      description: 'Complete appointment scheduling with calendar sync, automated reminders, payment collection, and team management. Perfect for service businesses.'
    },
    {
      icon: '💳',
      title: 'Financial Management',
      description: 'Comprehensive invoicing, expense tracking, tax reporting, and multi-currency support. Accept payments globally with low fees.'
    },
    {
      icon: '🎨',
      title: 'Template Marketplace',
      description: 'Monetize your designs by selling templates for websites, emails, and social media. Built-in licensing, payments, and creator revenue sharing.'
    },
    {
      icon: '🔐',
      title: 'Escrow System',
      description: 'Secure transaction processing for digital products and services. Built-in dispute resolution and milestone payments for project-based work.'
    },
    {
      icon: '🤖',
      title: 'AI Content Assistant',
      description: 'Generate high-converting content for social media, blogs, ads, and emails. AI-powered optimization suggestions and trend analysis included.'
    }
  ];

  return (
    <section className="features" id="features">
      <div className="section-header">
        <div className="section-badge">
          <span className="emoji">⚡</span> 
          <span className="text-content">12 Powerful Tools in One Platform</span>
        </div>
        <h2>Everything You Need to Succeed Online</h2>
        <p className="features-subtitle">From lead generation to course creation, marketplace building to financial management - we've got every aspect of your digital business covered.</p>
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
      text: "Mewayz transformed my Instagram strategy completely. I went from 5K to 50K followers in 6 months using their lead generation tools. The bio link builder alone increased my conversion rate by 340%.",
      author: "Sarah Chen",
      role: "Digital Marketing Coach",
      avatar: "SC",
      company: "@sarahchenmarketing"
    },
    {
      text: "As a course creator, I've tried everything. Mewayz is the first platform that truly does it all - from student management to payment processing. My course revenue increased 250% in the first quarter.",
      author: "Marcus Rodriguez",
      role: "Online Educator",
      avatar: "MR",
      company: "MasterClass Academy"
    },
    {
      text: "The marketplace feature is incredible. I built a multi-vendor platform for local artisans in just 2 weeks. We've processed over $100K in transactions with zero technical issues.",
      author: "Emily Watson",
      role: "E-commerce Entrepreneur",
      avatar: "EW",
      company: "Artisan Collective"
    }
  ];

  return (
    <section className="testimonials" id="testimonials">
      <div className="section-header">
        <div className="section-badge">
          <span className="emoji">⭐</span> 
          <span className="text-content">Success Stories</span>
        </div>
        <h2>Trusted by Thousands of Creators</h2>
        <p className="features-subtitle">Join successful entrepreneurs who have transformed their businesses with Mewayz. Real results from real users.</p>
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
                <span className="company">{testimonial.company}</span>
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
      <p>Join over 10,000 successful creators, entrepreneurs, and businesses who trust Mewayz to power their growth. Start your 14-day free trial today - no credit card required.</p>
      <div className="cta-actions">
        <a href="/register" className="btn btn-primary">
          Start Free Trial - 14 Days
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 17L17 7M17 7H7M17 7V17"/>
          </svg>
        </a>
        <a href="/contact" className="btn btn-secondary">
          Schedule Demo Call
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9,22 9,12 15,12 15,22"/>
          </svg>
        </a>
      </div>
      <div className="cta-guarantee">
        <p>✨ <strong>30-day money-back guarantee</strong> • 🔒 <strong>No setup fees</strong> • 📞 <strong>24/7 support</strong></p>
      </div>
    </section>
  );
};

const PricingSection = () => {
  const plans = [
    {
      name: 'Starter',
      price: '$0',
      period: '/month',
      description: 'Perfect for solopreneurs getting started',
      features: [
        '14-day free trial',
        '1 workspace',
        'Basic Instagram lead generation',
        'Simple bio link page',
        'Basic analytics',
        'Email support',
        'Mobile app access',
        'Community support'
      ],
      cta: 'Start Free Trial',
      popular: false
    },
    {
      name: 'Professional',
      price: '$29',
      period: '/month',
      yearly: '$290/year (save $58)',
      description: 'Best for growing creators & businesses',
      features: [
        'Everything in Starter',
        '5 workspaces',
        'Advanced Instagram database',
        'Multi-vendor marketplace',
        'Course creation platform',
        'Advanced CRM & automation',
        'Professional website builder',
        'Priority support',
        'Custom domains',
        'Advanced analytics & reporting'
      ],
      cta: 'Start Professional',
      popular: true
    },
    {
      name: 'Enterprise',
      price: '$99',
      period: '/month',
      yearly: '$990/year (save $198)',
      description: 'For teams & large organizations',
      features: [
        'Everything in Professional',
        'Unlimited workspaces',
        'White-label solution',
        'Custom branding',
        'Dedicated account manager',
        'Custom integrations',
        'Advanced security features',
        'SLA guarantee (99.9% uptime)',
        '24/7 phone support',
        'Priority feature requests'
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
            <span className="text-content">Transparent Pricing</span>
          </div>
          <h2>Choose Your Growth Plan</h2>
          <p className="pricing-subtitle">Start free and scale as you grow. No hidden fees, cancel anytime. Join thousands of successful creators and businesses.</p>
        </div>
        
        <div className="pricing-grid">
          {plans.map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.popular ? 'popular' : ''} animate-on-scroll`}>
              <h3 className="plan-name">{plan.name}</h3>
              <div className="plan-price">
                {plan.price}
                <span>{plan.period}</span>
                {plan.yearly && <div className="yearly-price">{plan.yearly}</div>}
              </div>
              <p className="plan-description">{plan.description}</p>
              <ul className="plan-features">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex}>{feature}</li>
                ))}
              </ul>
              <a href="/register" className="btn btn-primary plan-cta">
                {plan.cta}
              </a>
            </div>
          ))}
        </div>
        
        <div className="pricing-note">
          <p><strong>All plans include:</strong> Mobile app access, real-time analytics, automatic backups, SSL security, API access, and our comprehensive knowledge base. Trusted by 10,000+ businesses worldwide.</p>
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
            <div className="logo">MEWAYZ</div>
            <p>The complete creator economy platform trusted by over 10,000 businesses worldwide. Build, manage, and scale your online business with our comprehensive suite of tools.</p>
            <div className="social-links">
              <a href="https://twitter.com/mewayz" className="social-link" aria-label="Twitter" target="_blank" rel="noopener">𝕏</a>
              <a href="https://instagram.com/mewayz" className="social-link" aria-label="Instagram" target="_blank" rel="noopener">📷</a>
              <a href="https://linkedin.com/company/mewayz" className="social-link" aria-label="LinkedIn" target="_blank" rel="noopener">💼</a>
              <a href="https://youtube.com/mewayz" className="social-link" aria-label="YouTube" target="_blank" rel="noopener">📺</a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Platform</h4>
            <ul>
              <li><a href="/features/instagram">Instagram Lead Gen</a></li>
              <li><a href="/features/bio-links">Bio Link Builder</a></li>
              <li><a href="/features/courses">Course Platform</a></li>
              <li><a href="/features/marketplace">Marketplace</a></li>
              <li><a href="/features/website-builder">Website Builder</a></li>
              <li><a href="/features/crm">CRM & Automation</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li><a href="/help">Help Center</a></li>
              <li><a href="/documentation">Documentation</a></li>
              <li><a href="/blog">Blog</a></li>
              <li><a href="/case-studies">Case Studies</a></li>
              <li><a href="/templates">Template Library</a></li>
              <li><a href="/api-docs">API Documentation</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Company</h4>
            <ul>
              <li><a href="/about">About Us</a></li>
              <li><a href="/careers">Careers</a></li>
              <li><a href="/contact">Contact Sales</a></li>
              <li><a href="/partners">Partners</a></li>
              <li><a href="/affiliate">Affiliate Program</a></li>
              <li><a href="/status">System Status</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><a href="/terms">Terms of Service</a></li>
              <li><a href="/privacy">Privacy Policy</a></li>
              <li><a href="/cookies">Cookie Policy</a></li>
              <li><a href="/security">Security</a></li>
              <li><a href="/gdpr">GDPR Compliance</a></li>
              <li><a href="mailto:support@mewayz.com">Support</a></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>© {currentYear} Mewayz. All rights reserved. | Trusted by 10,000+ businesses worldwide | $2.5M+ revenue generated | 99.9% uptime</p>
          <div className="footer-badges">
            <span className="badge">SOC 2 Compliant</span>
            <span className="badge">GDPR Ready</span>
            <span className="badge">ISO 27001</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default LandingPage;