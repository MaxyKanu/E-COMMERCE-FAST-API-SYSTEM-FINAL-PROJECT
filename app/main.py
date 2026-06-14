"""
E-Commerce Inventory API - Main Application
SDG 8: Decent Work and Economic Growth
Empowering Sierra Leone SMEs with digital inventory management

FastAPI application with:
- Swagger UI (/docs) - Interactive API testing
- ReDoc (/redoc) - Beautiful responsive documentation
- OpenAPI Schema (/openapi.json) - Raw schema for imports
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from app.config import settings
from app.routers import auth, products, categories, users, orders, reviews


# =====================================================================
# LIFESPAN CONTEXT MANAGER (Modern - replaces deprecated on_event)
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    STARTUP: Code before 'yield' runs when server starts
    SHUTDOWN: Code after 'yield' runs when server stops
    """
    # ========== STARTUP ==========
    print("=" * 60)
    print("🚀 E-Commerce Inventory API Running!")
    print(f"📚 Swagger UI:  http://localhost:8000/docs")
    print(f"📖 ReDoc:        http://localhost:8000/redoc")
    print(f"🔧 OpenAPI:      http://localhost:8000/openapi.json")
    print(f"🌍 SDG 8 - Sierra Leone SME Support")
    print(f"💡 Version:      {settings.APP_VERSION}")
    print("=" * 60)
    
    yield  # Application runs while yielding
    
    # ========== SHUTDOWN ==========
    print("\n" + "=" * 60)
    print("🛑 E-Commerce Inventory API Shutting Down...")
    print("=" * 60)


# =====================================================================
# CREATE FASTAPI APPLICATION
# =====================================================================
app = FastAPI(
    title="E-Commerce Inventory API",
    description=(
        "**SDG 8 - Decent Work and Economic Growth**\n\n"
        "A digital inventory management API designed for "
        "Sierra Leone small businesses.\n\n"
        "## Features:\n"
        "- 📦 Product & inventory management with real-time stock tracking\n"
        "- 📋 Order processing with automatic stock validation & deduction\n"
        "- 👥 User management with role-based access (Admin/Customer)\n"
        "- ⭐ Product reviews and ratings (1-5 stars)\n"
        "- 🔐 JWT authentication with OAuth2 & bcrypt password hashing\n"
        "- 📧 Async email notifications on order confirmation\n\n"
        "## Target Users:\n"
        "Small and medium enterprises in Sierra Leone "
        "transitioning from paper-based inventory systems.\n\n"
        "## Documentation Links:\n"
        "- **Swagger UI** (`/docs`): Interactive API testing - Try endpoints directly\n"
        "- **ReDoc** (`/redoc`): Beautiful responsive documentation - Great for sharing"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=None,       # Custom Swagger UI endpoint
    redoc_url=None,      # Custom ReDoc endpoint
    openapi_url="/openapi.json",  # OpenAPI schema for both docs
    contact={
        "name": "E-Commerce Inventory API Support",
        "url": "https://github.com/MaxyKanu/E-COMMERCE-FAST-API-SYSTEM-FINAL-PROJECT",
    },
    license_info={
        "name": "MIT License - Free for Sierra Leone businesses",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# =====================================================================
# CORS MIDDLEWARE - Allows access from any device
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins for mobile/website access
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)

# =====================================================================
# STATIC FILES SETUP (For offline ReDoc support)
# =====================================================================
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files directory for local assets
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =====================================================================
# SWAGGER UI ENDPOINT - Interactive API Testing
# =====================================================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Swagger UI - Interactive API documentation
    
    Try out all endpoints directly in your browser:
    - Register users
    - Login to get JWT tokens
    - Browse products
    - Place orders
    - Manage inventory (admin)
    
    Perfect for developers testing the API.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# =====================================================================
# REDOC ENDPOINT - Beautiful Responsive Documentation
# =====================================================================
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    ReDoc - Beautiful, responsive, searchable API documentation
    
    FIXED: Uses official Redocly CDN (not broken jsdelivr @next)
    FALLBACK: Uses local file if downloaded to app/static/
    
    Features:
    - Mobile-friendly responsive design
    - Powerful search with highlighting
    - Clean, modern layout
    - Download OpenAPI spec
    - Perfect for sharing with stakeholders
    
    Best viewed in Chrome, Firefox, or Edge InPrivate mode.
    """
    
    # Check if local ReDoc file exists (for offline use)
    local_redoc = os.path.join(static_dir, "redoc.standalone.js")
    
    if os.path.exists(local_redoc):
        # Use locally hosted file (works completely offline)
        redoc_js = "/static/redoc.standalone.js"
        print("📖 ReDoc: Using LOCAL file (offline mode)")
    else:
        # FIX: Use official Redocly CDN instead of broken jsdelivr @next
        redoc_js = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
        print("📖 ReDoc: Using Redocly CDN (online mode)")
    
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc Documentation",
        redoc_js_url=redoc_js,
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


# =====================================================================
# ROOT ENDPOINT - SDG 8 Mission Statement
# =====================================================================
@app.get(
    "/",
    tags=["Root"],
    summary="API Root - SDG 8 Mission",
    description="Returns the API mission and SDG 8 alignment statement."
)
def root():
    """
    Root endpoint with SDG 8 mission statement
    
    Returns:
    - API name and version
    - SDG 8 alignment
    - Sierra Leone problem statement
    - Solution and impact description
    - Links to all documentation
    """
    return {
        "message": "E-Commerce Inventory API",
        "version": "1.0.0",
        "sdg": "SDG 8 - Decent Work and Economic Growth",
        "problem": "70% of Sierra Leone small businesses use paper-based inventory systems",
        "solution": "Free digital inventory API accessible from any device",
        "impact": "Reducing stock losses and improving order tracking for Sierra Leone SMEs",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }


# =====================================================================
# HEALTH CHECK ENDPOINT
# =====================================================================
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and all services are healthy."
)
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns 200 OK if API is running properly.
    Useful for uptime monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "api": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# =====================================================================
# INCLUDE ALL ROUTERS
# =====================================================================
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(reviews.router)