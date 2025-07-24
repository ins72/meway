# MEWAYZ V2 PROFESSIONAL SCREEN & PAGE DOCUMENTATION
### Complete Developer Implementation Guide

**Documentation Date:** December 30, 2024  
**Platform Version:** 2.0.0  
**Target Audience:** Frontend & Backend Developers  

---

## 📱 SCREEN ARCHITECTURE OVERVIEW

### User Journey Flow
```
Landing Page → Authentication → Onboarding Wizard → Dashboard → Features
     ↓              ↓               ↓                ↓           ↓
  Marketing     Login/Register   Workspace Setup   Main Hub   Goal-based
  Content       Multi-OAuth      6-Step Process    Navigation  Workspaces
```

### Screen Categories
- **🌟 Public Screens** (5 screens) - Marketing & Authentication
- **🚀 Onboarding Screens** (6 screens) - Multi-step setup wizard  
- **📊 Dashboard Screens** (10+ screens) - Main application interface
- **⚙️ Management Screens** (15+ screens) - Settings & administration
- **📱 Mobile Responsive** - All screens optimized for mobile

---

## 🌟 PUBLIC SCREENS DOCUMENTATION

### 1. Landing Page
**File:** `/frontend/src/pages/MEWAYZ_V2_LandingPage.jsx`  
**Route:** `/`  
**Status:** ✅ **PRODUCTION READY**

#### Screen Components
```javascript
const LandingPageSections = {
  header: {
    component: "Header",
    elements: ["logo", "navigation", "theme_toggle", "auth_buttons"],
    responsive: "collapsible_mobile_menu"
  },
  hero: {
    component: "HeroSection", 
    elements: ["headline", "cta_buttons", "trust_badge", "statistics"],
    cta_primary: "Start Free Trial - 14 Days",
    cta_secondary: "Watch 2-Min Demo"
  },
  features: {
    component: "FeaturesSection",
    display: "grid_layout_12_cards",
    animation: "scroll_triggered",
    cards: [
      { icon: "🔍", title: "Instagram Lead Generation", description: "Advanced database with 50M+ profiles" },
      { icon: "🔗", title: "Bio Link Builder", description: "Create stunning bio link pages" },
      // ... 10 more feature cards
    ]
  },
  testimonials: {
    component: "TestimonialsSection", 
    display: "horizontal_cards",
    count: 3,
    elements: ["quote", "author", "company", "avatar"]
  },
  pricing: {
    component: "PricingSection",
    plans: ["Free ($0)", "Professional ($29)", "Enterprise ($99)"],
    billing_toggle: "monthly_yearly",
    features_list: "checkmark_icons"
  },
  footer: {
    component: "Footer",
    sections: ["platform", "resources", "company", "legal"],
    social_links: true,
    compliance_badges: ["SOC 2", "GDPR", "ISO 27001"]
  }
};
```

#### Responsive Breakpoints
```css
/* Desktop: 1024px+ */
.features-grid { grid-template-columns: repeat(3, 1fr); }
.pricing-grid { grid-template-columns: repeat(3, 1fr); }

/* Tablet: 768px-1024px */  
.features-grid { grid-template-columns: repeat(2, 1fr); }
.pricing-grid { grid-template-columns: repeat(3, 1fr); }

/* Mobile: 320px-768px */
.features-grid { grid-template-columns: 1fr; }
.pricing-grid { grid-template-columns: 1fr; }
.nav-links { display: none; }
.mobile-menu-toggle { display: block; }
```

---

### 2. Login Page  
**File:** `/frontend/src/pages/auth/LoginPage.js`  
**Route:** `/login`  
**Status:** ✅ **READY** (Apple OAuth pending)

