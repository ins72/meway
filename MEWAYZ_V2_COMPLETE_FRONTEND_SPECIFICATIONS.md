# MEWAYZ V2 COMPLETE FRONTEND SPECIFICATIONS - REBUILT
## Modern, Clean Design Based on Landing Page Theme

**Documentation Date:** December 30, 2024  
**Design Foundation:** Based on MEWAYZ_V2_REACT_LANDING_PAGE.jsx theme and styling  
**Scope:** Complete UI/UX specifications with workspace-based access control  
**Design Philosophy:** Modern, gradient-based, glassmorphism with dark/light theme support

---

## 🎨 CORE DESIGN SYSTEM

### **Design Foundation & Theme**
Based on the existing landing page design system with consistent styling throughout all applications.

#### **Color Palette:**
```css
:root {
  /* Dark Theme (Primary) */
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card: rgba(18, 18, 26, 0.8);
  --bg-glass: rgba(255, 255, 255, 0.03);
  --text-primary: #ffffff;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;
  
  /* Gradient System */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --gradient-warm: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  --gradient-cool: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  
  /* Effects */
  --shadow-glow: 0 0 40px rgba(102, 126, 234, 0.15);
  --shadow-card: 0 20px 40px -15px rgba(0, 0, 0, 0.3);
  --border: rgba(255, 255, 255, 0.08);
  --border-light: rgba(255, 255, 255, 0.15);
}

/* Light Theme */
[data-theme="light"] {
  --bg-primary: #fafafa;
  --bg-secondary: #ffffff;
  --bg-card: rgba(255, 255, 255, 0.9);
  --bg-glass: rgba(0, 0, 0, 0.02);
  --text-primary: #1a1a1a;
  --text-secondary: #525252;
  --text-muted: #737373;
  --border: rgba(0, 0, 0, 0.08);
  --border-light: rgba(0, 0, 0, 0.12);
  --shadow-card: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
}
```

#### **Typography System:**
```css
/* Font Stack */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
font-family-mono: 'JetBrains Mono', monospace; /* For logo and code */

/* Typography Scale */
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */
```

#### **Component Library:**
```css
/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-glow);
}

.btn-secondary {
  background: var(--bg-glass);
  color: var(--text-primary);
  border: 1px solid var(--border);
  backdrop-filter: blur(20px);
}

/* Cards */
.card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow-card);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

/* Glass Effect */
.glass {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
}
```

---

## 🏠 PUBLIC PAGES & AUTHENTICATION

### **1. Landing Page** ✅ COMPLETE
**File:** `/frontend/src/pages/LandingPage.js`  
**Route:** `/`  
**Theme:** Modern glassmorphism with floating shapes and gradient elements

#### **Landing Page Structure:**
- **Header:** Fixed with backdrop blur, logo with gradient text, theme toggle
- **Hero:** Gradient badge, large heading with gradient text, dual CTA buttons
- **Features:** Glass cards with hover animations and gradient accents
- **Testimonials:** Glassmorphism cards with customer photos and gradient borders
- **Pricing:** Cards with gradient borders and glow effects on hover
- **Footer:** Dark with subtle borders and gradient logo

### **2. Authentication Screens**

#### **2.1 Login Page**
**File:** `/frontend/src/pages/auth/LoginPage.js`  
**Route:** `/login`  
**Design:** Split-screen layout with glassmorphism form

```javascript
const LoginPageDesign = {
  layout: {
    desktop: "split_screen", // Left: branding, Right: form
    mobile: "single_column", // Full-width form with header
    background: "floating_shapes_subtle"
  },
  
  left_panel: {
    background: "var(--gradient-primary)",
    content: [
      { element: "logo", size: "large", color: "white" },
      { element: "heading", text: "Welcome back to Mewayz", style: "text-4xl font-bold" },
      { element: "description", text: "Access your all-in-one business platform" },
      { element: "features_list", items: ["62 Integrated APIs", "Multi-workspace support", "Real-time analytics"] },
      { element: "testimonial_quote", rotating: true }
    ]
  },
  
  right_panel: {
    background: "var(--bg-card)",
    backdrop_filter: "blur(20px)",
    form: {
      title: "Sign in to your account",
      fields: [
        { 
          type: "email", 
          placeholder: "Enter your email",
          icon: "mail",
          validation: "real_time"
        },
        { 
          type: "password", 
          placeholder: "Enter your password",
          icon: "lock",
          toggle_visibility: true
        }
      ],
      
      actions: [
        { 
          type: "primary_button", 
          text: "Sign In",
          style: "btn-primary gradient",
          full_width: true
        },
        { 
          type: "forgot_password", 
          text: "Forgot your password?",
          style: "link gradient-text"
        }
      ],
      
      social_login: {
        divider: "Or continue with",
        providers: [
          { provider: "google", icon: "google", text: "Continue with Google" },
          { provider: "apple", icon: "apple", text: "Continue with Apple" }
        ]
      },
      
      footer: {
        text: "Don't have an account?",
        link: { text: "Sign up", route: "/register", style: "gradient-text" }
      }
    }
  }
};
```

