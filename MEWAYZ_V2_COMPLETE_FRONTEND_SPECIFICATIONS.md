# MEWAYZ V2 COMPLETE FRONTEND SPECIFICATIONS - UPDATED
## Every Screen, Widget, Popup & Page with Workspace Access Control + New Systems

**Documentation Date:** December 30, 2024  
**Updated with:** AI Token Purchase System, New Launch Pricing, Enhanced Transaction Fees  
**Scope:** Complete UI/UX specifications with workspace-based access control  
**Key Principle:** Users only see features their current workspace has access to

---

## 🎯 MAJOR UPDATES FOR PRODUCTION LAUNCH

### **NEW SYSTEMS REQUIRING FRONTEND IMPLEMENTATION:**

1. **🤖 AI Token Purchase System** - Complete token buying/management UI
2. **📊 Usage Tracking Dashboard** - Real-time feature usage monitoring
3. **💰 Enterprise Revenue Dashboard** - Revenue tracking for Enterprise workspaces
4. **🛒 Template Marketplace Access Control** - Bundle-based selling permissions
5. **💳 Enhanced Transaction Fees** - Automatic fee calculation display
6. **🎉 Launch Pricing System** - Time-limited launch specials with claim tracking ⚠️ **CRITICAL NEW**
7. **📋 Updated Launch Pricing** - New bundle pricing ($19-39/month) with multi-bundle discounts

---

## 🏢 WORKSPACE-BASED ACCESS ARCHITECTURE

### **Core Principle:**
- **Subscriptions are per workspace** (not per user)
- **Users can belong to multiple workspaces** with different roles
- **What users see depends on currently selected workspace**
- **Workspace selector determines feature visibility**

### **Access Control Logic:**
```javascript
const getVisibleFeatures = (user, currentWorkspace) => {
  // Check user's role in current workspace
  const userRole = currentWorkspace.members.find(m => m.user_id === user.id)?.role;
  
  // Check workspace subscription and enabled bundles
  const enabledBundles = currentWorkspace.subscription.enabled_bundles;
  
  // Return features based on subscription + role permissions
  return features.filter(feature => 
    enabledBundles.includes(feature.bundle) && 
    hasRoleAccess(userRole, feature.required_permissions)
  );
};
```

---

## 🎉 LAUNCH PRICING SYSTEM ⚠️ CRITICAL NEW IMPLEMENTATION NEEDED

### **Launch Special Banner** (Site-wide)
**File:** `/frontend/src/components/LaunchSpecialBanner.js`  
**Location:** Top of all pages, sticky header

#### **Banner Structure:**
```javascript
const LaunchSpecialBanner = {
  display_logic: {
    show_conditions: [
      "User not logged in (marketing)",
      "User logged in with eligible workspace",
      "User in onboarding flow"
    ],
    hide_conditions: [
      "User already claimed special",
      "Special expired or sold out",
      "User dismissed banner permanently"
    ]
  },
  
  content_rotation: {
    specials: [
      {
        bundle: "creator",
        text: "🎉 LAUNCH SPECIAL: First 1000 users get Creator Bundle for $9/month (3 months)!",
        urgency: "Only 127 spots left!",
        cta: "Claim Special",
        background: "gradient-orange"
      },
      {
        bundle: "ecommerce", 
        text: "🎁 E-COMMERCE LAUNCH: First 500 users get 2 months FREE!",
        urgency: "Limited time offer",
        cta: "Get Free Months",
        background: "gradient-blue"
      },
      {
        bundle: "social_media",
        text: "📱 SOCIAL MEDIA BUNDLE: Free 2-week trial - No credit card required!",
        urgency: "Start today",
        cta: "Start Free Trial", 
        background: "gradient-purple"
      }
    ],
    
    rotation_logic: "Show most relevant to user's interests/behavior",
    auto_rotate_interval: "8 seconds",
    click_tracking: "Track which specials get most clicks"
  },
  
  api_integration: {
    specials_endpoint: "GET /api/launch-pricing/active-specials",
    claim_endpoint: "POST /api/launch-pricing/claim-special",
    eligibility_check: "POST /api/launch-pricing/validate-eligibility"
  }
};
```

### **Launch Special Modal** ⚠️ CRITICAL IMPLEMENTATION
**File:** `/frontend/src/modals/LaunchSpecialModal.js`  
**Trigger:** Click banner CTA, onboarding step, pricing page

#### **Modal Layout:**
```javascript
const LaunchSpecialModal = {
  header: {
    title: "🎉 Limited Time Launch Special",
    subtitle: "Don't miss out on exclusive founding member pricing",
    countdown_timer: {
      shows: "Time remaining: 23 days, 14 hours, 32 minutes",
      urgency_colors: {
        green: "30+ days remaining",
        yellow: "7-30 days remaining", 
        red: "< 7 days remaining"
      }
    }
  },
  
  special_details: {
    creator_special: {
      title: "Creator Bundle Launch Special",
      original_price: "$19/month",
      special_price: "$9/month", 
      duration: "First 3 months",
      savings_highlight: "Save $30 total + ongoing 50% discount",
      features_preview: ["Unlimited Bio Links", "Website Builder", "AI Content (500 credits)", "Template Selling"],
      spots_remaining: "127 of 1000 spots left",
      urgency_bar: "Progress bar showing 87.3% claimed"
    },
    
    ecommerce_special: {
      title: "E-commerce Bundle Launch Special",
      original_price: "$24/month",
      special_price: "FREE",
      duration: "First 2 months",
      savings_highlight: "Save $48 + get started with no upfront cost",
      features_preview: ["Unlimited Products", "Multi-vendor Support", "Payment Processing", "Inventory Management"],
      spots_remaining: "67 of 500 spots left",
      urgency_bar: "Progress bar showing 86.6% claimed"
    }
  },
  
  claim_process: {
    step_1: {
      title: "Verify Eligibility",
      content: "✅ New workspace - eligible for launch special!",
      api_call: "POST /api/launch-pricing/validate-eligibility"
    },
    
    step_2: {
      title: "Claim Your Special",
      content: "Secure your founding member pricing",
      promo_code_input: {
        optional: true,
        placeholder: "Optional: Enter promo code",
        validation: "Real-time validation"
      }
    },
    
    step_3: {
      title: "Confirmation",
      content: "Special claimed! Your discount will apply automatically.",
      next_steps: "Complete workspace setup to activate"
    }
  },
  
  social_proof: {
    testimonials: [
      '"Saved me $200/month vs other tools!" - Sarah K.',
      '"Everything I need in one platform" - Mike R.'
    ],
    stats: [
      "Join 2,847 founding members",
      "Average savings: $156/month",
      "98% customer satisfaction"
    ]
  }
};
```

### **Pricing Page Enhancement** ⚠️ ENHANCEMENT NEEDED
**File:** Enhancement to existing pricing components  
**Location:** `/pricing` page and onboarding step 5

#### **Enhanced Pricing Cards:**
```javascript
const EnhancedPricingCards = {
  creator_bundle: {
    header: {
      title: "Creator Bundle",
      badge: "🔥 LAUNCH SPECIAL",
      original_price: "$19/month",
      strikethrough: true,
      special_price: "$9/month",
      special_duration: "First 3 months"
    },
    
    launch_special_section: {
      background: "special-gradient",
      content: {
        title: "Founding Member Special",
        savings: "Save $30 in your first 3 months",
        urgency: "Only 127 spots left!",
        countdown: "23 days remaining",
        claim_button: "Claim Special ($9/month)"
      }
    },
    
    features_section: {
      standard_features: ["Unlimited Bio Links", "Website Builder", "AI Content", "Template Selling"],
      bonus_features: ["🎁 Priority Support", "🎁 Launch Member Badge", "🎁 Future Feature Early Access"]
    }
  },
  
  multi_bundle_special: {
    position: "Between bundle cards",
    content: {
      title: "💥 Multi-Bundle Launch Combo",
      description: "Combine any 2+ bundles and save even more!",
      examples: [
        { bundles: "Creator + E-commerce", regular: "$43/month", special: "$28/month", savings: "35% off" },
        { bundles: "All 3 Popular", regular: "$72/month", special: "$40/month", savings: "44% off" }
      ],
      cta: "Build Your Combo"
    }
  }
};
```

### **Launch Special Tracking Dashboard** ⚠️ ADMIN FEATURE
**File:** `/frontend/src/pages/admin/LaunchSpecialAdmin.js`  
**Route:** `/admin/launch-specials`  
**Access:** Admin users only