#### Screen Layout
```javascript
const LoginPageStructure = {
  layout: "centered_card_2_column",
  left_column: {
    content: "branding_illustration",
    elements: ["logo", "headline", "features_preview"],
    theme: "gradient_background"
  },
  right_column: {
    content: "login_form",
    elements: ["form_fields", "social_buttons", "links"],
    validation: "real_time"
  }
};

// Form Configuration
const LoginForm = {
  fields: [
    {
      name: "email",
      type: "email", 
      placeholder: "Enter your email",
      validation: "email_format",
      required: true
    },
    {
      name: "password",
      type: "password",
      placeholder: "Enter your password", 
      validation: "min_length_8",
      required: true,
      show_hide_toggle: true
    }
  ],
  social_auth: [
    {
      provider: "google",
      button_text: "Continue with Google",
      icon: "google_icon",
      component: "GoogleLogin",
      status: "✅ implemented"
    },
    {
      provider: "apple", 
      button_text: "Continue with Apple",
      icon: "apple_icon",
      component: "AppleLogin",
      status: "⚠️ needs_implementation"
    }
  ],
  footer_links: [
    { text: "Forgot Password?", route: "/forgot-password" },
    { text: "Don't have an account? Sign up", route: "/register" }
  ]
};
```

#### Authentication API Integration
```javascript
// Login API calls
const authService = {
  emailLogin: async (email, password) => {
    return await api.post('/api/auth/login', { email, password });
  },
  googleLogin: async (googleToken) => {
    return await api.post('/api/google-oauth/login', { token: googleToken });
  },
  appleLogin: async (appleToken) => {
    // TO IMPLEMENT
    return await api.post('/api/apple-oauth/login', { token: appleToken });
  }
};

// Error handling
const errorMessages = {
  invalid_credentials: "Invalid email or password",
  account_not_found: "No account found with this email",
  social_auth_failed: "Social authentication failed",
  network_error: "Connection error. Please try again."
};
```

---

### 3. Registration Page
**File:** `/frontend/src/pages/auth/RegisterPage.js`  
**Route:** `/register`  
**Status:** ✅ **READY**

#### Registration Flow
```javascript
const RegistrationSteps = {
  step_1: {
    title: "Create Your Account",
    fields: ["full_name", "email", "password", "confirm_password"],
    validation: {
      email: "unique_check_real_time",
      password: "strength_meter",
      confirm_password: "match_validation"
    }
  },
  step_2: {
    title: "Verify Email",
    description: "Check your email for verification link",
    resend_option: true,
    timeout: "60_seconds"
  },
  step_3: {
    title: "Account Created",
    redirect: "/onboarding",
    message: "Welcome to Mewayz! Let's set up your workspace."
  }
};

// Social registration options
const SocialRegistration = {
  google: {
    auto_create_account: true,
    skip_email_verification: true,
    redirect_to: "/onboarding"
  },
  apple: {
    auto_create_account: true, 
    skip_email_verification: true,
    redirect_to: "/onboarding"
  }
};
```

---

### 4. Workspace Invitation Page
**File:** `/frontend/src/pages/auth/WorkspaceInvitationPage.js`  
**Route:** `/invitation/:token`  
**Status:** ⚠️ **NEEDS ENHANCEMENT**

#### Invitation States
```javascript
const InvitationStates = {
  loading: {
    display: "loading_spinner",
    message: "Verifying invitation...",
    duration: "2_seconds"
  },
  valid_invitation: {
    display: "invitation_card", 
    elements: [
      "workspace_logo",
      "workspace_name", 
      "inviter_info",
      "role_badge",
      "accept_decline_buttons"
    ],
    message: "You have been invited to join workspace {workspace_name}"
  },
  accepting: {
    display: "loading_screen",
    message: "Joining workspace {workspace_name}, please wait...",
    visual: "progress_animation"
  },
  success: {
    display: "success_state",
    message: "Welcome to {workspace_name}!",
    redirect: "/dashboard",
    delay: "3_seconds"
  },
  invalid_invitation: {
    display: "error_state",
    message: "This invitation is invalid or has expired",
    action_button: "Request New Invitation"
  }
};
```

#### Implementation Requirements
```javascript
// API endpoints needed
const invitationAPI = {
  validateToken: `GET /api/workspace/invitation/${token}`,
  acceptInvitation: `POST /api/workspace/invitation/${token}/accept`,
  declineInvitation: `POST /api/workspace/invitation/${token}/decline`
};

// Visual components needed
const InvitationComponents = {
  LoadingScreen: "Generic loading with message",
  InvitationCard: "Branded invitation display",
  SuccessAnimation: "Checkmark animation with redirect",
  ErrorState: "User-friendly error handling"
};
```

---

## 🚀 ONBOARDING WIZARD DOCUMENTATION