#### **2.2 Registration Page**
**File:** `/frontend/src/pages/auth/RegisterPage.js`  
**Route:** `/register`  
**Design:** Similar split-screen with multi-step wizard

```javascript
const RegisterPageDesign = {
  layout: "split_screen",
  wizard_steps: [
    {
      step: 1,
      title: "Create your account",
      fields: [
        { type: "text", placeholder: "Full Name", icon: "user" },
        { type: "email", placeholder: "Email Address", icon: "mail" },
        { type: "password", placeholder: "Password", icon: "lock", strength_meter: true },
        { type: "password", placeholder: "Confirm Password", icon: "lock" }
      ],
      validation: "real_time",
      progress_indicator: "1/3"
    },
    {
      step: 2,
      title: "Verify your email",
      content: "verification_code_input",
      resend_option: true,
      progress_indicator: "2/3"
    },
    {
      step: 3,
      title: "Account created successfully!",
      content: "success_animation",
      cta: { text: "Continue to Workspace Setup", route: "/onboarding" },
      progress_indicator: "3/3"
    }
  ]
};
```

---

## 🚀 ONBOARDING EXPERIENCE

### **Multi-Step Workspace Setup Wizard**
**File:** `/frontend/src/pages/onboarding/OnboardingWizard.js`  
**Route:** `/onboarding`  
**Design:** Full-screen wizard with glassmorphism cards and gradient progress

#### **Step 1: Workspace Creation**
```javascript
const WorkspaceSetupStep = {
  layout: {
    background: "floating_shapes",
    main_card: "centered_glass_card",
    progress_bar: "gradient_progress_top"
  },
  
  content: {
    header: {
      title: "Let's set up your workspace",
      subtitle: "Your personalized business command center",
      icon: "briefcase_gradient"
    },
    
    form: {
      fields: [
        { 
          type: "text", 
          label: "Workspace Name",
          placeholder: "e.g., Acme Marketing Agency",
          icon: "building",
          required: true
        },
        { 
          type: "textarea", 
          label: "Description (Optional)",
          placeholder: "Brief description of your business...",
          rows: 3
        },
        { 
          type: "select", 
          label: "Industry",
          placeholder: "Select your industry...",
          options: "industry_list_with_icons"
        },
        { 
          type: "url", 
          label: "Website (Optional)",
          placeholder: "https://yourwebsite.com",
          icon: "globe"
        }
      ]
    },
    
    navigation: {
      skip: { text: "Skip for now", style: "text-link" },
      continue: { text: "Continue", style: "btn-primary gradient" }
    }
  }
};
```

#### **Step 2: Business Goals Selection**
```javascript
const BusinessGoalsStep = {
  layout: {
    title: "What are your main business goals?",
    subtitle: "Select all that apply - we'll customize your experience",
    grid: "responsive_card_grid"
  },
  
  goal_cards: [
    {
      id: "social_media",
      title: "Social Media Growth",
      description: "Grow followers, engagement, and leads",
      icon: "users_gradient",
      gradient: "var(--gradient-primary)",
      features_preview: ["Instagram database", "Content scheduling", "Analytics"]
    },
    {
      id: "ecommerce",
      title: "E-commerce Sales",
      description: "Sell products and manage inventory",
      icon: "shopping_cart_gradient",
      gradient: "var(--gradient-accent)",
      features_preview: ["Online store", "Payment processing", "Order management"]
    },
    {
      id: "content_creation",
      title: "Content & Courses",
      description: "Create and monetize educational content",
      icon: "video_gradient",
      gradient: "var(--gradient-warm)",
      features_preview: ["Course builder", "Student management", "Content library"]
    },
    {
      id: "client_management",
      title: "Client & CRM",
      description: "Manage relationships and sales pipeline",
      icon: "handshake_gradient",
      gradient: "var(--gradient-secondary)",
      features_preview: ["Contact management", "Pipeline tracking", "Task automation"]
    },
    {
      id: "marketing",
      title: "Marketing Campaigns",
      description: "Email, ads, and campaign management",
      icon: "megaphone_gradient",
      gradient: "var(--gradient-cool)",
      features_preview: ["Email marketing", "Campaign tracking", "Lead generation"]
    },
    {
      id: "analytics",
      title: "Business Analytics",
      description: "Track performance and make data-driven decisions",
      icon: "chart_gradient",
      gradient: "var(--gradient-primary)",
      features_preview: ["Revenue tracking", "Performance metrics", "Custom reports"]
    }
  ],
  
  card_interaction: {
    hover_effect: "lift_and_glow",
    selection_effect: "gradient_border",
    multi_select: true,
    minimum_selection: 1
  }
};
```