#### **Admin Dashboard:**
```javascript
const LaunchSpecialAdminDashboard = {
  overview_metrics: {
    cards: [
      { title: "Total Claims", value: "2,847", change: "+127 today" },
      { title: "Revenue Impact", value: "$34,567", subtitle: "Discounts given" },
      { title: "Conversion Rate", value: "23.4%", subtitle: "Visitors to claims" },
      { title: "Most Popular", value: "Creator Bundle", subtitle: "87.3% claimed" }
    ]
  },
  
  special_status_table: {
    columns: ["Bundle", "Claims", "Limit", "% Claimed", "Days Left", "Status", "Actions"],
    data: [
      {
        bundle: "Creator",
        claims: "873 / 1000",
        percentage: "87.3%",
        days_left: 23,
        status: "Active",
        actions: ["Extend Time", "Increase Limit", "Generate Codes"]
      }
    ]
  },
  
  analytics_charts: [
    { type: "Line chart", title: "Daily Claims", timeframe: "Last 30 days" },
    { type: "Bar chart", title: "Claims by Bundle" },
    { type: "Funnel chart", title: "Claim Conversion Funnel" }
  ],
  
  management_actions: {
    generate_promo_codes: "Create custom promo codes",
    extend_specials: "Extend end dates",
    modify_limits: "Increase claim limits",
    create_new_special: "Launch new promotional campaigns"
  }
};
```

### **User Account - Claimed Specials Section** ⚠️ USER FEATURE
**File:** `/frontend/src/components/account/ClaimedSpecials.js`  
**Location:** User account page, billing section

#### **Claimed Specials Display:**
```javascript
const ClaimedSpecialsSection = {
  header: {
    title: "Your Launch Specials",
    subtitle: "Founding member benefits and savings"
  },
  
  claimed_special_cards: [
    {
      bundle: "Creator Bundle",
      status: "Active",
      special_price: "$9/month",
      regular_price: "$19/month",
      expires: "February 28, 2025",
      days_remaining: 23,
      total_savings: "$30 saved so far",
      progress_bar: "2 of 3 months used",
      renewal_info: "Will renew at $19/month after special expires"
    }
  ],
  
  savings_summary: {
    total_saved: "$67 saved with launch specials",
    ongoing_savings: "Save $156/month vs competitors",
    member_since: "Founding member since December 2024",
    member_badge: "🏆 Launch Member Badge"
  },
  
  referral_section: {
    title: "Share the Special",
    description: "Help friends save too and earn rewards",
    referral_code: "LAUNCH-SARAH-2024",
    share_buttons: ["Copy Link", "Email", "Social Media"],
    referral_stats: "3 friends joined, you earned $45 credit"
  }
};
```

### **Onboarding Integration** ⚠️ STEP 5 ENHANCEMENT
**File:** Enhancement to existing onboarding Step 5  
**Integration:** Show available launch specials in pricing selection

#### **Enhanced Onboarding Step 5:**
```javascript
const EnhancedOnboardingPricing = {
  launch_special_prompt: {
    position: "Top of pricing step",
    content: {
      title: "🎉 Perfect timing! You're eligible for launch specials",
      subtitle: "As a new user, you can claim exclusive founding member pricing",
      cta: "View Available Specials"
    }
  },
  
  pricing_cards_enhancement: {
    special_badges: "Show launch special badges on eligible bundles",
    special_pricing: "Display special prices prominently",
    urgency_indicators: "Show spots remaining and countdown",
    claim_integration: "Allow claiming directly from pricing cards"
  },
  
  multi_bundle_calculator: {
    real_time_special_pricing: true,
    shows_launch_discounts: true,
    stacks_with_multi_bundle: true,
    example: {
      creator_plus_ecommerce: {
        regular_bundle_price: "$43/month",
        multi_bundle_discount: "$34/month (20% off)",
        launch_special: "$23/month (additional special pricing)",
        total_savings: "Save $20/month for first 3 months"
      }
    }
  }
};
```

### **Mobile Launch Special Experience** ⚠️ MOBILE OPTIMIZATION
**Files:** Mobile-specific components for launch specials

#### **Mobile Considerations:**
```javascript
const MobileLaunchSpecials = {
  banner: {
    design: "Collapsible banner to save screen space",
    interaction: "Swipe up to dismiss, tap to expand",
    position: "Sticky at top, auto-hide on scroll"
  },
  
  modal: {
    design: "Full-screen modal for better mobile experience",
    navigation: "Swipe between different specials",
    claim_flow: "Simplified 2-step process for mobile"
  },
  
  pricing_cards: {
    layout: "Vertical stack with horizontal scroll for specials",
    special_indicators: "Prominent badges and colors",
    claim_buttons: "Large, thumb-friendly tap targets"
  }
};
```

---

## 📊 LAUNCH PRICING BACKEND INTEGRATION

### **API Endpoints Implemented:**
```javascript
const LaunchPricingAPIs = {
  "GET /api/launch-pricing/active-specials": "Get all current launch specials",
  "GET /api/launch-pricing/bundle/{bundle_name}/special": "Get specific bundle special",
  "POST /api/launch-pricing/claim-special": "Claim a launch special",
  "POST /api/launch-pricing/validate-eligibility": "Check user eligibility",
  "GET /api/launch-pricing/claimed-specials/{workspace_id}": "Get claimed specials",
  "POST /api/launch-pricing/generate-promo-code": "Generate promo codes (admin)",
  "GET /api/launch-pricing/special-analytics": "Get special analytics (admin)",
  "POST /api/launch-pricing/extend-special": "Modify specials (admin)",
  "GET /api/launch-pricing/referral-tracking/{code}": "Track referral usage"
};
```

### **Real-time Features Required:**
- **Live claim counters** - WebSocket updates for spots remaining
- **Countdown timers** - Real-time special expiration countdowns  
- **Eligibility checking** - Instant validation of user eligibility
- **Urgency updates** - Dynamic urgency levels based on claims

---

### **AI Token Balance Widget** (Dashboard Header)
**File:** `/frontend/src/components/AITokenBalance.js`  
**Location:** Dashboard header, right side of workspace selector

#### **Component Structure:**
```javascript
const AITokenBalanceWidget = {
  display_elements: {
    current_balance: {
      format: "1,247 tokens remaining",
      color_coding: {
        green: "500+ tokens",
        yellow: "100-499 tokens", 
        red: "< 100 tokens"
      },
      click_action: "Open token management modal"
    },
    
    monthly_allocation: {
      format: "500/month from Creator Bundle",
      tooltip: "Resets on January 1st",
      progress_bar: "Usage this month"
    },
    
    purchase_button: {
      text: "Buy More",
      prominence: "Only visible when < 200 tokens",
      click_action: "Open token purchase modal"
    }
  },
  
  api_integration: {
    balance_endpoint: "GET /api/ai-token-purchase/workspace/{id}/balance",
    refresh_interval: "30 seconds",
    real_time_updates: "WebSocket for token usage"
  }
};
```

### **Token Purchase Modal** ⚠️ CRITICAL IMPLEMENTATION
**File:** `/frontend/src/modals/TokenPurchaseModal.js`  
**Trigger:** Click "Buy More" button, or automatic when hitting limits

#### **Modal Layout:**
```javascript
const TokenPurchaseModal = {
  header: {
    title: "Purchase AI Tokens",
    subtitle: "Get more credits for AI content generation",
    current_balance_display: "Current: 47 tokens"
  },
  
  pricing_packages: {
    layout: "3x2 grid (6 packages)",
    packages: [
      {
        id: "starter_100",
        name: "Starter Pack",
        tokens: 100,
        price: "$9.99",
        price_per_token: "$0.099",
        popular: false,
        badge: null,
        features: ["Valid 6 months", "No rollover"]
      },
      {
        id: "popular_500",
        name: "Popular Pack", 
        tokens: 500,
        price: "$39.99",
        price_per_token: "$0.079",
        popular: true,
        badge: "MOST POPULAR",
        features: ["Valid 6 months", "20% discount", "Priority support"]
      },
      {
        id: "professional_1000",
        name: "Professional Pack",
        tokens: 1000, 
        price: "$69.99",
        price_per_token: "$0.069",
        popular: false,
        badge: "BEST VALUE",
        features: ["Valid 12 months", "30% discount", "Priority support", "Analytics"]
      },
      {
        id: "business_2500",
        name: "Business Pack",
        tokens: 2500,
        price: "$149.99", 
        price_per_token: "$0.059",
        popular: false,
        badge: null,
        features: ["Valid 12 months", "40% discount", "Priority support", "Analytics", "Bulk gifting"]
      },
      {
        id: "enterprise_5000",
        name: "Enterprise Pack",
        tokens: 5000,
        price: "$249.99",
        price_per_token: "$0.049", 
        popular: false,
        badge: null,
        features: ["Valid 12 months", "50% discount", "Priority support", "Analytics", "Bulk gifting", "Custom integrations"]
      },
      {
        id: "unlimited_monthly",
        name: "Unlimited Monthly",
        tokens: "∞",
        price: "$199.99",
        price_per_token: "N/A",
        popular: false,
        badge: "POWER USERS",
        features: ["Unlimited for 30 days", "Priority support", "Advanced analytics", "API access"]
      }
    ],
    
    selection_logic: {
      single_select: true,
      auto_recommend: "Based on usage patterns",
      savings_calculator: "Show savings vs $0.10 base price"
    }
  },
  
  payment_section: {
    payment_methods: ["Credit Card", "PayPal", "Stripe"],
    billing_info: "Reuse workspace billing info",
    purchase_button: "Purchase {tokens} Tokens for ${price}",
    processing_states: ["Processing...", "Success!", "Error"]
  },
  
  api_integration: {
    pricing_endpoint: "GET /api/ai-token-purchase/pricing",
    purchase_endpoint: "POST /api/ai-token-purchase/purchase",
    success_callback: "Update balance widget + close modal"
  }
};
```

