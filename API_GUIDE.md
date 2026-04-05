# URL Shortener API - Getting Started Guide

## Overview

PopOff is a Django REST API that enables users to create, manage, and track shortened URLs with analytics. Core features include:

- **User Authentication** — JWT-based token authentication
- **Link Management** — Create, list, retrieve, and delete short links
- **Custom Aliases** — Optional custom short codes for links
- **Expiration Support** — Set links to expire at a specific date/time
- **Click Analytics** — Track clicks with metadata (country, device, referrer, IP)
- **Rate Limiting** — Prevent abuse with request throttling
- **Interactive Documentation** — Swagger UI for easy API exploration

---

## Setup & Installation

### 1. Create Virtual Environment
```bash
cd url_shortener_backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install Django==5.0 djangorestframework djangorestframework-simplejwt dj-database-url psycopg2-binary python-dotenv drf-spectacular
```

### 3. Apply Migrations
```bash
# Temporarily move .env to use SQLite locally
mv .env .env.bak
python manage.py migrate
mv .env.bak .env
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Server runs at: **http://127.0.0.1:8000**

---

## Documentation & Testing

### **Interactive Swagger UI** 
Open your browser to: **http://localhost:8000/api/docs/**

This provides:
- Full API documentation
- Interactive endpoint testing
- Request/response examples
- JWT token injection for testing

### **OpenAPI Schema**
- JSON format: http://localhost:8000/api/schema/?format=json
- YAML format: http://localhost:8000/api/schema/

---

## API Endpoints

### Authentication

#### Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

---

#### Login & Get JWT Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Store the `access` token** — Use it in the `Authorization` header for authenticated requests.

---

#### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

#### Logout (Blacklist Token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

### Link Management

> **Required:** All link management endpoints require JWT authentication.
> Add this header: `Authorization: Bearer YOUR_ACCESS_TOKEN`

#### Create a Short Link (Auto-Generated Code)
```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "original_url": "https://github.com"
  }'
```

**Response:**
```json
{
  "shortUrl": "aBc12D",
  "customAlias": null,
  "longUrl": "https://github.com"
}
```

---

#### Create a Short Link with Custom Alias
```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "original_url": "https://python.org",
    "custom_alias": "py"
  }'
```

**Response:**
```json
{
  "shortUrl": "py",
  "customAlias": "py",
  "longUrl": "https://python.org"
}
```

---

#### Create a Link with Expiration
```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "original_url": "https://event.example.com",
    "expires_at": "2026-12-31T23:59:59Z"
  }'
```

Expired links will return HTTP 410 (Gone) when accessed.

---

#### List All User Links (with Pagination)
```bash
curl -X GET "http://localhost:8000/api/v1/urls/getall/?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "id": 1,
      "short_code": "aBc12D",
      "original_url": "https://github.com",
      "custom_alias": null,
      "user": 2,
      "is_active": true,
      "expires_at": null
    }
  ]
}
```

**Pagination Parameters:**
- `limit` — Results per page (default: 10, max: 100)
- `offset` — Number of results to skip (default: 0)

---

#### Get Link Details
```bash
curl -X GET "http://localhost:8000/api/v1/urls/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

#### Get Link Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/urls/1/analytics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "link_info": {
    "short_url": "http://localhost:8000/aBc12D/",
    "original_url": "https://github.com",
    "created_at": "2026-04-05T20:30:00Z",
    "is_active": true,
    "expires_at": null
  },
  "total_clicks": 42,
  "clicks_by_country": [
    {
      "country": "US",
      "count": 25
    },
    {
      "country": "GB",
      "count": 17
    }
  ]
}
```

---

#### Delete a Link
```bash
curl -X DELETE "http://localhost:8000/api/v1/urls/delete/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:** HTTP 204 (No Content)

---

### Redirects (No Authentication Required)

#### Follow a Short Link
```bash
curl -i http://localhost:8000/aBc12D/
```

**Response:** HTTP 302 with `Location` header pointing to the original URL.

Browser will automatically follow the redirect. Example:
```
HTTP/1.1 302 Found
Location: https://github.com
```

---

#### Invalid/Expired Links
```bash
curl -i http://localhost:8000/invalid_code/
```