#### **Step 3: Plan Selection**
```javascript
const PlanSelectionStep = {
  layout: {
    title: "Choose your plan",
    subtitle: "Based on your goals, here are our recommendations",
    cards_layout: "three_column_responsive"
  },
  
  pricing_cards: [
    {
      plan: "Free",
      recommended: false,
      price: "$0",
      period: "forever",
      description: "Perfect for getting started",
      gradient_border: false,
      features: [
        "10 features included",
        "1 workspace",
        "Basic analytics",
        "Community support"
      ],
      cta: { text: "Start Free", style: "btn-secondary" }
    },
    {
      plan: "Creator",
      recommended: true,
      price: "$19",
      period: "per month",
      description: "Most popular for creators",
      gradient_border: "var(--gradient-primary)",
      badge: "RECOMMENDED",
      features: [
        "25+ features included",
        "3 workspaces",
        "Advanced analytics",
        "Priority support",
        "AI content generation",
        "Social media tools"
      ],
      cta: { text: "Start 14-day Free Trial", style: "btn-primary gradient" }
    },
    {
      plan: "Business",
      recommended: false,
      price: "$39",
      period: "per month",
      description: "Full business management",
      gradient_border: false,
      features: [
        "All features included",
        "Unlimited workspaces",
        "Team collaboration",
        "Advanced integrations",
        "Custom branding",
        "API access"
      ],
      cta: { text: "Start Trial", style: "btn-secondary" }
    }
  ],
  
  billing_toggle: {
    monthly: "Monthly billing",
    yearly: "Yearly billing (Save 20%)",
    default: "monthly"
  }
};
```

#### **Step 4: Workspace Customization**
```javascript
const WorkspaceCustomizationStep = {
  layout: {
    title: "Customize your workspace",
    subtitle: "Make it yours with colors and branding",
    split_view: true // Left: settings, Right: preview
  },
  
  customization_options: {
    theme_selection: {
      title: "Choose Theme",
      options: [
        { theme: "dark", name: "Dark Mode", preview: "dark_preview" },
        { theme: "light", name: "Light Mode", preview: "light_preview" },
        { theme: "system", name: "System", preview: "auto_preview" }
      ]
    },
    
    color_scheme: {
      title: "Brand Colors",
      primary_color: {
        label: "Primary Color",
        default: "#667eea",
        picker: "gradient_color_picker"
      },
      accent_color: {
        label: "Accent Color", 
        default: "#4facfe",
        picker: "gradient_color_picker"
      }
    },
    
    logo_upload: {
      title: "Workspace Logo",
      upload_area: "drag_drop_with_preview",
      formats: ["PNG", "JPG", "SVG"],
      size_limit: "2MB",
      dimensions: "Recommended: 200x200px"
    }
  },
  
  preview_panel: {
    title: "Live Preview",
    preview_components: [
      "navigation_bar",
      "sidebar",
      "main_content_area",
      "cards_with_selected_colors"
    ]
  }
};
```

---

## 🏢 MAIN APPLICATION INTERFACE

### **Application Shell**
**File:** `/frontend/src/layouts/AppShell.js`  
**Design:** Modern sidebar + header layout with glassmorphism