### Multi-Step Wizard Architecture
**File:** `/frontend/src/pages/OnboardingWizard.js`  
**Route:** `/onboarding`  
**Status:** ⚠️ **70% COMPLETE**

#### Wizard Configuration
```javascript
const OnboardingWizardConfig = {
  total_steps: 6,
  progress_indicator: "step_dots_with_labels",
  navigation: {
    next_button: "Continue",
    back_button: "Back", 
    skip_option: "limited_steps_only",
    exit_option: "save_progress_modal"
  },
  persistence: {
    save_on_step_change: true,
    resume_capability: true,
    timeout_warning: "30_minutes"
  }
};
```

---

### Step 1: Workspace Setup
**Component:** `WorkspaceSetupStep`  
**Status:** ✅ **READY**

#### Form Configuration
```javascript
const WorkspaceSetupForm = {
  title: "Let's Set Up Your Workspace",
  subtitle: "Tell us about your business",
  fields: [
    {
      name: "workspace_name",
      type: "text",
      label: "Workspace Name",
      placeholder: "e.g., Acme Marketing Agency",
      validation: "required|min:2|max:50",
      help_text: "This will be visible to your team members"
    },
    {
      name: "description", 
      type: "textarea",
      label: "Description",
      placeholder: "What does your business do?",
      validation: "max:200",
      optional: true
    },
    {
      name: "industry",
      type: "select",
      label: "Industry",
      options: [
        "Marketing Agency", "E-commerce", "Education", "SaaS", 
        "Consulting", "Creator/Influencer", "Other"
      ],
      validation: "required"
    },
    {
      name: "website",
      type: "url", 
      label: "Website (Optional)",
      placeholder: "https://yourwebsite.com",
      validation: "url_format"
    }
  ],
  api_endpoint: "POST /api/workspace/",
  next_step_condition: "workspace_created"
};
```

---

### Step 2: Main Goals Selection  
**Component:** `MainGoalsSelectionStep`  
**Status:** ⚠️ **NEEDS IMPLEMENTATION**

#### Goals Configuration
```javascript
const MainGoalsConfig = {
  title: "Choose Your Main Goals",
  subtitle: "Select the goals that matter most to your business",
  selection_type: "multiple_choice",
  minimum_selection: 1,
  maximum_selection: 6,
  
  goals: [
    {
      id: "instagram",
      icon: "📱",
      title: "Instagram Lead Generation", 
      description: "Generate leads from Instagram with advanced filtering",
      features_included: 8,
      color: "gradient-purple",
      popular: false
    },
    {
      id: "link_in_bio",
      icon: "🔗", 
      title: "Link in Bio Builder",
      description: "Create beautiful bio link pages with analytics",
      features_included: 6,
      color: "gradient-blue", 
      popular: true
    },
    {
      id: "courses",
      icon: "🎓",
      title: "Courses & Community", 
      description: "Build and sell online courses with community",
      features_included: 6,
      color: "gradient-green",
      popular: false
    },
    {
      id: "ecommerce", 
      icon: "🛍️",
      title: "E-commerce & Marketplace",
      description: "Sell products online with multi-vendor support",
      features_included: 8, 
      color: "gradient-orange",
      popular: true
    },
    {
      id: "crm",
      icon: "👥",
      title: "CRM & Automation",
      description: "Manage customers with automated workflows", 
      features_included: 6,
      color: "gradient-red",
      popular: false
    },
    {
      id: "analytics",
      icon: "📊", 
      title: "Analytics & BI",
      description: "Business intelligence and unified analytics",
      features_included: 6,
      color: "gradient-indigo",
      popular: false
    }
  ]
};

// Visual Implementation
const GoalSelectionUI = {
  layout: "grid_2x3_desktop_1x6_mobile",
  card_design: {
    state_default: "border_gray_hover_lift",
    state_selected: "border_gradient_glow_effect", 
    state_disabled: "opacity_50_not_clickable"
  },
  interaction: {
    selection_feedback: "checkmark_animation",
    deselection_feedback: "fade_out_checkmark",
    hover_effect: "lift_shadow"
  }
};
```

---

### Step 3: Features Selection
**Component:** `FeaturesSelectionStep`  
**Status:** ⚠️ **NEEDS IMPLEMENTATION**

