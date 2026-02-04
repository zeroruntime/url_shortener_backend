# URL Shortener Platform Architecture

**Extended Technical Design & Implementation Specification**
**Backend:** Django + Django REST Framework
**Frontend:** Angular 21 + Tailwind CSS

---

## Purpose and Scope

The URL Shortener Platform is a multi-tenant web system that enables users to create, manage, and analyze shortened URLs. The system provides deterministic link redirection, click analytics, and abuse-resistant link generation while maintaining low-latency redirect performance.

The platform is an infrastructure service for URL mapping and analytics. It is not a content host, malware scanner, or content distribution platform.

---

## Design Principles

* **Deterministic Mapping** — Each short code maps to a single destination URL.
* **Low Latency Path** — Redirect resolution must remain independent from analytics processing.
* **Separation of Concerns** — Redirect path must remain isolated from dashboard APIs.
* **Write-Asynchronous Analytics** — Click logging must not delay redirect response.
* **Abuse Resistance** — System must enforce rate limits and link creation constraints.
* **Immutability of Click Events** — Click logs are append-only.

---

## High-Level System Architecture

```
Client Browser
   ↓
Angular SPA
   ↓ (HTTPS REST)
Django API Layer
   ↓
Service Layer
   ↓
PostgreSQL (Primary Data)
Redis (Cache + Queue Broker)
Celery Workers (Async Tasks)
Nginx (Reverse Proxy)
Gunicorn (WSGI)
```

---

# Backend System Components

## 1. API Layer (Django REST Framework)

This layer handles:

* Authentication
* Request validation
* Serialization
* Permission checks
* Rate limiting

No business logic is implemented directly in views.

---

## 2. Service Layer

Contains all application logic.

### Services

| Service          | Responsibility                                   |
| ---------------- | ------------------------------------------------ |
| LinkService      | Short code generation, link creation, validation |
| RedirectService  | Link resolution, expiration check                |
| AnalyticsService | Click event preparation                          |
| SecurityService  | Rate limiting, spam checks                       |
| UserService      | Account operations                               |

---

## 3. Redirect Engine (Performance-Critical)

This is a dedicated Django view with:

* No serializer overhead
* No session handling
* Minimal middleware

Flow:

```
GET /{short_code}
→ Check Redis cache
→ If hit → redirect
→ If miss → DB lookup
→ Cache result
→ Push click event to queue
→ Return HTTP 302
```

This endpoint must avoid heavy processing.

---

## 4. Analytics Pipeline

Click tracking is asynchronous.

### Flow

```
Redirect View
    ↓
Push event → Redis queue
    ↓
Celery Worker
    ↓
GeoIP lookup
Device parsing
Referrer parsing
    ↓
Store Click row
```

Redirect response is returned before analytics completes.

---

## 5. Caching Layer (Redis)

| Cached Item         | Key            | TTL     |
| ------------------- | -------------- | ------- |
| Short code mapping  | `link:{code}`  | 24h     |
| Rate limit counters | `rl:user:{id}` | rolling |
| Anonymous limit     | `rl:ip:{ip}`   | rolling |

---

## 6. Expiration & Maintenance Tasks

Handled by Celery beat.

| Task                  | Purpose                     |
| --------------------- | --------------------------- |
| Expire links job      | Mark expired links inactive |
| Analytics aggregation | Daily stats summary         |
| Cache cleanup         | Remove stale cache entries  |

---

# API Design Specification

All endpoints prefixed with `/api/v1/`

---

## Authentication

Uses JWT.

### POST `/auth/register`

Create account.

**Request**

```
{
  "email": "",
  "password": ""
}
```

---

### POST `/auth/login`

Returns access & refresh tokens.

---

## Link Management

### POST `/links`

Create short link.

**Request**

```
{
  "original_url": "https://...",
  "custom_alias": "optional",
  "expires_at": "optional"
}
```

**Logic**

1. Validate URL format
2. Check rate limits
3. Generate Base62 code
4. Ensure uniqueness
5. Save
6. Cache mapping

---

### GET `/links`

List user links (paginated)

---

### GET `/links/{id}`

Retrieve link details + summary analytics

---

### DELETE `/links/{id}`

Soft delete (disable redirects)

---

## Analytics

### GET `/links/{id}/analytics`

Returns:

* total_clicks
* clicks_by_day
* top_countries
* devices
* referrers

Data is aggregated, not raw.

---

# Data Model

## links

| Field        | Notes           |
| ------------ | --------------- |
| short_code   | indexed, unique |
| original_url | validated       |
| is_active    | allows disable  |
| expires_at   | nullable        |

---

## clicks (append-only)

| Field       | Notes    |
| ----------- | -------- |
| link_id     | FK       |
| timestamp   | indexed  |
| country     | ISO code |
| device_type | enum     |
| referrer    | text     |

---

# Security Controls

| Risk               | Control                  |
| ------------------ | ------------------------ |
| Mass link creation | Rate limiting            |
| Malicious URLs     | Regex + domain blacklist |
| Enumeration        | Random codes             |
| DDoS               | Nginx throttling         |

---

# Frontend Architecture

## Responsibilities

* Token storage
* Form validation
* Data visualization
* Route guarding

No business logic duplication.

---

## Angular Modules

| Module            | Role           |
| ----------------- | -------------- |
| AuthModule        | Login/Register |
| DashboardModule   | Link list      |
| LinkDetailsModule | Analytics      |
| SharedModule      | UI components  |

---

# Performance Constraints

| Path          | Max latency       |
| ------------- | ----------------- |
| Redirect      | <50ms server time |
| Dashboard API | <300ms            |

---

# Deployment Layout

```
Nginx
 ├─ /api → Django
 └─ / → Angular static
```

Workers run separately.

---

# Out of Scope

* Malware scanning
* Private links
* Federated shorteners
* CDN-based redirects

---

This system demonstrates:

* Async architecture
* Read-heavy optimization
* API-first design
* Secure multi-user backend
* Production deployment patterns

---

If you want next level, I can produce:

**1. Exact Django app structure**
**2. Celery task design**
**3. DB indexes strategy**
**4. Redis key schema**