#### **Navigation Structure:**
```javascript
const AppShellDesign = {
  layout: {
    structure: "sidebar_with_header",
    sidebar_width: "280px",
    header_height: "64px",
    main_content: "flexible_with_padding"
  },
  
  header: {
    background: "rgba(18, 18, 26, 0.9)",
    backdrop_filter: "blur(20px)",
    border_bottom: "1px solid var(--border)",
    
    left_section: {
      workspace_selector: {
        type: "dropdown_with_avatar",
        style: "glass_button",
        avatar: "workspace_logo",
        name: "workspace_name",
        role_indicator: true,
        dropdown_style: "glassmorphism_menu"
      }
    },
    
    center_section: {
      global_search: {
        placeholder: "Search features, content, people...",
        style: "glass_search_bar",
        icon: "search_gradient",
        shortcut: "Cmd+K",
        width: "400px"
      }
    },
    
    right_section: {
      components: [
        { 
          component: "notifications", 
          icon: "bell_gradient", 
          badge: "unread_count",
          dropdown: "notifications_panel"
        },
        { 
          component: "theme_toggle", 
          icon: "theme_icon",
          style: "glass_button"
        },
        { 
          component: "user_menu", 
          avatar: "user_photo",
          dropdown: "user_menu_panel"
        }
      ]
    }
  },
  
  sidebar: {
    background: "var(--bg-secondary)",
    border_right: "1px solid var(--border)",
    
    sections: [
      {
        section: "main_navigation",
        items: [
          { 
            label: "Overview", 
            icon: "home_gradient", 
            route: "/app",
            badge: null
          },
          { 
            label: "Social Media", 
            icon: "users_gradient", 
            route: "/app/social",
            badge: "3"
          },
          { 
            label: "E-commerce", 
            icon: "shopping_gradient", 
            route: "/app/ecommerce",
            badge: null
          },
          { 
            label: "Content & Courses", 
            icon: "video_gradient", 
            route: "/app/content",
            badge: null
          },
          { 
            label: "CRM & Contacts", 
            icon: "contacts_gradient", 
            route: "/app/crm",
            badge: "12"
          },
          { 
            label: "Analytics", 
            icon: "chart_gradient", 
            route: "/app/analytics",
            badge: null
          }
        ]
      },
      {
        section: "quick_actions",
        title: "Quick Actions",
        items: [
          { label: "Create Post", icon: "plus_gradient", action: "create_post_modal" },
          { label: "Add Contact", icon: "user_plus_gradient", action: "add_contact_modal" },
          { label: "New Campaign", icon: "megaphone_gradient", action: "create_campaign_modal" }
        ]
      },
      {
        section: "workspace_settings",
        items: [
          { label: "Settings", icon: "settings_gradient", route: "/app/settings" },
          { label: "Team", icon: "team_gradient", route: "/app/team" },
          { label: "Billing", icon: "credit_card_gradient", route: "/app/billing" }
        ]
      }
    ]
  }
};
```

### **Overview Page (App Home)**
**File:** `/frontend/src/pages/app/OverviewPage.js`  
**Route:** `/app`  
**Design:** Modern cards with metrics and quick actions

```javascript
const OverviewPageDesign = {
  layout: {
    background: "var(--bg-primary)",
    content_max_width: "1400px",
    padding: "2rem",
    grid: "responsive_grid"
  },
  
  header_section: {
    greeting: {
      title: "Good morning, [User Name]",
      subtitle: "Here's what's happening with [Workspace Name]",
      style: "text-2xl font-semibold"
    },
    
    quick_stats: {
      layout: "four_cards_row",
      cards: [
        {
          title: "Total Revenue",
          value: "$12,450",
          change: "+18.3%",
          period: "vs last month",
          icon: "dollar_sign_gradient",
          gradient: "var(--gradient-primary)"
        },
        {
          title: "New Contacts",
          value: "247",
          change: "+25.1%",
          period: "this week",
          icon: "users_gradient",
          gradient: "var(--gradient-accent)"
        },
        {
          title: "Campaign Performance",
          value: "94.2%",
          change: "+5.7%",
          period: "open rate",
          icon: "trending_up_gradient",
          gradient: "var(--gradient-warm)"
        },
        {
          title: "Content Views",
          value: "8,945",
          change: "+12.4%",
          period: "this month",
          icon: "eye_gradient",
          gradient: "var(--gradient-cool)"
        }
      ]
    }
  },
  
  main_content: {
    left_column: {
      width: "60%",
      components: [
        {
          component: "recent_activity",
          title: "Recent Activity",
          style: "glass_card",
          timeline: true,
          activities: [
            { type: "sale", title: "New order received", time: "2 minutes ago", icon: "shopping_cart" },
            { type: "contact", title: "3 new contacts added", time: "1 hour ago", icon: "user_plus" },
            { type: "campaign", title: "Email campaign sent", time: "3 hours ago", icon: "mail" }
          ]
        },
        {
          component: "performance_chart",
          title: "Revenue Trends",
          style: "glass_card",
          chart_type: "area_chart",
          period: "30_days",
          gradient_fill: "var(--gradient-primary)"
        }
      ]
    },
    
    right_column: {
      width: "40%",
      components: [
        {
          component: "goals_progress",
          title: "Monthly Goals",
          style: "glass_card",
          goals: [
            { label: "Revenue Target", current: 8450, target: 10000, unit: "$" },
            { label: "New Contacts", current: 247, target: 300, unit: "" },
            { label: "Content Published", current: 12, target: 20, unit: " posts" }
          ]
        },
        {
          component: "quick_actions",
          title: "Quick Actions",
          style: "glass_card",
          actions: [
            { label: "Create Social Post", icon: "camera", style: "btn-primary gradient" },
            { label: "Send Email Campaign", icon: "mail", style: "btn-secondary glass" },
            { label: "Add New Product", icon: "plus", style: "btn-secondary glass" },
            { label: "Schedule Meeting", icon: "calendar", style: "btn-secondary glass" }
          ]
        },
        {
          component: "team_activity",
          title: "Team Activity",
          style: "glass_card",
          members: [
            { name: "Sarah Chen", action: "Added 5 new products", time: "30m ago", avatar: "avatar_url" },
            { name: "Mike Johnson", action: "Completed email campaign", time: "2h ago", avatar: "avatar_url" }
          ]
        }
      ]
    }
  }
};
```