### **Token Usage Analytics Page** ⚠️ NEEDS IMPLEMENTATION
**File:** `/frontend/src/pages/TokenAnalytics.js`  
**Route:** `/workspace/{id}/ai-tokens`  
**Access:** All paid bundles

#### **Page Sections:**
```javascript
const TokenAnalyticsPage = {
  header_stats: {
    cards: [
      { title: "Current Balance", value: "1,247 tokens", change: "+500 this month" },
      { title: "This Month Usage", value: "753 tokens", change: "+12% vs last month" },
      { title: "Bundle Allocation", value: "500/month", change: "Creator Bundle" },
      { title: "Purchased Tokens", value: "1,500 tokens", change: "Expires in 4 months" }
    ]
  },
  
  usage_chart: {
    type: "Line chart",
    timeframe: "Last 30 days",
    data_points: "Daily usage",
    categories: ["Content Generation", "Image Creation", "Code Generation", "Translation", "SEO Optimization", "Data Analysis"]
  },
  
  category_breakdown: {
    type: "Donut chart + table",
    shows: "Usage by category",
    details: "Tokens used, number of operations, average per operation"
  },
  
  purchase_history: {
    type: "Table",
    columns: ["Date", "Package", "Tokens", "Price", "Status", "Expires"],
    actions: ["View Receipt", "Download Invoice"]
  },
  
  recommendations: {
    type: "Cards",
    shows: "Based on usage patterns",
    suggestions: ["Upgrade bundle", "Buy tokens", "Usage optimization tips"]
  }
};
```

### **Token Gifting Modal** ⚠️ PREMIUM FEATURE
**File:** `/frontend/src/modals/TokenGiftModal.js`  
**Access:** Business+ bundles only

#### **Gifting Flow:**
```javascript
const TokenGiftModal = {
  recipient_selection: {
    input_type: "Workspace ID or email",
    validation: "Check workspace exists",
    workspace_preview: "Show recipient workspace info"
  },
  
  gift_amount: {
    input_type: "Number input",
    constraints: "Min 10, Max current balance",
    balance_check: "Real-time balance validation"
  },
  
  personalization: {
    message_input: "Optional gift message",
    sender_info: "From {workspace_name}",
    delivery_option: "Send immediately or schedule"
  },
  
  confirmation: {
    summary: "Gift {amount} tokens to {recipient}",
    balance_after: "Your balance after: {remaining} tokens",
    send_button: "Send Gift"
  }
};
```

### **Auto-Refill Settings** ⚠️ PREMIUM FEATURE
**File:** `/frontend/src/components/AutoRefillSettings.js`  
**Location:** Token Analytics page, settings section

#### **Configuration Panel:**
```javascript
const AutoRefillSettings = {
  enable_toggle: {
    label: "Enable Auto-Refill",
    description: "Automatically purchase tokens when balance gets low"
  },
  
  trigger_threshold: {
    input_type: "Number input",
    label: "Refill when balance reaches",
    default: 50,
    validation: "10-500 range"
  },
  
  refill_package: {
    input_type: "Dropdown",
    options: "All available packages",
    recommendation: "Based on usage patterns"
  },
  
  payment_method: {
    input_type: "Dropdown", 
    options: "Saved payment methods",
    fallback: "Default workspace payment"
  },
  
  notifications: {
    checkboxes: ["Email when refill triggers", "Dashboard notification", "Slack notification"],
    default: "All enabled"
  }
};
```

---

## 📊 USAGE TRACKING DASHBOARD ⚠️ CRITICAL NEW IMPLEMENTATION NEEDED

### **Usage Overview Widget** (Main Dashboard)
**File:** `/frontend/src/components/UsageOverviewWidget.js`  
**Location:** Main dashboard, prominent placement

#### **Widget Structure:**
```javascript
const UsageOverviewWidget = {
  layout: "Card with progress bars",
  
  tracked_features: {
    ai_content_generation: {
      label: "AI Content",
      current: "347 / 500 credits",
      percentage: 69.4,
      color: "orange", // Warning at 70%
      reset_date: "January 1st"
    },
    
    instagram_searches: {
      label: "Instagram Searches", 
      current: "892 / 1000 searches",
      percentage: 89.2,
      color: "red", // Critical at 90%
      reset_date: "January 1st"
    },
    
    emails_sent: {
      label: "Emails Sent",
      current: "7,234 / 10,000 emails", 
      percentage: 72.3,
      color: "orange",
      reset_date: "January 1st"
    },
    
    // ... other tracked features based on workspace bundles
  },
  
  action_buttons: {
    view_details: "View Full Usage Report",
    upgrade_workspace: "Upgrade Bundle", // Only if over limits
    buy_tokens: "Buy AI Tokens" // For AI features only
  },
  
  api_integration: {
    data_endpoint: "GET /api/usage-tracking/current/{workspace_id}",
    limits_endpoint: "GET /api/usage-tracking/limits/{workspace_id}", 
    refresh_interval: "60 seconds"
  }
};
```

### **Detailed Usage Analytics Page** ⚠️ NEEDS IMPLEMENTATION
**File:** `/frontend/src/pages/UsageAnalytics.js`  
**Route:** `/workspace/{id}/usage`  
**Access:** All workspaces

#### **Page Layout:**
```javascript
const UsageAnalyticsPage = {
  header_metrics: {
    cards: [
      { title: "Features Used", value: "12 / 25", subtitle: "Available in your bundles" },
      { title: "This Month", value: "85% usage", subtitle: "Above average" },
      { title: "Most Used", value: "AI Content", subtitle: "347 credits used" },
      { title: "Days Until Reset", value: "12 days", subtitle: "January 1st" }
    ]
  },
  
  usage_trends: {
    chart_type: "Multi-line chart",
    timeframe: "Last 90 days", 
    toggles: "Daily / Weekly / Monthly view",
    feature_toggles: "Show/hide specific features"
  },
  
  feature_breakdown: {
    layout: "Table with progress bars",
    columns: ["Feature", "Current Usage", "Limit", "% Used", "Trend", "Reset Date"],
    sorting: "By usage percentage (highest first)",
    filtering: "By bundle, by status (warning/critical)"
  },
  
  warnings_alerts: {
    section: "Usage Warnings",
    alert_types: [
      { type: "critical", threshold: "90%+", color: "red", message: "Approaching limit" },
      { type: "warning", threshold: "80%+", color: "orange", message: "High usage" },
      { type: "info", threshold: "50%+", color: "blue", message: "Normal usage" }
    ]
  },
  
  recommendations: {
    section: "Upgrade Recommendations",
    logic: "Based on usage patterns",
    suggestions: ["Add Social Media Bundle", "Upgrade to Business Bundle", "Buy AI Tokens"]
  }
};
```

### **Usage Limit Warning Modal** ⚠️ CRITICAL IMPLEMENTATION
**File:** `/frontend/src/modals/UsageLimitWarningModal.js`  
**Trigger:** When user tries to use feature at/over limit

#### **Modal Content:**
```javascript
const UsageLimitWarningModal = {
  warning_types: {
    approaching_limit: {
      title: "Approaching Usage Limit",
      message: "You've used 89% of your Instagram searches this month",
      icon: "warning-triangle",
      color: "orange",
      actions: ["Continue Anyway", "Upgrade Bundle", "Cancel"]
    },
    
    limit_exceeded: {
      title: "Usage Limit Exceeded", 
      message: "You've reached your limit of 1,000 Instagram searches this month",
      icon: "stop-circle",
      color: "red",
      actions: ["Upgrade Bundle", "Buy More", "Cancel"]
    },
    
    tokens_depleted: {
      title: "AI Tokens Depleted",
      message: "You've used all 500 AI credits this month",
      icon: "zap-off", 
      color: "red",
      actions: ["Buy AI Tokens", "Upgrade Bundle", "Wait for Reset (12 days)"]  
    }
  },
  
  upgrade_suggestions: {
    current_bundle: "Creator Bundle ($19/month)",
    suggested_bundle: "Creator + Social Media Bundle ($34/month with 20% discount)",
    savings_highlight: "Save $13/month vs separate purchases",
    feature_comparison: "Side-by-side comparison table"
  }
};
```

---

## 💰 ENTERPRISE REVENUE DASHBOARD ⚠️ ENTERPRISE ONLY IMPLEMENTATION

### **Revenue Tracking Dashboard** 
**File:** `/frontend/src/pages/EnterpriseRevenue.js`  
**Route:** `/workspace/{id}/revenue`  
**Access:** Enterprise workspaces only (4+ bundles or revenue-based pricing)