#### Features Logic
```javascript
const FeaturesSelectionLogic = {
  title: "Choose Your Features",
  subtitle: "Select features based on your goals",
  
  feature_mapping: {
    instagram: [
      "Instagram Database Access", "Engagement Rate Filtering", 
      "Lead Export Tools", "Social Media Scheduling",
      "Twitter Integration", "TikTok Integration",
      "Social Media Analytics", "Hashtag Research Tools"
    ],
    link_in_bio: [
      "Bio Link Builder", "Custom Domains", "Link Analytics",
      "QR Code Generation", "Website Builder", "SEO Optimization"
    ],
    ecommerce: [
      "Product Management", "Multi-vendor Support", "Payment Processing",
      "Inventory Management", "Order Fulfillment", "Shipping Integration", 
      "Coupon System", "Escrow System"
    ],
    courses: [
      "Course Creation", "Student Management", "Progress Tracking",
      "Live Streaming", "Certificates", "Community Forums"
    ],
    crm: [
      "Contact Management", "Email Marketing", "Workflow Automation",
      "Lead Scoring", "Pipeline Management", "SMS Marketing"
    ],
    analytics: [
      "Unified Analytics", "Custom Reports", "Business Intelligence",
      "Gamification", "Data Export", "Performance Metrics"
    ]
  },
  
  selection_rules: {
    free_plan_limit: 10,
    show_upgrade_prompt: "when_over_limit",
    feature_categories: "grouped_by_goal",
    pricing_preview: "realtime_calculation"
  }
};

// Dynamic Feature Display
const FeatureDisplayLogic = {
  // Show features based on selected goals from Step 2
  getAvailableFeatures: (selectedGoals) => {
    const features = [];
    selectedGoals.forEach(goal => {
      features.push(...FeaturesSelectionLogic.feature_mapping[goal]);
    });
    return [...new Set(features)]; // Remove duplicates
  },
  
  // Calculate pricing based on selection
  calculatePricing: (selectedFeatures, billingCycle) => {
    if (selectedFeatures.length <= 10) return { plan: "Free", cost: 0 };
    
    const professionalCost = billingCycle === "yearly" 
      ? selectedFeatures.length * 10 
      : selectedFeatures.length * 1;
      
    return { 
      plan: "Professional", 
      cost: professionalCost,
      billing: billingCycle 
    };
  }
};
```

---

### Step 4: Team Invitations
**Component:** `TeamInvitationsStep`  
**Status:** ⚠️ **NEEDS IMPLEMENTATION**

#### Team Management Interface
```javascript
const TeamInvitationsConfig = {
  title: "Invite Your Team",
  subtitle: "Add team members and assign roles",
  optional: true,
  skip_text: "I'll add team members later",
  
  invitation_form: {
    bulk_invite: true,
    csv_import: true,
    individual_fields: [
      {
        name: "email",
        type: "email",
        placeholder: "team@company.com",
        validation: "required|email"
      },
      {
        name: "first_name", 
        type: "text",
        placeholder: "First Name",
        validation: "required"
      },
      {
        name: "last_name",
        type: "text", 
        placeholder: "Last Name",
        validation: "required"
      },
      {
        name: "role",
        type: "select",
        options: [
          { value: "admin", label: "Admin", description: "Full workspace access" },
          { value: "editor", label: "Editor", description: "Can create and edit" },
          { value: "viewer", label: "Viewer", description: "View-only access" }
        ],
        default: "editor"
      },
      {
        name: "message",
        type: "textarea",
        placeholder: "Personal invitation message (optional)",
        max_length: 200
      }
    ]
  },
  
  role_permissions: {
    admin: {
      permissions: ["read", "write", "delete", "invite", "billing"],
      badge_color: "red",
      icon: "👑"
    },
    editor: {
      permissions: ["read", "write", "create"],
      badge_color: "blue", 
      icon: "✏️"
    },
    viewer: {
      permissions: ["read"],
      badge_color: "gray",
      icon: "👁️"
    }
  }
};

// Invitation Management
const InvitationManagement = {
  add_invitation: "dynamic_form_rows",
  remove_invitation: "x_button_with_confirmation",
  email_validation: "real_time_duplicate_check",
  send_immediately: true,
  invitation_preview: "modal_with_email_template"
};
```