---

## 📱 FEATURE MODULES

### **Social Media Management**
**File:** `/frontend/src/pages/app/SocialMediaPage.js`  
**Route:** `/app/social`  
**Design:** Unified interface with glassmorphism cards

#### **Social Media Hub:**
```javascript
const SocialMediaPageDesign = {
  header: {
    title: "Social Media Management",
    subtitle: "Grow your audience across all platforms",
    actions: [
      { label: "Create Post", style: "btn-primary gradient", icon: "plus" },
      { label: "Schedule Campaign", style: "btn-secondary glass", icon: "calendar" }
    ]
  },
  
  tabs: {
    style: "glass_tabs_with_gradient_indicator",
    tabs: [
      { id: "dashboard", label: "Dashboard", icon: "home" },
      { id: "content", label: "Content", icon: "image" },
      { id: "analytics", label: "Analytics", icon: "chart" },
      { id: "leads", label: "Lead Database", icon: "users" }
    ]
  },
  
  dashboard_tab: {
    metrics_grid: {
      cards: [
        {
          platform: "Instagram",
          followers: "12.5K",
          engagement: "4.8%",
          gradient: "var(--gradient-primary)",
          icon: "instagram"
        },
        {
          platform: "Twitter",
          followers: "8.2K", 
          engagement: "3.2%",
          gradient: "var(--gradient-accent)",
          icon: "twitter"
        },
        {
          platform: "TikTok",
          followers: "25.1K",
          engagement: "7.1%",
          gradient: "var(--gradient-warm)",
          icon: "tiktok"
        },
        {
          platform: "LinkedIn",
          followers: "3.4K",
          engagement: "5.9%",
          gradient: "var(--gradient-cool)", 
          icon: "linkedin"
        }
      ]
    },
    
    recent_posts: {
      title: "Recent Posts",
      style: "glass_card",
      layout: "grid_with_hover_effects",
      posts: [
        {
          image: "post_thumbnail",
          caption: "post_preview_text",
          platform: "platform_icon",
          engagement: "likes_comments_shares",
          date: "relative_time"
        }
      ]
    },
    
    content_calendar: {
      title: "Content Calendar",
      style: "glass_card",
      view: "mini_calendar_with_posts",
      upcoming_posts: "sidebar_list"
    }
  },
  
  content_tab: {
    content_library: {
      search_bar: {
        placeholder: "Search content...",
        style: "glass_search_bar",
        filters: ["All", "Images", "Videos", "Templates"]
      },
      
      upload_area: {
        style: "glass_card_with_gradient_border", 
        drag_drop: true,
        supported_formats: ["JPG", "PNG", "MP4", "GIF"]
      },
      
      content_grid: {
        style: "masonry_grid",
        item_style: "glass_card_hover_lift",
        preview_modal: "glassmorphism_modal"
      }
    }
  },
  
  analytics_tab: {
    performance_charts: {
      layout: "two_column_charts",
      charts: [
        {
          title: "Engagement Over Time",
          type: "line_chart",
          gradient_fill: "var(--gradient-primary)",
          style: "glass_card"
        },
        {
          title: "Top Performing Content",
          type: "bar_chart",
          gradient_fill: "var(--gradient-accent)",
          style: "glass_card"
        }
      ]
    }
  }
};
```

