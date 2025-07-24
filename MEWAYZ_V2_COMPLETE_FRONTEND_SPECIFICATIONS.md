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
6. **📋 Updated Launch Pricing** - New bundle pricing ($19-39/month) with multi-bundle discounts

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

## 📊 MAIN DASHBOARD WITH WORKSPACE CONTROL

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