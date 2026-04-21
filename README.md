# PopOff - URL Shortener Backend

PopOff is a robust and scalable URL shortener backend built with Django and Django REST Framework. It provides a comprehensive API for creating, managing, and tracking shortened URLs with optional expiration and analytics.

This project was built to deepen practical experience with Django REST Framework and API design.

AI assistance was used for generating documentation (like this README, API guides, and architecture notes) and for debugging support across the codebase.

---

## Core Features

* **JWT Authentication**: Secure user registration, login, token refresh, and logout.
* **Link Management**: Create, list, retrieve, and delete shortened links.
* **Custom Aliases**: Optionally define your own short codes.
* **Link Expiration**: Set expiration timestamps for temporary links.
* **Link Activation Control**: Enable/disable links dynamically.
* **Click Analytics**: Endpoint available for retrieving link analytics.
* **Protected Routes**: JWT-protected endpoints for user-specific data.
* **OpenAPI Documentation**: Schema-driven API via Swagger.

---

## Technology Stack

* **Backend**: Django, Django REST Framework
* **Authentication**: djangorestframework-simplejwt (JWT)
* **Database**: PostgreSQL (production), SQLite (development)
* **API Docs**: drf-spectacular (OpenAPI/Swagger)

---

## Getting Started

### Prerequisites

* Python 3.x
* `pip` and `venv`

---

### 1. Clone the Repository

```bash
git clone https://github.com/zeroruntime/url_shortener_backend.git
cd url_shortener_backend
```

---

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install Django==5.0 djangorestframework djangorestframework-simplejwt dj-database-url psycopg2-binary python-dotenv drf-spectacular
```

---

### 4. Configure Database

Default is SQLite (no setup needed).

For PostgreSQL, create a `.env` file:

```
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
```

---

### 5. Run Migrations

```bash
python manage.py migrate
```

---

### 6. Start Server

```bash
python manage.py runserver
```

API base URL:

```
http://127.0.0.1:8000/api/
```

---

## API Documentation

Swagger UI:

```
http://127.0.0.1:8000/api/docs/
```

---

## Authentication

### Endpoints

| Method | Endpoint                   | Description                      |
| ------ | -------------------------- | -------------------------------- |
| POST   | `/api/auth/register/`      | Register a new user              |
| POST   | `/api/auth/token/`         | Obtain access + refresh tokens   |
| POST   | `/api/auth/token/refresh/` | Refresh access token             |
| POST   | `/api/auth/logout/`        | Logout (blacklist refresh token) |
| GET    | `/api/auth/protected/`     | Test protected route             |

### Example: Login

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response**

```json
{
  "access": "ACCESS_TOKEN",
  "refresh": "REFRESH_TOKEN"
}
```

---

## Link Management

All endpoints require:

```
Authorization: Bearer <ACCESS_TOKEN>
```

### Endpoints

| Method | Endpoint                     | Description            |
| ------ | ---------------------------- | ---------------------- |
| GET    | `/api/links/`                | List all links         |
| GET    | `/api/links/{id}/`           | Retrieve a single link |
| POST   | `/api/links/shorten/`        | Create a short link    |
| DELETE | `/api/links/{id}/delete/`    | Delete a link          |
| GET    | `/api/links/{id}/analytics/` | Get link analytics     |

---

## Link Object Schema

```json
{
  "id": 1,
  "short_code": "abc123",
  "original_url": "https://example.com",
  "custom_alias": "my-link",
  "user": 1,
  "is_active": true,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

---

## Example: Create Short Link

```bash
curl -X POST http://localhost:8000/api/links/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "original_url": "https://github.com/zeroruntime/url_shortener_backend",
    "custom_alias": "my-repo",
    "is_active": true
  }'
```

**Response**

```json
{
  "id": 1,
  "short_code": "my-repo",
  "original_url": "https://github.com/zeroruntime/url_shortener_backend",
  "custom_alias": "my-repo",
  "user": 1,
  "is_active": true,
  "expires_at": null
}
```