### **E-commerce Management**
**File:** `/frontend/src/pages/app/EcommercePage.js`  
**Route:** `/app/ecommerce`  
**Design:** Store management with modern card layouts

```javascript
const EcommercePageDesign = {
  header: {
    title: "E-commerce Store",
    subtitle: "Manage your online store and orders",
    actions: [
      { label: "Add Product", style: "btn-primary gradient", icon: "plus" },
      { label: "View Store", style: "btn-secondary glass", icon: "external-link" }
    ]
  },
  
  store_overview: {
    metrics_cards: [
      {
        title: "Total Revenue",
        value: "$24,580",
        change: "+12.5%",
        period: "this month",
        icon: "dollar_sign_gradient",
        gradient: "var(--gradient-primary)"
      },
      {
        title: "Orders",
        value: "143",
        change: "+18.2%",
        period: "this week",
        icon: "shopping_bag_gradient",
        gradient: "var(--gradient-accent)"
      },
      {
        title: "Products",
        value: "89",
        change: "+5",
        period: "active",
        icon: "package_gradient",
        gradient: "var(--gradient-warm)"
      },
      {
        title: "Conversion Rate",
        value: "3.4%",
        change: "+0.8%",
        period: "vs last month",
        icon: "trending_up_gradient",
        gradient: "var(--gradient-cool)"
      }
    ]
  },
  
  main_content: {
    left_panel: {
      width: "70%",
      components: [
        {
          component: "recent_orders",
          title: "Recent Orders",
          style: "glass_card",
          table_style: "modern_table_with_hover",
          columns: ["Order ID", "Customer", "Amount", "Status", "Date"],
          row_actions: ["View", "Update Status", "Print Invoice"]
        },
        {
          component: "sales_chart",
          title: "Sales Performance",
          style: "glass_card",
          chart_type: "area_chart_with_gradient",
          period_selector: ["7d", "30d", "90d", "1y"]
        }
      ]
    },
    
    right_panel: {
      width: "30%",
      components: [
        {
          component: "inventory_alerts",
          title: "Inventory Alerts",
          style: "glass_card",
          alerts: [
            { product: "Product Name", stock: 3, level: "low", color: "orange" },
            { product: "Another Product", stock: 0, level: "out", color: "red" }
          ]
        },
        {
          component: "top_products",
          title: "Top Selling Products",
          style: "glass_card", 
          products: [
            { name: "Product A", sales: 45, revenue: "$1,230" },
            { name: "Product B", sales: 32, revenue: "$890" }
          ]
        }
      ]
    }
  }
};
```

### **Content & Courses**
**File:** `/frontend/src/pages/app/ContentPage.js`  
**Route:** `/app/content`  
**Design:** Content creation hub with modern interface

```javascript
const ContentPageDesign = {
  header: {
    title: "Content & Courses",
    subtitle: "Create, manage, and monetize your content",
    actions: [
      { label: "Create Course", style: "btn-primary gradient", icon: "video" },
      { label: "New Article", style: "btn-secondary glass", icon: "edit" }
    ]
  },
  
  content_overview: {
    stats_grid: [
      {
        title: "Published Courses",
        value: "12",
        subtitle: "8 active enrollments",
        icon: "graduation_cap_gradient",
        gradient: "var(--gradient-primary)"
      },
      {
        title: "Total Students",
        value: "1,247",
        subtitle: "+89 this month",
        icon: "users_gradient",
        gradient: "var(--gradient-accent)"
      },
      {
        title: "Course Revenue",
        value: "$8,945",
        subtitle: "+23% vs last month",
        icon: "dollar_sign_gradient",
        gradient: "var(--gradient-warm)"
      },
      {
        title: "Completion Rate",
        value: "87%",
        subtitle: "Above average",
        icon: "check_circle_gradient",
        gradient: "var(--gradient-cool)"
      }
    ]
  },
  
  tabs: {
    style: "glass_tabs",
    tabs: [
      { id: "courses", label: "Courses", icon: "video" },
      { id: "articles", label: "Articles", icon: "file-text" },
      { id: "templates", label: "Templates", icon: "layout" },
      { id: "analytics", label: "Analytics", icon: "chart" }
    ]
  },
  
  courses_tab: {
    course_grid: {
      style: "responsive_card_grid",
      card_design: {
        thumbnail: "course_preview_image",
        title: "course_title",
        students: "enrolled_count",
        revenue: "total_earnings",
        status: "published_draft_badge",
        actions: ["Edit", "View Analytics", "Manage Students"],
        hover_effect: "lift_and_glow"
      }
    },
    
    course_builder: {
      trigger: "Create Course button",
      modal_style: "full_screen_glassmorphism",
      steps: [
        { step: "Basic Info", fields: ["title", "description", "category", "price"] },
        { step: "Curriculum", interface: "drag_drop_lesson_builder" },
        { step: "Settings", fields: ["enrollment_settings", "certificates", "community"] }
      ]
    }
  }
};
```

