from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vazi"

    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # Paystack
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PLAN_CODE: str = ""
    PAYSTACK_WEBHOOK_SECRET: str = ""

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Vazi <alerts@vazi.io>"

    # AI Providers
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""
    SERP_API_KEY: str = ""

    # App
    API_URL: str = "http://localhost:8000"
    DASHBOARD_URL: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
