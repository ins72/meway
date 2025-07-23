# Mewayz Platform v2 - API Reference
**Version 2.0 | Updated: June 2025**

## Authentication

All API requests require authentication using JWT tokens.

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

### Register
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password",
  "name": "User Name"
}
```

## Core Platform APIs

### Workspace Management
- `GET /api/workspaces` - List user workspaces
- `POST /api/workspaces` - Create new workspace
- `GET /api/workspaces/{id}` - Get workspace details
- `PUT /api/workspaces/{id}` - Update workspace
- `DELETE /api/workspaces/{id}` - Delete workspace
- `POST /api/workspaces/{id}/invite` - Invite user to workspace
- `POST /api/workspaces/invitations/{token}/accept` - Accept invitation

### Social Media Management
- `GET /api/social/instagram/search` - Search Instagram database
- `POST /api/social/posts/schedule` - Schedule social media post
- `GET /api/social/posts` - Get scheduled posts
- `POST /api/social/leads/export` - Export lead data
- `GET /api/social/analytics` - Get social media analytics

### Link in Bio
- `GET /api/link-in-bio/pages` - Get user's bio pages
- `POST /api/link-in-bio/pages` - Create new bio page
- `PUT /api/link-in-bio/pages/{id}` - Update bio page
- `GET /api/link-in-bio/templates` - Get available templates
- `GET /api/link-in-bio/analytics/{id}` - Get page analytics

### Course & Community
- `GET /api/courses` - List courses
- `POST /api/courses` - Create new course
- `GET /api/courses/{id}` - Get course details
- `POST /api/courses/{id}/lessons` - Add lesson to course
- `GET /api/community/groups` - List community groups
- `POST /api/community/groups` - Create new group

### E-commerce & Marketplace
- `GET /api/ecommerce/products` - List products
- `POST /api/ecommerce/products` - Create new product
- `GET /api/ecommerce/orders` - Get orders
- `POST /api/marketplace/templates` - Submit template for sale
- `GET /api/marketplace/templates` - Browse marketplace templates

### CRM & Email Marketing
- `GET /api/crm/contacts` - List contacts
- `POST /api/crm/contacts` - Add new contact
- `GET /api/crm/campaigns` - List email campaigns
- `POST /api/crm/campaigns` - Create email campaign
- `GET /api/crm/analytics` - Get CRM analytics

### Booking System
- `GET /api/booking/services` - List booking services
- `POST /api/booking/appointments` - Create appointment
- `GET /api/booking/calendar` - Get calendar availability
- `PUT /api/booking/appointments/{id}` - Update appointment

### Financial Management
- `GET /api/finance/invoices` - List invoices
- `POST /api/finance/invoices` - Create invoice
- `GET /api/finance/payments` - List payments
- `POST /api/finance/payments` - Process payment
- `GET /api/finance/reports` - Get financial reports

### Analytics & Reporting
- `GET /api/analytics/dashboard` - Get analytics dashboard
- `GET /api/analytics/reports` - List available reports
- `POST /api/analytics/reports/custom` - Create custom report
- `GET /api/analytics/metrics/{type}` - Get specific metrics

### AI & Automation
- `POST /api/ai/content/generate` - Generate AI content
- `POST /api/ai/images/generate` - Generate AI images
- `GET /api/automation/workflows` - List workflows
- `POST /api/automation/workflows` - Create workflow

### Mobile PWA
- `GET /api/pwa/manifest` - Get PWA manifest
- `POST /api/pwa/notifications/subscribe` - Subscribe to push notifications
- `POST /api/pwa/offline/sync` - Sync offline data
- `GET /api/pwa/analytics` - Get PWA analytics

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-06-23T10:00:00Z"
}
```

## Error Handling

Error responses include:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {}
  },
  "timestamp": "2025-06-23T10:00:00Z"
}
```

## Rate Limiting

- Standard users: 1000 requests/hour
- Premium users: 5000 requests/hour
- Enterprise users: Unlimited

## Webhook Events

Available webhook events:
- `workspace.created`
- `user.invited`
- `post.published`
- `order.created`
- `payment.completed`
- `course.completed`

---

For complete API documentation with examples, visit: https://docs.mewayz.com/api

*Copyright © 2025 Mewayz. All rights reserved.*