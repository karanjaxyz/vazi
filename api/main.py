from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services.firebase import init_firebase
from services.paystack import init_paystack
from services.email import init_email
from api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Init services
    init_firebase(settings.FIREBASE_CREDENTIALS_PATH)
    init_paystack(settings.PAYSTACK_SECRET_KEY)
    init_email(settings.RESEND_API_KEY, settings.EMAIL_FROM)
    yield


app = FastAPI(
    title="Vazi API",
    description="AI Visibility Tracking",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow dashboard to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.DASHBOARD_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