---

## ⚙️ WORKSPACE SETTINGS & MANAGEMENT

### **Settings Page**
**File:** `/frontend/src/pages/app/SettingsPage.js`  
**Route:** `/app/settings`  
**Design:** Tabbed settings with glassmorphism panels

```javascript
const SettingsPageDesign = {
  layout: {
    structure: "sidebar_tabs_with_content",
    sidebar_width: "280px",
    content_width: "flexible"
  },
  
  sidebar_navigation: {
    style: "glass_sidebar",
    sections: [
      {
        section: "Workspace",
        items: [
          { label: "General", icon: "settings", active: true },
          { label: "Branding", icon: "palette" },
          { label: "Integrations", icon: "link" },
          { label: "API Keys", icon: "key" }
        ]
      },
      {
        section: "Account",
        items: [
          { label: "Profile", icon: "user" },
          { label: "Security", icon: "shield" },
          { label: "Notifications", icon: "bell" },
          { label: "Billing", icon: "credit-card" }
        ]
      },
      {
        section: "Team",
        items: [
          { label: "Members", icon: "users" },
          { label: "Roles & Permissions", icon: "lock" },
          { label: "Invitations", icon: "user-plus" }
        ]
      }
    ]
  },
  
  general_settings: {
    sections: [
      {
        title: "Workspace Information",
        style: "glass_card",
        fields: [
          { 
            label: "Workspace Name",
            type: "text",
            value: "current_workspace_name",
            placeholder: "Enter workspace name..."
          },
          { 
            label: "Description",
            type: "textarea",
            value: "current_description",
            placeholder: "Describe your workspace..."
          },
          { 
            label: "Industry",
            type: "select",
            value: "current_industry",
            options: "industry_options"
          },
          { 
            label: "Website",
            type: "url",
            value: "current_website",
            placeholder: "https://..."
          }
        ]
      },
      {
        title: "Preferences",
        style: "glass_card",
        fields: [
          {
            label: "Theme",
            type: "radio_group",
            options: [
              { value: "dark", label: "Dark", preview: "dark_theme_preview" },
              { value: "light", label: "Light", preview: "light_theme_preview" },
              { value: "system", label: "System", preview: "auto_theme_preview" }
            ]
          },
          {
            label: "Language",
            type: "select",
            value: "current_language",
            options: ["English", "Spanish", "French", "German"]
          },
          {
            label: "Timezone",
            type: "timezone_select",
            value: "current_timezone"
          }
        ]
      }
    ]
  },
  
  branding_settings: {
    sections: [
      {
        title: "Logo & Visual Identity",
        style: "glass_card",
        components: [
          {
            component: "logo_upload",
            current_logo: "workspace_logo_url",
            upload_area: "drag_drop_with_preview",
            formats: ["PNG", "JPG", "SVG"],
            recommendations: "200x200px, transparent background"
          },
          {
            component: "color_scheme",
            primary_color: {
              label: "Primary Color",
              current: "current_primary_color",
              picker: "gradient_color_picker"
            },
            accent_color: {
              label: "Accent Color", 
              current: "current_accent_color",
              picker: "gradient_color_picker"
            },
            preview: "live_preview_panel"
          }
        ]
      },
      {
        title: "Custom Domain",
        style: "glass_card",
        description: "Use your own domain for your public pages",
        fields: [
          {
            label: "Domain",
            type: "text",
            placeholder: "your-domain.com",
            validation: "domain_validation",
            status_indicator: true
          }
        ],
        setup_guide: "DNS configuration instructions"
      }
    ]
  }
};
```

---

## 🎨 COMPONENT SPECIFICATIONS

### **Reusable UI Components**

#### **Glass Card Component**
```javascript
const GlassCard = {
  style: {
    background: "var(--bg-card)",
    backdrop_filter: "blur(20px)",
    border: "1px solid var(--border)",
    border_radius: "1rem",
    box_shadow: "var(--shadow-card)",
    padding: "1.5rem",
    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
  },
  
  hover_effects: {
    transform: "translateY(-4px)",
    box_shadow: "var(--shadow-glow)",
    border_color: "var(--border-light)"
  },
  
  variants: [
    { name: "default", padding: "1.5rem" },
    { name: "compact", padding: "1rem" },
    { name: "large", padding: "2rem" },
    { name: "gradient-border", border: "gradient_border" }
  ]
};
```

