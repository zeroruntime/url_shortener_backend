# PopOff - URL Shortener Backend
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/zeroruntime/url_shortener_backend)

PopOff is a robust and scalable URL shortener backend built with Django and Django REST Framework. It provides a comprehensive API for creating, managing, and tracking shortened URLs with detailed analytics.

I chose this project to help me practice and get more familiar with Django REST Framework

AI was used in generating the Markdown files such as this README, the API_Guide and the Architecture markdown, It was used to go over the workspace to locate and help me fix critical bugs 

## Core Features

-   **JWT Authentication**: Secure user registration and login using JSON Web Tokens.
-   **Link Management**: Full CRUD functionality for creating, listing, retrieving, and deleting short links.
-   **Custom Aliases**: Users can define their own custom short codes for branded links.
-   **Link Expiration**: Set an expiration date and time for temporary links.
-   **Click Analytics**: Tracks each click and records metadata like country, device type, referrer, and IP address.
-   **Rate Limiting**: Built-in protection against abuse with request throttling on critical endpoints.
-   **Interactive API Docs**: Explore and test the API in real-time with the integrated Swagger UI.

## Technology Stack

-   **Backend**: Django, Django REST Framework
-   **Authentication**: djangorestframework-simplejwt (JWT)
-   **Database**: Supports PostgreSQL (production) and SQLite (development)
-   **API Documentation**: drf-spectacular (Swagger/OpenAPI)

## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

-   Python 3.x
-   `pip` and `venv`

### 1. Clone the Repository

```bash
git clone https://github.com/zeroruntime/url_shortener_backend.git
cd url_shortener_backend
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install Django==5.0 djangorestframework djangorestframework-simplejwt dj-database-url psycopg2-binary python-dotenv drf-spectacular
```

### 4. Configure the Database

The project defaults to SQLite for local development, which requires no configuration.

To use PostgreSQL, create a `.env` file in the project root and add your database connection string:

```
# .env file
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
```

### 5. Apply Migrations

Run the following command to set up the database schema:

```bash
python manage.py migrate
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the server is running, you can access the interactive Swagger UI for complete API documentation, request/response examples, and endpoint testing.

-   **Swagger UI**: **http://127.0.0.1:8000/api/docs/**

You can use the Swagger interface to register a user, obtain a JWT token, and test all protected endpoints directly in your browser.

## API Endpoints

All endpoints are prefixed with `/api/v1/`.

### Authentication

| Method | Endpoint                    | Description                       |
| :----- | :-------------------------- | :-------------------------------- |
| `POST` | `/auth/register/`           | Create a new user account.        |
| `POST` | `/auth/token/`              | Log in and receive JWT tokens.    |
| `POST` | `/auth/token/refresh/`      | Obtain a new access token.        |
| `POST` | `/auth/logout/`             | Blacklist a refresh token to log out. |

### Link Management

*All link management endpoints require `Authorization: Bearer <YOUR_ACCESS_TOKEN>` header.*

| Method   | Endpoint                  | Description                               |
| :------- | :------------------------ | :---------------------------------------- |
| `POST`   | `/urls/shorten/`          | Create a new short link.                  |
| `GET`    | `/urls/getall/`           | List all of your links (paginated).       |
| `GET`    | `/urls/<int:pk>/`         | Retrieve details for a specific link.     |
| `DELETE` | `/urls/delete/<int:pk>/`  | Delete a specific link.                   |
| `GET`    | `/urls/<int:pk>/analytics/` | Get click analytics for a specific link.  |
| `GET`    | `/<short_code>/`          | Redirect to the original URL.             |

### Example: Creating a Short Link

```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "original_url": "https://github.com/zeroruntime/url_shortener_backend",
    "custom_alias": "my-repo"
  }'
```

**Response:**

```json
{
  "shortUrl": "my-repo",
  "customAlias": "my-repo",
  "longUrl": "https://github.com/zeroruntime/url_shortener_backend"
}
```

Now, navigating to `http://localhost:8000/my-repo/` will redirect you to the original URL.