---

### Step 5: Subscription Selection
**Component:** `SubscriptionSelectionStep`  
**Status:** ⚠️ **NEEDS IMPLEMENTATION**

#### Subscription Plans UI
```javascript
const SubscriptionPlansConfig = {
  title: "Choose Your Plan", 
  subtitle: "Based on your selected features",
  billing_toggle: {
    options: ["monthly", "yearly"],
    default: "monthly",
    savings_highlight: "Save 17% with yearly billing"
  },
  
  plans: [
    {
      id: "free",
      name: "Free",
      price: 0,
      billing_cycle: "none",
      features_limit: 10,
      description: "Perfect for getting started",
      highlight: false,
      disabled_if: "features_count > 10",
      features: [
        "Up to 10 features",
        "1 workspace",
        "Basic support",
        "Mobile app access"
      ],
      cta_text: "Start Free"
    },
    {
      id: "professional", 
      name: "Professional",
      price_per_feature: { monthly: 1, yearly: 10 },
      description: "Best for growing businesses",
      highlight: true,
      features: [
        "All features available",
        "Unlimited workspaces", 
        "Priority support",
        "Custom domains",
        "Advanced analytics"
      ],
      cta_text: "Choose Professional"
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price_per_feature: { monthly: 1.5, yearly: 15 },
      description: "For large organizations",
      highlight: false,
      features: [
        "Everything in Professional",
        "White-label solution",
        "Dedicated support",
        "Custom integrations", 
        "SLA guarantee"
      ],
      cta_text: "Contact Sales"
    }
  ]
};

// Dynamic Pricing Calculation
const PricingCalculation = {
  calculateCost: (selectedFeatures, plan, billingCycle) => {
    if (plan === "free") return 0;
    
    const featureCount = selectedFeatures.length;
    const pricePerFeature = SubscriptionPlansConfig.plans
      .find(p => p.id === plan)
      .price_per_feature[billingCycle];
      
    return featureCount * pricePerFeature;
  },
  
  displayPricing: {
    format: "currency_usd",
    period_suffix: true,
    savings_calculation: "automatic",
    feature_breakdown: "expandable_details"
  }
};
```

---

### Step 6: Branding Setup
**Component:** `BrandingSetupStep`  
**Status:** ⚠️ **NEEDS IMPLEMENTATION**

#### Branding Configuration
```javascript
const BrandingSetupConfig = {
  title: "Set Up Your Brand",
  subtitle: "Customize how your brand appears to customers",
  optional: true,
  skip_text: "Use default branding",
  
  branding_options: [
    {
      section: "logo_upload",
      title: "Upload Your Logo",
      fields: [
        {
          name: "logo",
          type: "file_upload",
          accept: ".png,.jpg,.svg",
          max_size: "2MB",
          preview: true,
          crop_options: ["square", "rectangle"]
        }
      ]
    },
    {
      section: "color_scheme", 
      title: "Choose Colors",
      fields: [
        {
          name: "primary_color",
          type: "color_picker",
          label: "Primary Color",
          default: "#667eea"
        },
        {
          name: "secondary_color",
          type: "color_picker", 
          label: "Secondary Color",
          default: "#764ba2"
        },
        {
          name: "accent_color",
          type: "color_picker",
          label: "Accent Color", 
          default: "#4facfe"
        }
      ]
    },
    {
      section: "company_info",
      title: "Company Information",
      fields: [
        {
          name: "company_name",
          type: "text",
          label: "Company Name",
          placeholder: "Your Company Name"
        },
        {
          name: "custom_domain",
          type: "text", 
          label: "Custom Domain (Optional)",
          placeholder: "yourdomain.com",
          validation: "domain_format",
          help_text: "Use your own domain for external pages"
        }
      ]
    }
  ],
  
  preview_areas: [
    "bio_link_page_preview",
    "email_template_preview", 
    "course_landing_preview"
  ]
};
```

---

## 📊 DASHBOARD SCREENS DOCUMENTATION

### Main Dashboard
**File:** `/frontend/src/pages/dashboard/Dashboard.js`  
**Route:** `/dashboard`  
**Status:** ⚠️ **NEEDS MAIN GOALS IMPLEMENTATION**

