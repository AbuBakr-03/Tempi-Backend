# Tempi - Job Marketplace API

A Django REST API for connecting job seekers with companies for temporary work opportunities.

## Features

- **Dual User System**: Regular users and company profiles
- **Job Management**: Companies can post jobs, users can apply
- **Wishlist System**: Save interesting job opportunities
- **Application Tracking**: Full application lifecycle management
- **Job Assignments**: Match users to jobs with status tracking
- **JWT Authentication**: Secure token-based authentication
- **File Storage**: Cloudflare R2 integration for resumes and profile pictures

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT with Djoser
- **Storage**: Cloudflare R2
- **Deployment**: Ready for Render

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TempiProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file with:
   ```env
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True
   DATABASE_URL=your_postgres_url
   CLOUDFLARE_R2_BUCKET=your_bucket_name
   CLOUDFLARE_R2_ACCESS_KEY=your_access_key
   CLOUDFLARE_R2_SECRET_KEY=your_secret_key
   CLOUDFLARE_R2_BUCKET_ENDPOINT=your_endpoint_url
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /auth/users/` - User registration
- `POST /auth/jwt/create/` - Login
- `POST /auth/jwt/refresh/` - Refresh token

### Core Features
- `/api/job/` - Browse jobs
- `/api/application/` - Job applications
- `/api/wishlist/` - Saved jobs
- `/api/profile/` - User/company profiles
- `/api/assignments/` - Job assignments

### Admin
- `/api/category/` - Job categories
- `/api/job-type/` - Employment types
- `/admin/` - Django admin panel

## User Types

**Regular Users**: Can browse jobs, apply, manage wishlists, and track assignments
**Companies**: Can post jobs, manage applications, and assign users to positions