#### **Dashboard Structure:**
```javascript
const EnterpriseRevenueDashboard = {
  revenue_overview: {
    cards: [
      { title: "This Month Revenue", value: "$24,567", change: "+18% vs last month" },
      { title: "Platform Fee (15%)", value: "$3,685", subtitle: "Due: January 31st" },
      { title: "Net Revenue", value: "$20,882", change: "+18% vs last month" },
      { title: "Revenue Sources", value: "6 active", subtitle: "E-commerce, Courses, etc." }
    ]
  },
  
  revenue_chart: {
    type: "Area chart",
    timeframe: "Last 12 months",
    breakdown: "By revenue source",
    drill_down: "Click to see source details"
  },
  
  revenue_sources: {
    table_columns: ["Source", "This Month", "Last Month", "Change", "% of Total"],
    sources: [
      "E-commerce Sales",
      "Course Sales", 
      "Booking Payments",
      "Template Sales",
      "Subscription Revenue",
      "Affiliate Commissions",
      "Consulting Services",
      "Digital Products"
    ]
  },
  
  billing_history: {
    section: "Platform Fee History",
    table_columns: ["Month", "Revenue", "Fee (15%)", "Status", "Due Date", "Actions"],
    actions: ["View Details", "Download Invoice", "Dispute"]
  },
  
  projections: {
    section: "Revenue Projections",
    chart_type: "Line chart with confidence intervals",
    timeframe: "Next 12 months",
    methodology: "Based on historical trends"
  }
};
```

### **Revenue Source Details Modal** ⚠️ ENTERPRISE FEATURE
**File:** `/frontend/src/modals/RevenueSourceModal.js`  
**Trigger:** Click on revenue source in dashboard

#### **Modal Content:**
```javascript
const RevenueSourceModal = {
  header: {
    title: "E-commerce Sales - December 2024",
    total_revenue: "$18,456",
    transaction_count: "347 transactions",
    average_transaction: "$53.21"
  },
  
  transaction_details: {
    table_columns: ["Date", "Transaction ID", "Amount", "Customer", "Product", "Status"],
    pagination: "50 per page",
    filtering: ["Date range", "Amount range", "Customer", "Product category"],
    export_options: ["CSV", "PDF", "Excel"]
  },
  
  analytics: {
    charts: [
      { type: "Bar chart", title: "Daily Revenue", timeframe: "This month" },
      { type: "Pie chart", title: "Revenue by Product Category" },
      { type: "Line chart", title: "Average Transaction Value Trend" }
    ]
  }
};
```

---

## 🛒 TEMPLATE MARKETPLACE ACCESS CONTROL ⚠️ NEW IMPLEMENTATION NEEDED

### **Template Selling Permission Check** 
**Component:** Enhancement to existing template marketplace  
**Logic:** Only show "Sell Template" options to Creator+ bundle users

#### **Access Control Implementation:**
```javascript
const TemplateMarketplaceAccess = {
  selling_button_logic: {
    free_users: {
      button_text: "Upgrade to Sell",
      click_action: "Show upgrade modal",
      tooltip: "Template selling requires Creator+ bundle"
    },
    
    creator_plus_users: {
      button_text: "Sell This Template", 
      click_action: "Open template selling form",
      tooltip: "Earn 85% revenue share"
    }
  },
  
  seller_onboarding: {
    modal_title: "Start Selling Templates",
    steps: [
      {
        title: "Verify Bundle Access",
        content: "✅ Creator Bundle detected - you can sell templates!"
      },
      {
        title: "Commission Structure", 
        content: "You keep 85%, platform takes 15% commission"
      },
      {
        title: "Quality Requirements",
        content: "Templates must meet quality standards and get approved"
      },
      {
        title: "Enable Selling",
        content: "Activate template selling for your workspace"
      }
    ]
  },
  
  seller_dashboard: {
    file: "/frontend/src/pages/TemplateSeller.js",
    route: "/workspace/{id}/template-selling",
    access: "Creator+ bundle users only",
    
    metrics: [
      { title: "Templates Live", value: "23 templates" },
      { title: "Total Sales", value: "156 sales" },
      { title: "Revenue Earned", value: "$2,847" },
      { title: "Average Rating", value: "4.7 stars" }
    ]
  }
};
```

### **Template Validation Interface** ⚠️ SELLER FEATURE
**File:** `/frontend/src/components/TemplateValidator.js`  
**Usage:** When sellers submit templates for approval

#### **Validation UI:**
```javascript
const TemplateValidationInterface = {
  validation_checklist: {
    required_fields: [
      { field: "Title", status: "✅", message: "Title provided" },
      { field: "Description", status: "⚠️", message: "Description too short (32/50 chars)" },
      { field: "Category", status: "✅", message: "Category selected" },
      { field: "Price", status: "✅", message: "$29 (valid range)" },
      { field: "Preview Images", status: "❌", message: "Need at least 1 preview image" }
    ]
  },
  
  quality_checks: {
    automated: [
      { check: "Image quality", status: "✅", message: "All images high resolution" },
      { check: "Template functionality", status: "⚠️", message: "Some links not working" },
      { check: "Mobile responsiveness", status: "✅", message: "Mobile-friendly design" },
      { check: "Loading speed", status: "✅", message: "Fast loading (2.1s)" }
    ]
  },
  
  submission_status: {
    states: ["Draft", "Validation", "Under Review", "Approved", "Rejected"],
    current_state: "Validation",
    next_steps: "Fix issues above to submit for review",
    estimated_review: "2-3 business days"
  }
};
```

---

## 💳 ENHANCED TRANSACTION FEES DISPLAY ⚠️ ENHANCEMENT NEEDED

### **Transaction Fee Calculator Widget**
**File:** `/frontend/src/components/TransactionFeeCalculator.js`  
**Location:** E-commerce checkout, payment modals

#### **Fee Display Implementation:**
```javascript
const TransactionFeeDisplay = {
  fee_breakdown: {
    layout: "Inline with transaction total",
    
    standard_workspace: {
      subtotal: "$100.00",
      platform_fee: "$2.40 (2.4%)",
      seller_receives: "$97.60",
      fee_description: "Standard platform fee"
    },
    
    enterprise_workspace: {
      subtotal: "$100.00", 
      platform_fee: "$1.90 (1.9%)",
      seller_receives: "$98.10",
      fee_description: "Enterprise rate (4+ bundles)"
    }
  },
  
  fee_explanation: {
    tooltip: "Platform fees help maintain servers, payment processing, and customer support",
    comparison: "Competitive with PayPal (2.9%) and Stripe (2.9% + $0.30)",
    benefits: "Includes escrow protection, dispute resolution, and analytics"
  },
  
  real_time_calculation: {
    api_endpoint: "GET /api/escrow/calculate-fees",
    update_trigger: "Amount change",
    debounce: "500ms"
  }
};
```

### **Enhanced Payment Flow** ⚠️ CHECKOUT ENHANCEMENT
**File:** Enhancement to existing checkout components  
**Logic:** Show fee calculation before payment confirmation

#### **Checkout Flow Updates:**
```javascript
const EnhancedCheckoutFlow = {
  step_3_payment: {
    // Existing payment step enhanced with fee transparency
    
    order_summary: {
      item_total: "$97.50",
      shipping: "$2.50", 
      subtotal: "$100.00",
      platform_fee: "$2.40 (2.4%)", // NEW: Transparent fee display
      total_charged: "$102.40", // NEW: Total including fees
      seller_receives: "$97.60" // NEW: Seller net amount
    },
    
    fee_explanation: {
      expandable_section: true,
      title: "Why platform fees?",
      content: "Covers payment processing, escrow protection, dispute resolution, and platform maintenance",
      comparison: "Lower than most competitors (PayPal: 2.9%, Square: 2.6% + $0.10)"
    }
  }
};
```

---

## 📋 UPDATED LAUNCH PRICING & ONBOARDING ⚠️ CRITICAL PRICING UPDATES

### **Updated Pricing Display** (Multiple locations)
**Files:** Update existing pricing components  
**New Pricing:** Based on MEWAYZ_V2_SMART_LAUNCH_PRICING_STRATEGY.md

#### **New Bundle Prices:**
```javascript
const UpdatedBundlePricing = {
  bundle_prices: {
    creator: {
      monthly: "$19/month",
      yearly: "$190/year (save $38)",
      launch_special: "First 1000 users: 3 months for $9/month"
    },
    
    ecommerce: {
      monthly: "$24/month", 
      yearly: "$240/year (save $48)",
      launch_special: "First 500 users: 2 months free"
    },
    
    social_media: {
      monthly: "$29/month",
      yearly: "$290/year (save $58)", 
      launch_special: "First 2 weeks free trial"
    },
    
    education: {
      monthly: "$29/month",
      yearly: "$290/year (save $58)",
      launch_special: "First month free"
    },
    
    business: {
      monthly: "$39/month",
      yearly: "$390/year (save $78)",
      launch_special: "50% off first 3 months"
    },
    
    operations: {
      monthly: "$24/month",
      yearly: "$240/year (save $48)",
      launch_special: "First month free"
    }
  },
  
  multi_bundle_discounts: {
    two_bundles: "20% discount",
    three_bundles: "30% discount", 
    four_plus_bundles: "40% discount"
  },
  
  enterprise_pricing: {
    model: "15% revenue share",
    minimum: "$99/month",
    launch_special: "First 50 customers: 10% revenue share for 6 months"
  }
};
```

