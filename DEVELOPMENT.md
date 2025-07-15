# Mewayz Platform - Development Guide

**Professional Development Documentation for Mewayz Technologies Inc.'s Flagship Platform**

*Building seamless business solutions with modern technology stacks*

---

## 🎯 Platform Overview

Mewayz represents the pinnacle of Mewayz Technologies Inc.'s commitment to creating seamless business management solutions. This development guide provides comprehensive technical documentation for contributing to and extending the Mewayz platform.

### Brand Architecture
- **Mewayz**: The user-facing platform brand
- **Mewayz Technologies Inc.**: The engineering and innovation company
- **Seamless**: Our core development philosophy

### Domain Configuration
- **Production Domain**: mewayz.com
- **Development**: Local environment configurations
- **API Routes**: All backend routes must use `/api` prefix

**Important**: Do not modify environment URLs or domain configurations without proper testing to avoid breaking functionality.

---

## 🏗️ Technical Architecture

### Simplified Laravel-Only Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Laravel       │    │   Database      │
│   (Port 3000)   │◄──►│   (Port 8001)   │◄──►│   MySQL/MariaDB │
│   Static Files  │    │   Complete      │    │   Data Storage  │
│   (Optional)    │    │   Backend       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Backend (Laravel 10+)
- **Framework**: Laravel 10.48.4 (PHP 8.2.28)
- **Database**: MySQL 8.0+ / MariaDB
- **Authentication**: Laravel Sanctum with OAuth 2.0
- **API**: RESTful API with comprehensive endpoints
- **Security**: AES-256, TLS 1.3, 2FA, RBAC
- **Queue**: Redis for background job processing
- **Cache**: Redis for application caching
- **Storage**: Local with S3 compatibility

#### Frontend (Multi-Platform)
- **Web**: Laravel Blade + Vite + Alpine.js
- **Mobile**: Flutter 3.x (Dart)
- **State Management**: Provider (Flutter)
- **Styling**: Tailwind CSS + Custom Design System
- **PWA**: Service Worker with offline capabilities
- **Build Tools**: Vite for asset compilation

#### Development Tools
- **Composer**: PHP dependency management
- **NPM/Yarn**: JavaScript dependency management
- **Vite**: Modern build tool and dev server
- **PHP CS Fixer**: Code style fixing
- **ESLint**: JavaScript linting
- **Prettier**: Code formatting

---

## 📦 Project Structure

```
mewayz/
├── app/                    # Laravel application
│   ├── Http/
│   │   ├── Controllers/    # API and web controllers
│   │   ├── Middleware/     # Custom middleware
│   │   └── Requests/       # Form requests
│   ├── Models/             # Eloquent models
│   ├── Services/           # Business logic services
│   └── Providers/          # Service providers
├── config/                 # Configuration files
├── database/
│   ├── migrations/         # Database migrations
│   ├── seeders/           # Database seeders
│   └── factories/         # Model factories
├── resources/
│   ├── views/             # Blade templates
│   ├── js/                # JavaScript assets
│   └── sass/              # Sass stylesheets
├── routes/
│   ├── api.php            # API routes
│   ├── web.php            # Web routes
│   └── auth.php           # Authentication routes
├── flutter_app/           # Flutter mobile application
│   ├── lib/
│   │   ├── screens/       # Flutter screens
│   │   ├── widgets/       # Custom widgets
│   │   ├── services/      # API services
│   │   └── providers/     # State management
│   └── pubspec.yaml       # Flutter dependencies
├── public/                # Public web assets
├── storage/               # Storage directories
├── tests/                 # Test files
└── vendor/                # Composer dependencies
```

---

## 🚀 Development Setup

### Prerequisites

- **PHP**: 8.2.28 or higher
- **Composer**: Latest version
- **Node.js**: 18+ LTS
- **MySQL/MariaDB**: 8.0+
- **Redis**: 6.0+ (optional but recommended)
- **Flutter**: 3.x (for mobile development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mewayz/mewayz.git
   cd mewayz
   ```

2. **Install dependencies**
   ```bash
   composer install
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   php artisan key:generate
   ```

4. **Database setup**
   ```bash
   php artisan migrate
   php artisan db:seed
   ```

5. **Build assets**
   ```bash
   npm run dev
   ```

6. **Start development server**
   ```bash
   php artisan serve --host=0.0.0.0 --port=8001
   ```

### Flutter Development

```bash
cd flutter_app
flutter pub get
flutter run -d chrome
```