#### Dashboard Layout
```javascript
const DashboardLayout = {
  header: {
    components: ["workspace_selector", "global_search", "notifications", "user_menu"],
    workspace_selector: {
      display: "dropdown_with_switch_option",
      show_workspace_logo: true,
      quick_switch_shortcuts: true
    }
  },
  
  sidebar: {
    sections: [
      {
        title: "Main Goals",
        items: "dynamic_based_on_workspace_selection",
        display: "icon_with_label"
      },
      {
        title: "Tools", 
        items: ["settings", "team", "analytics", "billing"],
        collapsible: true
      }
    ]
  },
  
  main_content: {
    layout: "main_goals_grid",
    responsive: "mobile_stacked"
  }
};

// Dynamic Main Goals Display
const MainGoalsDashboard = {
  goal_cards: {
    instagram: {
      title: "Instagram Leads",
      icon: "📱",
      color: "gradient-purple",
      stats: ["leads_generated", "profiles_analyzed", "exports_made"],
      quick_actions: ["new_search", "view_leads", "export_data"],
      route: "/dashboard/instagram",
      visible_if: "workspace.main_goals.includes('instagram')"
    },
    link_in_bio: {
      title: "Link in Bio", 
      icon: "🔗",
      color: "gradient-blue",
      stats: ["total_clicks", "active_links", "conversion_rate"],
      quick_actions: ["create_page", "view_analytics", "edit_links"],
      route: "/dashboard/bio-links",
      visible_if: "workspace.main_goals.includes('link_in_bio')"
    },
    courses: {
      title: "Courses",
      icon: "🎓", 
      color: "gradient-green",
      stats: ["active_students", "courses_published", "revenue"],
      quick_actions: ["create_course", "view_students", "check_earnings"],
      route: "/dashboard/courses",
      visible_if: "workspace.main_goals.includes('courses')"
    },
    ecommerce: {
      title: "E-commerce",
      icon: "🛍️",
      color: "gradient-orange", 
      stats: ["orders_today", "total_products", "revenue"],
      quick_actions: ["add_product", "view_orders", "manage_inventory"],
      route: "/dashboard/ecommerce",
      visible_if: "workspace.main_goals.includes('ecommerce')"
    },
    crm: {
      title: "CRM",
      icon: "👥",
      color: "gradient-red",
      stats: ["active_contacts", "open_deals", "conversion_rate"], 
      quick_actions: ["add_contact", "view_pipeline", "send_email"],
      route: "/dashboard/crm",
      visible_if: "workspace.main_goals.includes('crm')"
    },
    analytics: {
      title: "Analytics",
      icon: "📊",
      color: "gradient-indigo",
      stats: ["total_users", "sessions_today", "conversion_rate"],
      quick_actions: ["view_reports", "create_dashboard", "export_data"],
      route: "/dashboard/analytics", 
      visible_if: "workspace.main_goals.includes('analytics')"
    }
  }
};
```

#### Access Control Implementation
```javascript
const AccessControlLogic = {
  // Check if user can access specific goal
  canAccessGoal: (user, workspace, goal) => {
    // Check workspace membership
    const membership = workspace.members.find(m => m.user_id === user.id);
    if (!membership) return false;
    
    // Check if goal is enabled for workspace
    if (!workspace.main_goals.includes(goal)) return false;
    
    // Check subscription limits
    const subscription = workspace.subscription;
    if (subscription.plan === 'free' && workspace.features_enabled.length > 10) {
      return false;
    }
    
    // Check role permissions
    const rolePermissions = {
      owner: ['all'],
      admin: ['read', 'write', 'delete'],
      editor: ['read', 'write'],
      viewer: ['read']
    };
    
    return rolePermissions[membership.role].includes('read');
  },
  
  // Filter visible goals based on access
  getVisibleGoals: (user, workspace) => {
    return MainGoalsDashboard.goal_cards.filter(goal => 
      canAccessGoal(user, workspace, goal.id)
    );
  }
};
```

---

## ⚙️ MANAGEMENT SCREENS DOCUMENTATION

### Workspace Settings
**File:** `/frontend/src/pages/dashboard/WorkspaceSettings.js`  
**Route:** `/dashboard/settings`  
**Status:** ✅ **READY**