### **Enhanced Onboarding Pricing Step** ⚠️ STEP 5 UPDATE
**File:** `/frontend/src/components/onboarding/Step5PricingSelection.js`  
**Enhancement:** Show multi-bundle discounts and launch specials

#### **Updated Pricing Selection:**
```javascript
const EnhancedPricingStep = {
  bundle_selection: {
    layout: "2x3 grid of bundle cards",
    multi_select: true,
    
    discount_calculator: {
      real_time: true,
      shows: "Live pricing as user selects bundles",
      example: {
        creator_plus_ecommerce: {
          regular_price: "$43/month",
          discounted_price: "$34/month (20% discount)",
          savings: "Save $9/month"
        }
      }
    }
  },
  
  launch_specials: {
    display: "Prominent banner above pricing",
    offers: {
      creator: "🎉 LAUNCH SPECIAL: First 1000 users get 3 months for $9/month!",
      ecommerce: "🎁 LAUNCH SPECIAL: First 500 users get 2 months free!",
      // ... other specials
    },
    
    countdown_timer: {
      shows: "Limited time offers",
      urgency: "Only 127 spots left for Creator launch special!"
    }
  },
  
  enterprise_option: {
    display: "Separate card at bottom",
    title: "Enterprise Revenue Share",
    description: "Pay 15% of revenue generated (min $99/month)",
    benefits: ["All bundles included", "White-label solution", "Dedicated support"],
    cta: "Contact Sales"
  }
};
```

---

## 🎯 CRITICAL FRONTEND IMPLEMENTATIONS SUMMARY

### **IMMEDIATE PRIORITIES (Week 1):**

1. **🤖 AI Token Purchase System**
   - Token balance widget (dashboard header)
   - Token purchase modal (6 pricing packages)
   - Usage analytics page
   - Auto-refill settings

2. **📊 Usage Tracking Dashboard**
   - Usage overview widget (main dashboard) 
   - Detailed usage analytics page
   - Usage limit warning modals
   - Real-time usage monitoring

3. **💳 Enhanced Transaction Fees**
   - Fee calculator widget (checkout)
   - Transparent fee display 
   - Fee explanation tooltips

### **SECONDARY PRIORITIES (Week 2):**

4. **💰 Enterprise Revenue Dashboard** (Enterprise only)
   - Revenue tracking dashboard
   - Revenue source details
   - Billing history interface

5. **🛒 Template Marketplace Access Control**
   - Bundle-based selling permissions
   - Seller onboarding flow
   - Template validation interface

6. **📋 Updated Pricing & Onboarding**
   - New launch pricing display
   - Multi-bundle discount calculator
   - Launch specials banners

### **TECHNICAL REQUIREMENTS:**

- **Real-time Updates:** WebSocket connections for balance/usage
- **Payment Integration:** Stripe for token purchases  
- **Permission System:** Bundle-based feature visibility
- **Responsive Design:** Mobile-first for all new components
- **API Integration:** All new backend endpoints implemented
- **Error Handling:** Graceful degradation for API failures

---

## 📱 MOBILE CONSIDERATIONS

All new components must be mobile-responsive:

- **Token Purchase Modal:** Stack pricing cards vertically on mobile
- **Usage Dashboard:** Horizontal scroll for usage bars
- **Revenue Dashboard:** Card layout for enterprise metrics
- **Fee Calculator:** Collapsible details section

---

## 🔒 SECURITY & PERMISSIONS

### **Access Control Matrix:**
```javascript
const FeatureAccessMatrix = {
  ai_token_purchase: "All paid bundles",
  usage_tracking: "All workspaces", 
  enterprise_revenue: "Enterprise workspaces only (4+ bundles)",
  template_selling: "Creator+ bundles only",
  transaction_fees: "E-commerce bundle users",
  
  admin_features: "Workspace owners/admins only",
  billing_management: "Owners/admins with billing permissions"
};
```

### **Enhanced Dashboard Layout**
**File:** `/frontend/src/pages/dashboard/Dashboard.js`  
**Route:** `/dashboard`

#### **Header Components** ⚠️ CRITICAL IMPLEMENTATION NEEDED
```javascript
const DashboardHeader = {
  workspace_selector: {
    component: "WorkspaceDropdown",
    functionality: [
      "Show all user's workspaces",
      "Display current workspace name + logo", 
      "Switch workspace (reload dashboard)",
      "Show subscription status per workspace",
      "Create new workspace option"
    ],
    api_calls: [
      "GET /api/workspace/ (list user workspaces)",
      "POST /api/complete-multi-workspace/switch",
      "GET /api/workspace/{id} (get workspace details)"
    ]
  },
  
  subscription_indicator: {
    component: "SubscriptionBadge",
    shows: [
      "Current workspace plan (Free/Creator/E-commerce/etc)",
      "Features used vs limits",
      "Upgrade prompts if over limits",
      "Billing status"
    ]
  },
  
  global_search: {
    component: "UnifiedSearch",
    scope: "Current workspace only",
    searches_across: "Only enabled features for current workspace"
  }
};
```

#### **Dynamic Feature Cards** ⚠️ NEEDS IMPLEMENTATION
```javascript
const WorkspaceBasedFeatureCards = {
  visibility_logic: {
    free_workspace: {
      visible_features: ["basic_bio_links", "basic_forms", "basic_analytics"],
      feature_limits: {
        bio_links: "1 page, 5 links max",
        forms: "1 form, 50 submissions/month", 
        analytics: "7 days retention"
      },
      branding: "Mewayz watermark required"
    },
    
    creator_bundle: {
      visible_features: ["advanced_bio_links", "website_builder", "seo_tools", "ai_content", "template_marketplace"],
      feature_limits: {
        bio_links: "Unlimited links, custom domain",
        website: "10 pages, custom domain",
        ai_content: "500 credits/month"
      },
      branding: "No Mewayz watermark"
    },
    
    ecommerce_bundle: {
      visible_features: ["ecommerce_store", "multi_vendor", "promotions", "payment_processing", "inventory"],
      feature_limits: {
        products: "Unlimited",
        vendors: "Up to 10",
        transactions: "Unlimited"
      }
    },
    
    // ... other bundles
    
    enterprise: {
      visible_features: "All features available",
      feature_limits: "No limits",
      additional: ["white_label", "api_access", "custom_analytics"]
    }
  },
  
  card_rendering: {
    enabled_features: {
      style: "full_color_card",
      clickable: true,
      shows_usage_stats: true
    },
    disabled_features: {
      style: "grayed_out_with_lock_icon", 
      clickable: false,
      shows_upgrade_prompt: true
    }
  }
};
```

---

## 🚀 WORKSPACE-SPECIFIC ONBOARDING

### **Enhanced Onboarding Wizard**
**File:** `/frontend/src/pages/OnboardingWizard.js`

#### **Step 5: Subscription Selection** ⚠️ ENHANCED IMPLEMENTATION NEEDED
```javascript
const WorkspaceSubscriptionStep = {
  title: "Choose Your Workspace Plan",
  subtitle: "This subscription applies to this workspace only",
  
  pricing_display: {
    bundle_cards: [
      {
        bundle: "creator",
        price: "$19/month",
        features: ["Bio links", "Website", "SEO", "AI content"],
        limits: "Perfect for individual creators"
      },
      {
        bundle: "ecommerce", 
        price: "$24/month",
        features: ["Online store", "Multi-vendor", "Payments"],
        limits: "Great for online businesses"
      },
      // ... other bundles
      {
        bundle: "enterprise",
        price: "15% of revenue",
        minimum: "$99/month",
        features: "All bundles + white-label + API access",
        limits: "For agencies and large businesses"
      }
    ]
  },
  
  workspace_context: {
    shows: "You are setting up: {workspace_name}",
    billing: "Billing will be separate for each workspace",
    clarification: "You can create additional workspaces with different plans"
  },
  
  api_integration: {
    endpoint: "POST /api/workspace/{id}/subscription",
    payload: {
      bundle_type: "creator|ecommerce|social|education|business|operations|enterprise",
      billing_cycle: "monthly|yearly",
      payment_method: "stripe_payment_method_id"
    }
  }
};
```

---

## 💼 WORKSPACE MANAGEMENT SCREENS

### **Workspace Settings** ⚠️ ENHANCED IMPLEMENTATION NEEDED
**File:** `/frontend/src/pages/dashboard/WorkspaceSettings.js`

