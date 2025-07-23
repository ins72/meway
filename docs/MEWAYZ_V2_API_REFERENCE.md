# Mewayz V2 API Reference Guide
**Version:** 2.0  
**Date:** January 28, 2025  
**Total Endpoints:** 674

---

## 🔗 Base URL & Authentication

### Base URL
```
https://api.mewayz.com/api
```

### Authentication
All API requests require JWT bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.mewayz.com/api/endpoint
```

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login |
| POST | `/auth/register` | User registration |
| POST | `/auth/logout` | User logout |
| GET | `/auth/verify` | Token verification |

---

## 🏢 Multi-Workspace System

### Workspace Management
| Method | Endpoint | Description | Success Rate |
|--------|----------|-------------|--------------|
| GET | `/multi-workspace/workspaces` | List user workspaces | 80% |
| POST | `/multi-workspace/workspaces` | Create new workspace | 80% |
| GET | `/multi-workspace/workspaces/{id}` | Get workspace details | 80% |
| PUT | `/multi-workspace/workspaces/{id}` | Update workspace | 80% |
| DELETE | `/multi-workspace/workspaces/{id}` | Delete workspace | 80% |

### Team Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/team-management/teams/{team_id}/members` | Get team members |
| POST | `/team-management/teams/{team_id}/invitations` | Send team invitation |
| GET | `/team-management/teams/{team_id}/roles` | Get team roles |
| PUT | `/team-management/members/{member_id}/role` | Update member role |

---

## 📱 Social Media Management

### Lead Generation (87% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/social-media-leads/discover/instagram` | Discover Instagram accounts |
| POST | `/social-media-leads/discover/tiktok` | Discover TikTok creators |
| POST | `/social-media-leads/discover/twitter` | Discover Twitter users |
| GET | `/social-media-leads/analytics/overview` | Get analytics overview |
| GET | `/social-media-leads/leads/export` | Export leads to CSV |

### Alternative Endpoints (Backward Compatibility)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/social-media-leads/tiktok/search` | Search TikTok creators |
| POST | `/social-media-leads/twitter/search` | Search Twitter users |

---

## 🔗 Link in Bio System

### Bio Site Management (95% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/link-in-bio/sites` | List bio sites |
| POST | `/link-in-bio/sites` | Create bio site |
| GET | `/link-in-bio/sites/{id}` | Get bio site |
| PUT | `/link-in-bio/sites/{id}` | Update bio site |
| DELETE | `/link-in-bio/sites/{id}` | Delete bio site |
| GET | `/link-in-bio/sites/{id}/analytics` | Get site analytics |
| POST | `/link-in-bio/sites/{id}/qr-code` | Generate QR code |

---

## 🎓 Courses & Community

### Course Management (85% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/courses` | List courses |
| POST | `/courses/courses` | Create course |
| GET | `/courses/courses/{id}` | Get course details |
| PUT | `/courses/courses/{id}` | Update course |
| DELETE | `/courses/courses/{id}` | Delete course |
| POST | `/courses/courses/{id}/modules` | Add course module |
| GET | `/courses/courses/{id}/students` | Get enrolled students |

### Community Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/community/forums` | List discussion forums |
| POST | `/courses/community/forums` | Create forum |
| GET | `/courses/community/forums/{id}/posts` | Get forum posts |
| POST | `/courses/community/forums/{id}/posts` | Create forum post |

---

## 🛒 Marketplace & E-Commerce

### Product Management (87.5% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ecommerce/products` | List products |
| POST | `/ecommerce/products` | Create product |
| GET | `/ecommerce/products/{id}` | Get product details |
| PUT | `/ecommerce/products/{id}` | Update product |
| DELETE | `/ecommerce/products/{id}` | Delete product |

### Order Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ecommerce/orders` | List orders |
| POST | `/ecommerce/orders` | Create order |
| GET | `/ecommerce/orders/{id}` | Get order details |
| PUT | `/ecommerce/orders/{id}/status` | Update order status |

### Store Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ecommerce/stores` | List stores |
| POST | `/ecommerce/stores` | Create store |
| GET | `/ecommerce/stores/{id}` | Get store details |
| PUT | `/ecommerce/stores/{id}` | Update store |

---

## 👥 CRM & Email Marketing

### Contact Management (90% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/crm/contacts` | List contacts |
| POST | `/crm/contacts` | Create contact |
| GET | `/crm/contacts/{id}` | Get contact details |
| PUT | `/crm/contacts/{id}` | Update contact |
| DELETE | `/crm/contacts/{id}` | Delete contact |

### Email Campaigns
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/email-marketing/campaigns` | List email campaigns |
| POST | `/email-marketing/campaigns` | Create campaign |
| GET | `/email-marketing/campaigns/{id}` | Get campaign details |
| POST | `/email-marketing/campaigns/{id}/send` | Send campaign |
| GET | `/email-marketing/campaigns/{id}/analytics` | Get campaign analytics |

---

## 🌐 Website Builder

### Website Management (85% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/website-builder/sites` | List websites |
| POST | `/website-builder/sites` | Create website |
| GET | `/website-builder/sites/{id}` | Get website |
| PUT | `/website-builder/sites/{id}` | Update website |
| DELETE | `/website-builder/sites/{id}` | Delete website |