#### **Gradient Button Component**
```javascript
const GradientButton = {
  base_style: {
    padding: "0.75rem 1.5rem",
    border_radius: "0.5rem",
    font_weight: "500",
    border: "none",
    cursor: "pointer",
    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    display: "inline-flex",
    align_items: "center",
    gap: "0.5rem"
  },
  
  variants: {
    primary: {
      background: "var(--gradient-primary)",
      color: "white",
      box_shadow: "var(--shadow-glow)",
      hover: {
        transform: "translateY(-2px)",
        box_shadow: "0 0 60px rgba(102, 126, 234, 0.25)"
      }
    },
    secondary: {
      background: "var(--bg-glass)",
      color: "var(--text-primary)",
      border: "1px solid var(--border)",
      backdrop_filter: "blur(20px)",
      hover: {
        border_color: "var(--border-light)",
        background: "rgba(255, 255, 255, 0.08)"
      }
    }
  }
};
```

#### **Navigation Component**
```javascript
const NavigationComponent = {
  sidebar_style: {
    background: "var(--bg-secondary)",
    border_right: "1px solid var(--border)",
    backdrop_filter: "blur(20px)"
  },
  
  nav_item: {
    base_style: {
      padding: "0.75rem 1rem",
      border_radius: "0.5rem",
      margin: "0.25rem 0",
      transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      display: "flex",
      align_items: "center",
      gap: "0.75rem"
    },
    
    states: {
      default: {
        color: "var(--text-secondary)",
        hover: {
          background: "var(--bg-glass)",
          color: "var(--text-primary)"
        }
      },
      active: {
        background: "var(--gradient-primary)",
        color: "white",
        box_shadow: "var(--shadow-glow)"
      }
    }
  },
  
  nav_icon: {
    size: "20px",
    gradient_icons: true,
    icon_style: "outlined"
  }
};
```

---

## 📱 RESPONSIVE DESIGN SYSTEM

### **Breakpoints**
```css
/* Mobile First Approach */
:root {
  --breakpoint-xs: 320px;   /* Small phones */
  --breakpoint-sm: 576px;   /* Large phones */
  --breakpoint-md: 768px;   /* Tablets */
  --breakpoint-lg: 992px;   /* Small desktops */
  --breakpoint-xl: 1200px;  /* Large desktops */
  --breakpoint-2xl: 1400px; /* Extra large screens */
}
```

### **Mobile Adaptations**
```javascript
const MobileAdaptations = {
  navigation: {
    mobile: "bottom_tab_bar",
    tablet: "collapsible_sidebar",
    desktop: "full_sidebar"
  },
  
  cards: {
    mobile: "single_column_stack",
    tablet: "two_column_grid", 
    desktop: "multi_column_grid"
  },
  
  modals: {
    mobile: "full_screen_overlay",
    tablet: "large_centered_modal",
    desktop: "standard_modal"
  },
  
  forms: {
    mobile: "single_column_layout",
    tablet: "two_column_layout",
    desktop: "optimized_multi_column"
  }
};
```

---

## 🎯 IMPLEMENTATION SUMMARY

### **Development Roadmap**
1. **Phase 1 (Weeks 1-2):** Authentication + Onboarding + App Shell
2. **Phase 2 (Weeks 3-4):** Overview Page + Settings + Core Navigation  
3. **Phase 3 (Weeks 5-8):** Feature Modules (Social, E-commerce, Content)
4. **Phase 4 (Weeks 9-10):** Mobile Optimization + Polish
5. **Phase 5 (Weeks 11-12):** Testing + Performance + Launch

### **Technical Requirements**
- **Framework:** React 18+ with hooks
- **Styling:** CSS Custom Properties + CSS Modules
- **State Management:** Context API + React Query
- **Icons:** Custom gradient icon system
- **Animations:** CSS transitions + Framer Motion for complex animations
- **Responsive:** Mobile-first CSS Grid + Flexbox

### **Design Standards**
- **Glassmorphism** throughout all interfaces
- **Gradient accents** for primary actions and highlights  
- **Consistent spacing** using 8px grid system
- **Smooth animations** with cubic-bezier timing
- **Dark/Light theme** support across all components
- **Accessibility** compliance (WCAG 2.1 AA)

---

*Complete Frontend Specification: Modern glassmorphism design system with gradient accents, built on the foundation of the existing landing page theme and styling.*