#### **Subscription Management Tab**
```javascript
const WorkspaceSubscriptionSettings = {
  current_plan_display: {
    shows: [
      "Current bundle(s) active",
      "Monthly/yearly billing cycle",
      "Next billing date and amount",
      "Features included vs used",
      "Usage limits and overages"
    ]
  },
  
  bundle_management: {
    add_bundle: {
      action: "Add additional bundles to workspace",
      pricing: "Shows multi-bundle discounts (20%, 30%, 40%)",
      confirmation: "Prorated billing calculation"
    },
    
    remove_bundle: {
      action: "Remove bundles from workspace", 
      warning: "Data and features will be disabled",
      timing: "Takes effect at next billing cycle"
    },
    
    upgrade_to_enterprise: {
      action: "Switch to 15% revenue share model",
      requirements: "Minimum $660/month revenue",
      benefits: "All bundles + white-label + API access"
    }
  },
  
  billing_section: {
    payment_methods: "Workspace-specific payment methods",
    invoices: "Workspace billing history", 
    usage_tracking: "For enterprise revenue calculation"
  }
};
```

### **Multi-Workspace Switcher** ⚠️ CRITICAL IMPLEMENTATION NEEDED
**Component:** `WorkspaceSwitcher`

```javascript
const WorkspaceSwitcherComponent = {
  dropdown_content: {
    current_workspace: {
      displays: ["Name", "Logo", "Plan badge", "Role badge"],
      style: "Highlighted as current"
    },
    
    other_workspaces: {
      displays: ["Name", "Logo", "Plan", "Your role"],
      action: "Click to switch context",
      api_call: "POST /api/complete-multi-workspace/switch"
    },
    
    actions: [
      {
        label: "Create New Workspace", 
        action: "Opens onboarding wizard",
        icon: "+"
      },
      {
        label: "Workspace Settings",
        action: "Opens current workspace settings",
        icon: "⚙️"
      }
    ]
  },
  
  switching_behavior: {
    on_switch: [
      "Update global app state",
      "Reload dashboard with new workspace context", 
      "Update navigation based on new workspace features",
      "Clear any cached data from previous workspace"
    ]
  }
};
```

---

## 🔒 ROLE-BASED ACCESS WITHIN WORKSPACES

### **Permission Matrix by Role**
```javascript
const WorkspaceRolePermissions = {
  owner: {
    permissions: ["full_access", "billing", "team_management", "delete_workspace"],
    sees: "All enabled features + workspace management"
  },
  
  admin: {
    permissions: ["feature_access", "team_management", "view_billing"],
    sees: "All enabled features + team management (no billing)"
  },
  
  editor: {
    permissions: ["feature_access", "create_content", "edit_content"],
    sees: "All enabled features (no team/billing management)"
  },
  
  viewer: {
    permissions: ["view_only"],
    sees: "Read-only access to enabled features"
  }
};
```

---

## 📱 FEATURE MODULE ACCESS CONTROL

### **Dynamic Feature Routing** ⚠️ IMPLEMENTATION NEEDED
```javascript
const FeatureAccessControl = {
  route_guards: {
    before_route_enter: (to, from, next) => {
      const currentWorkspace = getCurrentWorkspace();
      const requiredBundle = getRequiredBundle(to.path);
      
      if (workspaceHasBundle(currentWorkspace, requiredBundle)) {
        next(); // Allow access
      } else {
        next('/dashboard/upgrade'); // Redirect to upgrade page
      }
    }
  },
  
  feature_specific_checks: {
    "/dashboard/instagram": {
      required_bundle: "social_media",
      fallback: "Upgrade to Social Media Bundle"
    },
    
    "/dashboard/ecommerce": {
      required_bundle: "ecommerce", 
      fallback: "Upgrade to E-commerce Bundle"
    },
    
    "/dashboard/courses": {
      required_bundle: "education",
      fallback: "Upgrade to Education Bundle"
    }
    
    // ... for all features
  }
};
```

### **Feature Usage Limits** ⚠️ IMPLEMENTATION NEEDED
```javascript
const FeatureUsageLimits = {
  bio_links: {
    free: { pages: 1, links_per_page: 5, custom_domain: false },
    creator: { pages: "unlimited", links_per_page: "unlimited", custom_domain: true }
  },
  
  forms: {
    free: { forms: 1, submissions_per_month: 50 },
    operations: { forms: "unlimited", submissions_per_month: "unlimited" }
  },
  
  ai_content: {
    creator: { credits_per_month: 500 },
    business: { credits_per_month: 2000 },
    enterprise: { credits_per_month: "unlimited" }
  },
  
  ecommerce: {
    ecommerce: { products: "unlimited", transaction_fee: "2.4%" },
    enterprise: { products: "unlimited", transaction_fee: "1.9%" }
  }
};
```

---

## 🔄 SUBSCRIPTION MANAGEMENT WORKFLOWS

### **Upgrade/Downgrade Flows** ⚠️ NEEDS IMPLEMENTATION

#### **Bundle Addition Flow**
1. **Current Plan Display** → Shows active bundles
2. **Available Bundles** → Shows unselected bundles with pricing
3. **Multi-Bundle Discount Calculator** → Real-time pricing
4. **Payment Confirmation** → Prorated billing
5. **Feature Activation** → Immediate access to new features

#### **Enterprise Upgrade Flow**  
1. **Revenue Verification** → Must show $660+ monthly revenue
2. **Revenue Share Explanation** → 15% model with examples
3. **White-label Setup** → Branding configuration
4. **API Access Provisioning** → Generate API keys
5. **Success State** → All features unlocked

---

## 📊 MISSING BACKEND IMPLEMENTATIONS NEEDED

### **1. Workspace-Based Subscription Management** ⚠️ TO BUILD
```python
# New API endpoints needed
@router.post("/workspace/{workspace_id}/subscription")
async def create_workspace_subscription(workspace_id: str, data: dict):
    # Create subscription for specific workspace
    pass

@router.put("/workspace/{workspace_id}/subscription/add-bundle")
async def add_bundle_to_workspace(workspace_id: str, bundle_data: dict):
    # Add bundle to existing workspace subscription
    pass

@router.get("/workspace/{workspace_id}/usage-limits")
async def get_workspace_usage_limits(workspace_id: str):
    # Get current usage vs limits for workspace
    pass
```

### **2. Enterprise Revenue Tracking** ⚠️ TO BUILD
```python
@router.get("/workspace/{workspace_id}/revenue-tracking")
async def get_workspace_revenue(workspace_id: str, period: str):
    # Calculate total revenue generated through platform
    # Include: e-commerce sales, course sales, bookings, templates
    pass

@router.post("/enterprise/calculate-billing")
async def calculate_enterprise_billing(workspace_id: str):
    # Calculate 15% of total revenue for billing
    # Minimum $99/month enforcement
    pass
```

### **3. Feature Access Control Service** ⚠️ TO BUILD
```python
@router.get("/workspace/{workspace_id}/feature-access")
async def check_feature_access(workspace_id: str, feature: str):
    # Check if workspace has access to specific feature
    # Return usage limits and current usage
    pass
```

---

## 🎯 IMPLEMENTATION PRIORITY

### **Phase 1: Critical Workspace Features (Week 1)**
1. **Workspace-based subscription management**
2. **Multi-workspace switcher component**
3. **Feature access control middleware**
4. **Usage limits enforcement**

### **Phase 2: Enhanced UI/UX (Week 2)**
1. **Dynamic dashboard based on workspace**
2. **Upgrade/downgrade flows**
3. **Enterprise revenue tracking**
4. **Role-based permission UI**

### **Phase 3: Advanced Features (Week 3)**
1. **White-label configuration**
2. **API access management**
3. **Advanced analytics per workspace**
4. **Billing optimization**

---

This workspace-based approach ensures users have a clean, focused experience where they only see what they have access to, while enabling flexible multi-workspace management with per-workspace billing.

---

*Complete Workspace-Based Architecture: Subscriptions per workspace, dynamic feature access, role-based permissions*

---

## 🌟 PUBLIC & AUTHENTICATION SCREENS

### **1. Landing Page** ✅ COMPLETE
- **Web:** Full responsive marketing page
- **Mobile:** Optimized mobile version
- **Components:** Hero, features, pricing, testimonials

### **2. Authentication Screens**

#### **2.1 Login Page** 
- **Web Layout:** Split screen (branding left, form right)
- **Mobile Layout:** Full screen with compact form
- **Components:**
  - Email/password form with validation
  - Google OAuth button (✅ implemented)
  - Apple OAuth button (⚠️ needs implementation)  
  - "Forgot Password" link
  - "Create Account" link
  - Theme toggle

#### **2.2 Registration Page**
- **Web Layout:** Similar to login, multi-step flow
- **Mobile Layout:** Full screen wizard
- **Steps:**
  1. Account creation form
  2. Email verification 
  3. Success state
- **Components:**
  - Email uniqueness validation
  - Password strength meter
  - Social registration options

#### **2.3 Workspace Invitation Page**
- **States:** Loading → Invitation Display → Accepting → Success/Error
- **Components:**
  - Workspace branding display
  - Inviter information
  - Role badge
  - Accept/Decline buttons
  - Loading animations

