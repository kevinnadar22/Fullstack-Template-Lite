# Backend Documentation

This directory contains the FastAPI backend for the application.

## 📂 Project Structure

The project follows a layered architecture to ensure separation of concerns:

```
backend/
├── app/
│   ├── api/            # API Endpoints & Routes
│   │   ├── v1/         # Versioned API controllers
│   │   └── router.py   # Main router configuration
│   ├── core/           # Core configuration
│   │   ├── config.py   # Environment variables & settings
│   │   └── security.py # Auth utilities (JWT, etc.)
│   ├── domain/         # Data Models
│   │   ├── models/     # SQLAlchemy Database Models
│   │   └── schemas/    # Pydantic Schemas (Request/Response)
│   ├── repository/     # Database Access Layer (CRUD)
│   ├── service/        # Business Logic Layer
│   ├── db.py           # Database connection & session
│   └── __main__.py     # App entry point
├── alembic/            # Database Migrations
└── tests/              # Test suite
```

## 🚀 Key Concepts

- **Domain Driven:** We separate data models (`domain/models`) from data transfer objects (`domain/schemas`).
- **Repository Pattern:** Database queries live in `repository/`. Do not write SQL/ORM queries directly in endpoints.
- **Service Layer:** Complex business logic lives in `service/`. Endpoints should be thin and delegate to services.
- **Dependencies:** Uses FastAPI's dependency injection for DB sessions and current user.

## ⚙️ Configuration Guide (`app/core/config.py`)

The application uses `pydantic-settings` to manage environment variables. You can define these in a `.env` file (see `.sample.env`).

### Environment & Database
| Variable | Description | Default |
| :--- | :--- | :--- |
| `ENV` | Environment mode (`dev` or `prod`). | `dev` |
| `DATABASE_URL` | Connection string for the database (PostgreSQL/SQLite). | `sqlite:///./instance/test.db` |
| `FRONTEND_URL` | URL of the frontend application (for CORS). | **Required** |
| `LOGFIRE_TOKEN` | Token for Logfire observability. | `None` |
| `TZ` | Timezone for the application. | `UTC` |

### Authentication & Security
| Variable | Description | Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Secret key for JWT encoding. **Change this!** | `your-secret` |
| `REFRESH_SECRET_KEY` | Secret key for Refresh Token encoding. **Change this!** | `your-refresh-secret` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | API Access Token lifetime in minutes. | `10` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh Token lifetime in minutes. | `10080` (7 days) |
| `ALGORITHM` | Hashing algorithm for JWT. | `HS256` |

### Feature Flags
| Variable | Description | Default |
| :--- | :--- | :--- |
| `ENABLE_LOGIN_OTP` | Enable OTP verification for login. | `False` |
| `ENABLE_SIGNUP_OTP` | Enable OTP verification for signup. | `False` |
| `ENABLE_GOOGLE_AUTH` | Enable Google OAuth login. | `False` |

### Third-Party Services
**Google OAuth** (Required if `ENABLE_GOOGLE_AUTH=True`):
- `GOOGLE_CLIENT_ID`: OAuth Client ID from Google Cloud Console.
- `GOOGLE_CLIENT_SECRET`: OAuth Client Secret.
- `GOOGLE_REDIRECT_URL`: Callback URL for Google Auth.

**Email / Brevo** (Required if OTP is enabled):
- `BREVO_API_KEY`: API Key for Brevo email service.
- `MAIL_FROM_EMAIL`: Sender email address.
- `MAIL_FROM_NAME`: Sender name.

**Celery / RabbitMQ**:
- `RABBITMQ_URL`: Connection string for RabbitMQ. If set, async task processing is enabled.

### Admin Defaults
- `ADMIN_USERNAME`: Default username for SQLAdmin (Default: `admin`).
- `ADMIN_PASSWORD`: Default password for SQLAdmin (Default: `123`).

---

## 🛠️ How to Add a New Feature

Follow this workflow to add a new entity (e.g., `Product`):

1.  **Define the Model:**
    Create `app/domain/models/product.py`. Define your SQLAlchemy model here.

2.  **Define the Schemas:**
    Create `app/domain/schemas/product.py`. Define Pydantic models for:
    - `ProductCreate` (input)
    - `ProductUpdate` (input)
    - `ProductResponse` (output)

3.  **Create Repository:**
    Create `app/repository/product.py`. Implement CRUD operations using the session.
    ```python
    class ProductRepository(BaseRepository[Product]):
        ...
    ```

4.  **Create Service:**
    Create `app/service/product.py`. helper methods or complex logic that uses the repository.

5.  **Create API Endpoint:**
    Create `app/api/v1/product.py`. Define routes (`GET`, `POST`, etc.) using FastAPI.
    - Inject dependencies (Session, User).
    - Call the Service/Repository.
    - Return the Pydantic schema.

6.  **Register Router:**
    Add your new router to `app/api/router.py` or inside `app/api/v1/__init__.py`.

7.  **Migration:**
    Run `alembic revision --autogenerate -m "add product table"` and then `alembic upgrade head`.

## ⚙️ Setup & Running

1.  **Environment:**
    Copy `.sample.env` to `.env` and fill in the values (DB connection, usage secrets).

2.  **Run Locally:**
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Run server (hot reload)
    python run.py --reload
    ```
    
3.  **Docs:**
    Visit `http://localhost:8000/docs` for Swagger UI.
