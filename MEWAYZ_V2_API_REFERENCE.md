# Mewayz v2 - API Reference
*Complete API Documentation - July 22, 2025*

## Authentication
All API requests require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
https://your-domain.com/api
```

## Core Platform APIs

### 1. Marketing Website Suite
```
POST   /api/marketing-website/pages              # Create marketing page with SEO
GET    /api/marketing-website/pages              # List marketing pages
POST   /api/marketing-website/ab-tests           # Create A/B test
GET    /api/marketing-website/ab-tests           # List A/B tests
GET    /api/marketing-website/templates/marketplace # Template marketplace
GET    /api/marketing-website/seo/analysis/{id}  # SEO analysis
GET    /api/marketing-website/analytics/overview # Marketing analytics
```

### 2. Social Media Management Suite
```
POST   /api/social-media-suite/accounts/connect  # Connect social account
GET    /api/social-media-suite/accounts          # List connected accounts
POST   /api/social-media-suite/content/ai-generate # Generate AI content
POST   /api/social-media-suite/listening/setup   # Setup social listening
GET    /api/social-media-suite/listening/mentions # Get brand mentions
POST   /api/social-media-suite/influencers/discover # Discover influencers
GET    /api/social-media-suite/analytics         # Social analytics
GET    /api/social-media-suite/dashboard         # Social dashboard
```

### 3. Enterprise Security & Compliance
```
POST   /api/enterprise-security/compliance/frameworks # Implement compliance
GET    /api/enterprise-security/compliance/frameworks # List frameworks
POST   /api/enterprise-security/threat-detection/setup # Setup threat detection
GET    /api/enterprise-security/threat-detection/alerts # Get threat alerts
POST   /api/enterprise-security/audit/log        # Create audit log
GET    /api/enterprise-security/audit/logs       # Get audit logs
POST   /api/enterprise-security/vulnerability-assessment # Run vulnerability scan
GET    /api/enterprise-security/security/dashboard # Security dashboard
```

### 4. Advanced Business Intelligence
```
POST   /api/business-intelligence/predictive-analytics # Generate predictions
POST   /api/business-intelligence/cohort-analysis # Generate cohort analysis
POST   /api/business-intelligence/funnel-tracking # Track conversion funnels
POST   /api/business-intelligence/competitive-analysis # Competitive intelligence
POST   /api/business-intelligence/custom-reports # Create custom reports
GET    /api/business-intelligence/visualizations # Advanced visualization options
```

### 5. Multi-Vendor Marketplace
```
POST   /api/marketplace/vendors/onboard          # Onboard new vendor
POST   /api/marketplace/vendors/{id}/approve     # Approve vendor
POST   /api/marketplace/pricing/dynamic          # Calculate dynamic pricing
POST   /api/marketplace/vendors/{id}/payout      # Process vendor payout
GET    /api/marketplace/vendors/{id}/performance # Vendor performance metrics
GET    /api/marketplace/vendors                  # List vendors
```

### 6. Advanced Learning Management System
```
POST   /api/lms/scorm/package                    # Create SCORM package
POST   /api/lms/courses/{id}/progress            # Update learning progress
POST   /api/lms/certificates/{id}/generate       # Generate certificate
GET    /api/lms/analytics                        # Learning analytics
GET    /api/lms/gamification                     # Gamification data
GET    /api/lms/courses/scorm                    # List SCORM packages
```

### 7. Existing Core Platform APIs (100+ endpoints)
- User Management (`/api/users/*`)
- Workspace Management (`/api/workspaces/*`)
- CRM System (`/api/crm/*`)
- E-commerce (`/api/e-commerce/*`)
- Email Marketing (`/api/email-marketing/*`)
- Analytics (`/api/analytics/*`)
- Booking System (`/api/booking/*`)
- Financial Management (`/api/finance/*`)
- Admin Configuration (`/api/admin-config/*`)

## Response Format
All API responses follow this structure:
```json
{
  "message": "Description of the operation",
  "data": {}, // Response data
  "success": true,
  "timestamp": "2025-07-22T10:30:00Z"
}
```

## Error Handling
Error responses include:
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {},
  "timestamp": "2025-07-22T10:30:00Z"
}
```

## Rate Limiting
- Standard: 100 requests/minute
- Enterprise: 1000 requests/minute
- Burst: Up to 200 requests in 10 seconds

## Webhook Support
Available for real-time notifications:
- User actions
- Payment events
- Content updates
- Security alerts

*API Version: 2.0*  
*Last Updated: July 22, 2025*