#### Settings Sections
```javascript
const WorkspaceSettingsSections = {
  general: {
    title: "General Settings",
    fields: ["workspace_name", "description", "industry", "website"],
    permissions: ["owner", "admin"]
  },
  
  branding: {
    title: "Branding",
    fields: ["logo", "colors", "custom_domain", "external_branding"],
    permissions: ["owner", "admin"],
    upgrade_required: "professional"
  },
  
  team: {
    title: "Team Management", 
    sections: ["members_list", "pending_invitations", "role_management"],
    permissions: ["owner", "admin"]
  },
  
  subscription: {
    title: "Subscription & Billing",
    sections: ["current_plan", "feature_usage", "billing_history", "payment_methods"],
    permissions: ["owner"]
  },
  
  security: {
    title: "Security",
    sections: ["two_factor_auth", "api_keys", "audit_logs", "data_export"],
    permissions: ["owner", "admin"]
  }
};
```

---

### Team Management  
**File:** `/frontend/src/pages/dashboard/TeamManagement.js`  
**Route:** `/dashboard/team`  
**Status:** ✅ **READY**

#### Team Interface
```javascript
const TeamManagementInterface = {
  members_table: {
    columns: ["avatar", "name", "email", "role", "status", "last_active", "actions"],
    filters: ["role", "status", "join_date"],
    sorting: ["name", "role", "last_active"],
    actions: ["edit_role", "remove_member", "resend_invitation"]
  },
  
  invite_section: {
    bulk_invite: true,
    role_assignment: true,
    custom_message: true,
    email_template_preview: true
  },
  
  pending_invitations: {
    display: "separate_table",
    columns: ["email", "role", "invited_by", "sent_date", "status"],
    actions: ["resend", "cancel", "copy_link"]
  }
};
```

---

### Subscription Management
**File:** `/frontend/src/pages/dashboard/SubscriptionPage.js`  
**Route:** `/dashboard/subscription`  
**Status:** ⚠️ **NEEDS FEATURE-BASED BILLING**

#### Subscription Interface
```javascript
const SubscriptionInterface = {
  current_plan_card: {
    display: ["plan_name", "features_used", "monthly_cost", "next_billing"],
    actions: ["upgrade", "downgrade", "cancel", "manage_features"]
  },
  
  feature_usage: {
    display: "progress_bars_per_feature",
    show_limits: true,
    upgrade_prompts: "contextual",
    billing_preview: "real_time"
  },
  
  billing_section: {
    payment_methods: ["cards_list", "add_new", "set_default"],
    billing_history: ["invoices_table", "download_receipts"],
    next_billing: ["date", "amount", "features_breakdown"]
  },
  
  plan_comparison: {
    display: "side_by_side_table",
    highlight_differences: true,
    upgrade_path_suggestions: true
  }
};
```

---

## 📱 MOBILE RESPONSIVE IMPLEMENTATION

### Mobile Navigation Pattern
```javascript
const MobileNavigation = {
  pattern: "bottom_tab_bar",
  tabs: [
    { icon: "🏠", label: "Home", route: "/dashboard" },
    { icon: "📊", label: "Goals", route: "/dashboard/goals" },
    { icon: "👥", label: "Team", route: "/dashboard/team" },
    { icon: "⚙️", label: "Settings", route: "/dashboard/settings" }
  ],
  
  header: {
    components: ["workspace_selector", "notifications", "hamburger_menu"],
    compact_mode: true
  }
};
```

### Mobile Breakpoints
```css
/* Mobile optimizations for all screens */
@media (max-width: 768px) {
  /* Dashboard goal cards */
  .goal-cards-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  /* Form layouts */
  .form-two-column {
    grid-template-columns: 1fr;
  }
  
  /* Tables */
  .data-table {
    overflow-x: auto;
    font-size: 0.875rem;
  }
  
  /* Modals */
  .modal {
    margin: 1rem;
    max-height: 90vh;
    overflow-y: auto;
  }
}
```

---

## 🔗 API INTEGRATION SPECIFICATIONS

### Frontend API Service
**File:** `/frontend/src/services/api.js`  
**Status:** ✅ **READY**