---

## 🚀 ONBOARDING WIZARD (6 STEPS)

### **Step 1: Workspace Setup**
**Components:**
- Workspace name input
- Description textarea  
- Industry selector
- Website URL input
- Progress indicator (1/6)

### **Step 2: Main Goals Selection** ⚠️ NEEDS IMPLEMENTATION
**Layout:** 3x3 grid (web) / 1x9 list (mobile)
**Components:**
- 9 goal cards with icons and descriptions
- Multi-select functionality
- "Select All" / "Deselect All" options
- Goal dependency hints
- Progress indicator (2/6)

**Goals:**
1. 📱 Social Media Lead Generation
2. 🔗 Link in Bio & Websites  
3. 🛍️ E-commerce & Marketplace
4. 🎓 Courses & Education
5. 👥 CRM & Marketing
6. 📊 Analytics & BI
7. 💼 Business Operations
8. 🤖 AI & Content Creation
9. 📱 Mobile & PWA

### **Step 3: Features Selection** ⚠️ NEEDS IMPLEMENTATION  
**Layout:** Categorized feature grid
**Components:**
- Feature cards grouped by selected goals
- Real-time feature counter
- Free plan limit indicator (10/10)
- Upgrade prompt when over limit
- Feature search/filter
- "Select Popular" presets
- Progress indicator (3/6)

### **Step 4: Team Invitations** ⚠️ NEEDS IMPLEMENTATION
**Components:**
- Add team member form (email, name, role)
- Role selector with permissions preview
- Bulk CSV import option
- Team members list with remove option
- Invitation message customization
- "Skip for now" option
- Progress indicator (4/6)

### **Step 5: Subscription Selection** ⚠️ NEEDS IMPLEMENTATION
**Components:**
- Three pricing cards (Free, Professional, Enterprise)
- Monthly/Yearly toggle
- Selected features breakdown
- Real-time cost calculation
- Payment method input (for paid plans)
- Billing address form
- Progress indicator (5/6)

### **Step 6: Branding Setup** ⚠️ NEEDS IMPLEMENTATION
**Components:**
- Logo upload with crop tool
- Color picker for brand colors
- Custom domain input
- Company information form
- Branding preview panel
- "Use default branding" option
- Progress indicator (6/6)

---

## 📊 MAIN DASHBOARD

### **Dashboard Layout**
**Web:**
- Left sidebar with main goals
- Top header with workspace selector
- Main content area with goal cards
- Right panel for quick actions

**Mobile:**
- Bottom tab navigation
- Collapsible header
- Card-based layout
- Floating action button

### **Dashboard Components** ⚠️ NEEDS IMPLEMENTATION
- **Workspace Selector:** Dropdown with logo and switch option
- **Global Search:** Unified search across all features
- **Notification Center:** Real-time notifications panel
- **Quick Stats:** Key metrics summary
- **Recent Activity:** Timeline of workspace actions
- **Main Goal Cards:** 9 dynamic cards based on workspace access

---

## 📱 FEATURE MODULE SPECIFICATIONS

## 1. SOCIAL MEDIA LEAD GENERATION (5 Features)

### **1.1 Instagram Lead Database**

#### **Main Screen: Instagram Database**
**Route:** `/dashboard/instagram`  
**Components:**
- **Search Interface:**
  - Username/hashtag search bar
  - Advanced filters panel (followers, engagement, location)
  - Saved searches dropdown
  - Search history
- **Results Grid:**
  - Profile cards with avatar, stats, verified badge
  - Bulk selection checkboxes
  - Sort options (followers, engagement, recent)
  - Pagination controls
- **Profile Details Modal:**
  - Full profile information
  - Engagement analytics chart
  - Recent posts preview
  - Contact information (if available)
  - Add to lead list button

#### **Leads Management Screen**
**Route:** `/dashboard/instagram/leads`
**Components:**
- **Leads Table:**
  - Profile image, username, followers, engagement rate
  - Status tags (New, Contacted, Qualified, Converted)
  - Last contact date
  - Notes preview
- **Bulk Actions Bar:**
  - Export selected leads
  - Update status
  - Send bulk message
  - Add to campaign
- **Lead Detail Sidebar:**
  - Full profile information
  - Contact history timeline
  - Notes and tags
  - Action buttons (Contact, Qualify, Archive)

#### **Export & Integration Screen**
**Route:** `/dashboard/instagram/export`
**Components:**
- **Export Options:**
  - Format selection (CSV, Excel, JSON)
  - Field customization checklist
  - Filter settings
  - Schedule recurring exports
- **Integration Setup:**
  - CRM connection settings
  - Email marketing integration
  - Webhook configuration
  - API key management

### **1.2 Social Media Scheduling**

#### **Content Calendar Screen**
**Route:** `/dashboard/social/calendar`
**Components:**
- **Calendar View:**
  - Month/Week/Day view toggle
  - Post thumbnails on dates
  - Drag-and-drop rescheduling
  - Multi-platform indicators
- **Post Creation Modal:**
  - Multi-platform composer
  - Image/video upload
  - Caption editor with hashtag suggestions
  - Scheduling date/time picker
  - Preview for each platform
- **Content Library:**
  - Saved posts and templates
  - Media asset browser
  - Hashtag collections
  - Brand asset storage

#### **Publishing Queue Screen**
**Route:** `/dashboard/social/queue`
**Components:**
- **Queue Timeline:**
  - Chronological post preview
  - Platform indicators
  - Status badges (Scheduled, Published, Failed)
  - Bulk reschedule options
- **Performance Preview:**
  - Expected reach estimates
  - Optimal timing suggestions
  - Engagement predictions
  - Content quality score

### **1.3-1.5 Twitter, TikTok, Social Email Integration**
**Similar structure to Instagram with platform-specific features**

## 2. LINK IN BIO & WEBSITES (4 Features)

### **2.1 Bio Link Builder**

#### **Bio Page Builder Screen**
**Route:** `/dashboard/bio-links/builder`
**Components:**
- **Visual Builder:**
  - Drag-and-drop canvas
  - Component library (buttons, text, images, videos)
  - Theme selector
  - Mobile preview panel
- **Link Management Panel:**
  - Add link form
  - Link list with analytics preview
  - UTM parameter builder
  - Link scheduling options
- **Design Customization:**
  - Color scheme editor
  - Font selector
  - Background options (solid, gradient, image)
  - Custom CSS editor (advanced)

#### **Bio Page Analytics Screen**
**Route:** `/dashboard/bio-links/analytics`
**Components:**
- **Traffic Overview:**
  - Total clicks chart
  - Click-through rate
  - Top performing links
  - Geographic data map
- **Link Performance Table:**
  - Individual link statistics
  - Click timestamps
  - Referrer information
  - Device breakdown
- **Audience Insights:**
  - Visitor demographics
  - Peak activity times
  - Return visitor rate
  - Conversion tracking

### **2.2 Website Builder**

#### **Website Builder Screen**
**Route:** `/dashboard/websites/builder`
**Components:**
- **Page Builder:**
  - Drag-and-drop editor
  - Pre-built sections
  - Template library
  - Responsive preview modes
- **Site Management:**
  - Page tree navigation
  - SEO settings per page
  - Menu builder
  - Global settings
- **Asset Manager:**
  - Image library
  - File upload system
  - CDN integration
  - Optimization tools

#### **Website Analytics Screen**
**Route:** `/dashboard/websites/analytics`
**Components:**
- **Traffic Dashboard:**
  - Visitor statistics
  - Page performance
  - Traffic sources
  - Goal conversions
- **SEO Performance:**
  - Search rankings
  - Keyword performance
  - Page speed scores
  - Mobile usability

### **2.3 Link Shortener & 2.4 SEO Tools**
**Integrated within bio link and website builders**

## 3. E-COMMERCE & MARKETPLACE (5 Features)

### **3.1 E-commerce Store**

#### **Store Dashboard**
**Route:** `/dashboard/ecommerce`
**Components:**
- **Store Overview:**
  - Revenue metrics
  - Order statistics
  - Top products
  - Conversion rates
- **Quick Actions:**
  - Add product button
  - Process orders
  - Manage inventory
  - View analytics

#### **Product Management Screen**
**Route:** `/dashboard/ecommerce/products`
**Components:**
- **Product Grid:**
  - Product cards with images
  - Stock status indicators
  - Price and variants
  - Quick edit options
- **Product Editor Modal:**
  - Product information form
  - Image gallery manager
  - Variants configuration
  - SEO settings
  - Inventory tracking
- **Bulk Actions:**
  - Import/export products
  - Update pricing
  - Manage categories
  - Stock adjustments

#### **Order Management Screen**
**Route:** `/dashboard/ecommerce/orders`
**Components:**
- **Orders Table:**
  - Order details (ID, customer, total, status)
  - Status update dropdown
  - Fulfillment tracking
  - Payment status