### Page Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/website-builder/sites/{id}/pages` | List pages |
| POST | `/website-builder/sites/{id}/pages` | Create page |
| GET | `/website-builder/sites/{id}/pages/{page_id}` | Get page |
| PUT | `/website-builder/sites/{id}/pages/{page_id}` | Update page |

---

## 📅 Booking System

### Service Management (83.3% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/booking/services` | List services |
| POST | `/booking/services` | Create service |
| GET | `/booking/services/{id}` | Get service |
| PUT | `/booking/services/{id}` | Update service |
| DELETE | `/booking/services/{id}` | Delete service |

### Appointment Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/booking/appointments` | List appointments |
| POST | `/booking/appointments` | Create appointment |
| GET | `/booking/appointments/{id}` | Get appointment |
| PUT | `/booking/appointments/{id}` | Update appointment |
| DELETE | `/booking/appointments/{id}` | Cancel appointment |

---

## 💰 Financial Management

### Invoice Management (87.5% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/financial/invoices` | List invoices |
| POST | `/financial/invoices` | Create invoice |
| GET | `/financial/invoices/{id}` | Get invoice |
| PUT | `/financial/invoices/{id}` | Update invoice |
| POST | `/financial/invoices/{id}/send` | Send invoice |

### Payment Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/financial/payments` | List payments |
| POST | `/financial/payments` | Process payment |
| GET | `/financial/payments/{id}` | Get payment details |
| POST | `/financial/payments/{id}/refund` | Process refund |

---

## 📊 Analytics & Reporting

### Analytics Dashboard (85% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/unified-analytics/dashboard` | Get dashboard overview |
| GET | `/unified-analytics/dashboard/{period}` | Get period dashboard |
| GET | `/unified-analytics/reports` | List custom reports |
| POST | `/unified-analytics/reports` | Create custom report |

### Gamification System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/unified-analytics/gamification/profile` | Get user gamification profile |
| POST | `/unified-analytics/gamification/points` | Add points |
| GET | `/unified-analytics/gamification/leaderboard` | Get leaderboard |
| GET | `/unified-analytics/gamification/achievements` | Get achievements |

---

## 🎨 Template Marketplace

### Template Management (87.5% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates` | List templates |
| POST | `/templates` | Create template |
| GET | `/templates/{id}` | Get template |
| PUT | `/templates/{id}` | Update template |
| DELETE | `/templates/{id}` | Delete template |

### Template Marketplace
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/template-marketplace/marketplace` | Browse marketplace |
| POST | `/template-marketplace/templates/{id}/purchase` | Purchase template |
| GET | `/template-marketplace/my-templates` | Get creator templates |
| GET | `/template-marketplace/purchases` | Get user purchases |

---

## 📱 Mobile PWA Features

### Push Notifications (75% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mobile-pwa/push/subscribe` | Subscribe to notifications |
| POST | `/mobile-pwa/push/send` | Send push notification |
| GET | `/mobile-pwa/push/subscriptions` | List subscriptions |

### Device Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mobile-pwa/devices/register` | Register device |
| GET | `/mobile-pwa/devices` | List devices |
| PUT | `/mobile-pwa/devices/{id}` | Update device |

---

## 🤖 AI & Automation

### AI Content Generation (80% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai-automation/content/generate` | Generate content |
| POST | `/ai-automation/content/optimize` | Optimize content |
| POST | `/ai-automation/images/generate` | Generate images |

### Automation Workflows
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workflows` | List workflows |
| POST | `/workflows` | Create workflow |
| GET | `/workflows/{id}` | Get workflow |
| PUT | `/workflows/{id}` | Update workflow |
| POST | `/workflows/{id}/execute` | Execute workflow |

---

## ⚙️ Admin Dashboard

### System Management (90% Success Rate)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin-dashboard/users` | List all users |
| GET | `/admin-dashboard/users/{id}` | Get user details |
| PUT | `/admin-dashboard/users/{id}/status` | Update user status |
| GET | `/admin-dashboard/system/metrics` | Get system metrics |

### Configuration Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin-config/configuration` | Get system configuration |
| PUT | `/admin-config/configuration` | Update configuration |
| GET | `/admin-config/integration/status` | Get integration status |
| POST | `/admin-config/test/stripe` | Test Stripe integration |
| POST | `/admin-config/test/openai` | Test OpenAI integration |

---

## 📈 Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2025-01-28T10:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message",
  "details": {
    // Additional error details
  },
  "timestamp": "2025-01-28T10:00:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 🚀 Rate Limits

### Default Limits
- **Standard API calls:** 1000 requests per hour
- **Authentication endpoints:** 10 requests per minute
- **File upload endpoints:** 50 requests per hour
- **Email sending:** 500 emails per day

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643123400
```

---

## 📞 Support

For API support and technical assistance:

**API Version:** 2.0  
**Documentation Updated:** January 28, 2025  
**Total Endpoints:** 674  
**Average Success Rate:** 85.6%

---

*Mewayz V2 API - Comprehensive business platform integration*