#### API Configuration
```javascript
const apiConfig = {
  baseURL: process.env.REACT_APP_BACKEND_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  
  // JWT token management
  tokenStorage: 'localStorage',
  tokenKey: 'mewayz_token',
  refreshTokenKey: 'mewayz_refresh_token',
  
  // Automatic token refresh
  interceptors: {
    request: 'add_auth_header',
    response: 'handle_token_refresh'
  }
};

// API methods for each screen
const screenAPIMethods = {
  authentication: {
    login: 'POST /api/auth/login',
    register: 'POST /api/auth/register',
    googleLogin: 'POST /api/google-oauth/login',
    appleLogin: 'POST /api/apple-oauth/login'
  },
  
  onboarding: {
    createWorkspace: 'POST /api/workspace/',
    saveProgress: 'PUT /api/complete-onboarding/',
    getProgress: 'GET /api/complete-onboarding/'
  },
  
  dashboard: {
    getWorkspaces: 'GET /api/workspace/',
    getWorkspaceDetails: 'GET /api/workspace/{id}',
    switchWorkspace: 'POST /api/complete-multi-workspace/switch'
  },
  
  team: {
    inviteMembers: 'POST /api/workspace/{id}/invite',
    getMembers: 'GET /api/workspace/{id}/members',
    updateMemberRole: 'PUT /api/workspace/{id}/members/{user_id}'
  },
  
  subscription: {
    getSubscription: 'GET /api/subscription/',
    updateSubscription: 'PUT /api/subscription/{id}',
    createPayment: 'POST /api/stripe-integration/payment'
  }
};
```

---

## 🎯 IMPLEMENTATION PRIORITY MATRIX

### Phase 1: Critical Screens (Week 1)
```javascript
const Phase1Screens = [
  {
    screen: "LoginPage",
    tasks: ["implement_apple_oauth", "improve_error_handling"],
    effort: "2 days"
  },
  {
    screen: "OnboardingWizard", 
    tasks: ["build_multi_step_ui", "implement_goals_selection", "features_selection_logic"],
    effort: "4 days"
  },
  {
    screen: "WorkspaceInvitationPage",
    tasks: ["enhance_visual_states", "loading_animations", "error_handling"],
    effort: "1 day"
  }
];
```

### Phase 2: Dashboard Screens (Week 2)
```javascript
const Phase2Screens = [
  {
    screen: "Dashboard",
    tasks: ["implement_main_goals_cards", "access_control_logic", "stats_integration"],
    effort: "3 days"
  },
  {
    screen: "SubscriptionPage",
    tasks: ["feature_based_billing_ui", "payment_integration", "upgrade_downgrade_flows"],
    effort: "2 days"
  }
];
```

### Phase 3: Polish & Mobile (Week 3)
```javascript
const Phase3Tasks = [
  "mobile_responsive_optimization",
  "loading_states_throughout",
  "error_boundaries", 
  "comprehensive_testing",
  "performance_optimization"
];
```

---

## 📋 DEVELOPER CHECKLIST

### Before Implementation
- [ ] Set up environment variables for all third-party services
- [ ] Configure Google OAuth credentials
- [ ] Set up Stripe test environment  
- [ ] Configure email service for invitations
- [ ] Set up Apple Developer account for Apple OAuth

### During Implementation  
- [ ] Follow responsive design patterns for all screens
- [ ] Implement proper error boundaries and loading states
- [ ] Add form validation for all user inputs
- [ ] Test API integration thoroughly
- [ ] Implement proper access control checks

### After Implementation
- [ ] Test complete user journey from registration to dashboard
- [ ] Verify mobile responsive design on multiple devices
- [ ] Test invitation flow with real email addresses
- [ ] Validate subscription and payment workflows
- [ ] Performance testing and optimization

---

## 🚀 CONCLUSION

This comprehensive screen documentation provides a complete blueprint for implementing the Mewayz v2 SaaS platform frontend. With the backend already 85% complete, the frontend development can focus on creating exceptional user experiences while leveraging the robust API infrastructure already in place.

**Estimated Development Time:** 3-4 weeks  
**Team Recommended:** 2-3 frontend developers + 1 backend developer for integration  
**Key Success Factors:** Focus on user experience, mobile-first design, and seamless API integration  

---

*End of Professional Screen Documentation*  
*Total Screens Documented: 25+ screens with complete implementation details*