- **Order Detail Panel:**
  - Customer information
  - Order timeline
  - Product details
  - Shipping information
  - Payment history

### **3.2 Multi-vendor Marketplace**

#### **Vendor Dashboard**
**Route:** `/dashboard/marketplace/vendors`
**Components:**
- **Vendor List:**
  - Vendor cards with metrics
  - Status indicators (Active, Pending, Suspended)
  - Commission tracking
  - Performance scores
- **Vendor Detail Screen:**
  - Vendor profile information
  - Product catalog
  - Sales analytics
  - Commission statements
  - Communication tools

#### **Marketplace Analytics Screen**
**Route:** `/dashboard/marketplace/analytics`
**Components:**
- **Revenue Dashboard:**
  - Total marketplace revenue
  - Commission breakdown
  - Vendor performance comparison
  - Growth metrics
- **Product Performance:**
  - Best-selling products
  - Category analysis
  - Vendor contributions
  - Market trends

### **3.3 Payment Processing**

#### **Payment Settings Screen**
**Route:** `/dashboard/payments`
**Components:**
- **Gateway Configuration:**
  - Stripe integration setup
  - PayPal configuration
  - Payment method toggles
  - Currency settings
- **Transaction History:**
  - Payment timeline
  - Transaction details
  - Refund management
  - Dispute handling

### **3.4 Escrow System & 3.5 Promotions**
**Integrated within e-commerce workflows**

## 4. COURSES & EDUCATION (2 Features)

### **4.1 Course Platform**

#### **Course Dashboard**
**Route:** `/dashboard/courses`
**Components:**
- **Course Overview:**
  - Course list with enrollment stats
  - Revenue metrics
  - Student engagement scores
  - Completion rates
- **Quick Actions:**
  - Create new course
  - View student progress
  - Access course builder
  - Manage discussions

#### **Course Builder Screen**
**Route:** `/dashboard/courses/builder/{course_id}`
**Components:**
- **Curriculum Builder:**
  - Drag-and-drop lesson organizer
  - Section and lesson editor
  - Content type selector (video, text, quiz, assignment)
  - Progress tracking setup
- **Content Editor:**
  - Rich text editor
  - Video upload and player
  - Interactive elements
  - Resource attachments
- **Assessment Builder:**
  - Quiz creator
  - Assignment manager
  - Grading rubrics
  - Certificate templates

#### **Student Management Screen**
**Route:** `/dashboard/courses/students`
**Components:**
- **Student Directory:**
  - Student list with progress
  - Enrollment status
  - Engagement metrics
  - Communication tools
- **Progress Tracking:**
  - Individual student dashboards
  - Completion analytics
  - Performance reports
  - Intervention alerts

### **4.2 Template Marketplace**

#### **Template Gallery Screen**
**Route:** `/dashboard/templates`
**Components:**
- **Template Browser:**
  - Category filters
  - Template previews
  - Popularity indicators
  - Price information
- **Template Editor:**
  - Customization interface
  - Preview modes
  - Asset replacement
  - Export options

## 5. CRM & MARKETING (6 Features)

### **5.1 CRM System**

#### **CRM Dashboard**
**Route:** `/dashboard/crm`
**Components:**
- **Pipeline Overview:**
  - Deal stages visualization
  - Revenue forecasting
  - Activity timeline
  - Key metrics
- **Contact Summary:**
  - Recent contacts
  - Lead sources
  - Conversion rates
  - Task reminders

#### **Contacts Screen**
**Route:** `/dashboard/crm/contacts`
**Components:**
- **Contact List:**
  - Contact cards with photos
  - Last interaction date
  - Deal value
  - Status indicators
- **Contact Detail Panel:**
  - Contact information form
  - Interaction history
  - Deal pipeline
  - Task management
  - Email integration

#### **Pipeline Management Screen**
**Route:** `/dashboard/crm/pipeline`
**Components:**
- **Pipeline Board:**
  - Kanban-style deal cards
  - Drag-and-drop between stages
  - Deal value indicators
  - Probability scores
- **Deal Detail Modal:**
  - Deal information
  - Contact associations
  - Activity timeline
  - File attachments
  - Next steps

### **5.2 Email Marketing**

#### **Campaign Manager Screen**
**Route:** `/dashboard/email/campaigns`
**Components:**
- **Campaign List:**
  - Campaign cards with metrics
  - Status indicators
  - Performance preview
  - Duplicate/edit options
- **Email Builder:**
  - Drag-and-drop editor
  - Template library
  - Personalization tools
  - Preview modes
- **Audience Segmentation:**
  - List management
  - Segment builder
  - Import/export tools
  - Engagement scoring

#### **Email Analytics Screen**
**Route:** `/dashboard/email/analytics`
**Components:**
- **Performance Dashboard:**
  - Open rates
  - Click-through rates
  - Conversion tracking
  - List growth metrics
- **Campaign Comparison:**
  - A/B test results
  - Performance trends
  - Engagement heatmaps
  - ROI calculations

### **5.3-5.6 Lead Management, Customer Experience, Workflow Automation, Campaign Management**
**Similar detailed specifications for each feature**

## 6. ANALYTICS & BUSINESS INTELLIGENCE (4 Features)

### **6.1 Business Analytics**

#### **Analytics Dashboard**
**Route:** `/dashboard/analytics`
**Components:**
- **Unified Metrics:**
  - Cross-platform performance
  - Revenue attribution
  - Customer journey mapping
  - Goal tracking
- **Custom Reports:**
  - Report builder interface
  - Data visualization tools
  - Scheduled reports
  - Export options

### **6.2-6.4 Business Intelligence, Custom Reports, Financial Analytics**
**Detailed specifications for each analytics feature**

## 7. BUSINESS OPERATIONS (5 Features)

### **7.1 Booking System**

#### **Booking Calendar**
**Route:** `/dashboard/bookings`
**Components:**
- **Calendar Interface:**
  - Month/week/day views
  - Appointment blocks
  - Availability settings
  - Color-coded services
- **Appointment Details:**
  - Client information
  - Service details
  - Payment status
  - Notes and history

### **7.2-7.5 Financial Management, Form Builder, Survey Tools, Blog Platform**
**Complete specifications for each business tool**

## 8. AI & CONTENT CREATION (3 Features)

### **8.1 AI Content Generation**

#### **Content Generator Screen**
**Route:** `/dashboard/ai/content`
**Components:**
- **Content Templates:**
  - Blog post generator
  - Social media captions
  - Email templates
  - Product descriptions
- **AI Editor:**
  - Prompt interface
  - Generated content preview
  - Editing tools
  - Export options

### **8.2-8.3 AI Tools, Content Creation Tools**
**Detailed AI-powered feature specifications**

## 9. MOBILE & PWA (2 Features)

### **9.1-9.2 Progressive Web App, Mobile Features**
**Native mobile interface specifications**

---

## 📱 MOBILE-SPECIFIC COMPONENTS

### **Native Mobile Navigation**
- **Bottom Tab Bar:** 5 main sections
- **Floating Action Button:** Quick actions
- **Slide-out Menu:** Additional options
- **Gesture Navigation:** Swipe interactions

### **Mobile-Optimized Widgets**
- **Card Layouts:** Stacked content
- **Form Controls:** Touch-friendly inputs
- **Modal Sheets:** Bottom-up modals
- **Pull-to-Refresh:** Data refreshing
- **Infinite Scroll:** Content loading

---

## 🎨 DESIGN SYSTEM SPECIFICATIONS

### **Component Library**
```
- Buttons (Primary, Secondary, Ghost, Icon)
- Forms (Input, Select, Textarea, Checkbox, Radio)
- Navigation (Sidebar, Tabs, Breadcrumbs, Pagination)
- Data Display (Tables, Cards, Lists, Metrics)
- Feedback (Alerts, Toasts, Loading, Empty States)
- Overlays (Modals, Drawers, Tooltips, Popovers)
```

### **Responsive Breakpoints**
```css
/* Mobile First */
xs: 320px   /* Small phones */
sm: 576px   /* Large phones */
md: 768px   /* Tablets */
lg: 992px   /* Small desktops */
xl: 1200px  /* Large desktops */
xxl: 1400px /* Extra large screens */
```

---

## 📊 IMPLEMENTATION SUMMARY

### **Total Frontend Requirements:**
- **🏠 Core Screens:** 25+ main screens
- **📱 Feature Modules:** 36 feature interfaces  
- **🎨 Components:** 200+ reusable components
- **📝 Forms:** 150+ forms and inputs
- **📊 Data Tables:** 50+ data management interfaces
- **🔔 Modals/Popups:** 100+ overlays and dialogs
- **📱 Mobile Screens:** Native mobile versions of all web screens

### **Development Estimate:**
- **Web Application:** 8-10 weeks
- **Mobile Application:** 6-8 weeks (after web completion)
- **Total Development:** 14-18 weeks with 3-4 developers

---

*Complete Frontend Specification: 36 Sellable Features Across 9 Main Goals*  
*Every Screen, Widget, Popup & Page Documented for Web + Mobile*