**Response:** HTTP 404 (Not Found)

---

```bash
curl -i http://localhost:8000/expired_code/
```

**Response:** HTTP 410 (Gone) - Link has expired

---

## Rate Limiting

The API enforces rate limits to prevent abuse:

| Endpoint | Limit | Window |
|----------|-------|--------|
| Create Link | 100 | 1 hour |
| Redirect | 1000 | 1 hour |

Exceeding limits returns HTTP 429 (Too Many Requests):
```json
{
  "error": "Rate limit exceeded. Max 100 requests per 3600 seconds"
}
```

---

## Complete Testing Workflow

### Step 1: Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!"}'
```

### Step 2: Get Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!"}' | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"
```

### Step 3: Create a Link
```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"original_url":"https://example.com","custom_alias":"ex"}'
```

### Step 4: List Links
```bash
curl -X GET "http://localhost:8000/api/v1/urls/getall/?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 5: Follow Redirect
```bash
curl -i http://localhost:8000/ex/
```

### Step 6: Get Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/urls/1/analytics/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Responses

### Invalid Request
```json
{
  "error": "URL must start with http:// or https://"
}
```
Status: `400 Bad Request`

---

### Unauthorized (Missing Token)
```json
{
  "detail": "Authentication credentials were not provided."
}
```
Status: `401 Unauthorized`

---

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded. Max 100 requests per 3600 seconds"
}
```
Status: `429 Too Many Requests`

---

### Link Not Found
```json
{
  "error": "Link not found"
}
```
Status: `404 Not Found`

---

## Database Models

### Links
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `user` | FK | Link owner |
| `short_code` | String(7) | Unique short code |
| `custom_alias` | String(50) | Optional custom alias |
| `original_url` | URL | Target URL |
| `is_active` | Boolean | Active status |
| `expires_at` | DateTime | Expiration timestamp |
| `created_at` | DateTime | Creation timestamp |

### Clicks
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `link` | FK | Associated link |
| `timestamp` | DateTime | Click time |
| `country` | String(3) | ISO country code |
| `device_type` | String | Device category |
| `referrer` | URL | HTTP referrer |
| `user_agent` | Text | User agent string |
| `ip_address` | IP | Visitor IP |

---

## Environment Variables

Create a `.env` file in the project root:

```
# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@hostname:5432/dbname

# Or use SQLite (Development)
# Leave DATABASE_URL unset to use SQLite
```

---

## Common Issues

### "ModuleNotFoundError: No module named 'django'"
**Solution:** Run `pip install -r requirements.txt` or activate the virtual environment.

---

### "Tenant or user not found" (PostgreSQL)
**Solution:** Move `.env` to `.env.bak` before running migrations to use SQLite locally.

---

### "Authentication credentials were not provided"
**Solution:** Add `Authorization: Bearer YOUR_ACCESS_TOKEN` header to requests.

---

### Link doesn't redirect
**Solution:** Check if link is expired. View analytics to verify it exists and is active.

---

## Performance Tips

1. **Use Pagination** — Always specify `limit` and `offset` for list endpoints
2. **Cache Tokens** — Reuse JWT tokens; they're valid for 30 minutes
3. **Batch Requests** — Create multiple links in a testing script
4. **Monitor Analytics** — Check clicks_by_country for traffic patterns

---

## Architecture

```
Client Browser (Angular/Postman)
    ↓
Django REST API (ASGI/WSGI)
    ↓
Authentication (JWT)
    ↓
Views & Serializers
    ↓
SQLite/PostgreSQL Database
    ↓
Click Analytics (Append-only)
```

---

## Future Enhancements

- [ ] Implement Celery for async click analytics
- [ ] Add Redis caching for sub-50ms redirects
- [ ] Migrate to PostgreSQL for production
- [ ] Add user dashboard with charts
- [ ] Implement QR code generation
- [ ] Add custom domains support

---

## Support

For questions or issues, refer to:
- **Swagger UI:** http://localhost:8000/api/docs/
- **Architecture Doc:** [URL_Shortener_Platform_Architecture.md](URL_Shortener_Platform_Architecture.md)
- **Code:** Check `api/views.py` and `api/models.py`
