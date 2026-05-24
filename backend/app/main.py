from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.companies.routes import router as companies_router
from app.api.v1.suppliers.routes import router as suppliers_router
from app.api.v1.rfqs.routes import router as rfqs_router
from app.api.v1.files.routes import router as files_router
from app.api.v1.ai.routes import router as ai_router
from app.api.v1.tenders.routes import router as tenders_router
from app.api.v1.quotes.routes import router as quotes_router
from app.api.v1.landed_costs.routes import router as landed_costs_router
from app.api.v1.orders.routes import router as orders_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.admin.routes import router as admin_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(companies_router, prefix=settings.api_prefix)
    app.include_router(suppliers_router, prefix=settings.api_prefix)
    app.include_router(rfqs_router, prefix=settings.api_prefix)
    app.include_router(files_router, prefix=settings.api_prefix)
    app.include_router(ai_router, prefix=settings.api_prefix)
    app.include_router(tenders_router, prefix=settings.api_prefix)
    app.include_router(quotes_router, prefix=settings.api_prefix)
    app.include_router(landed_costs_router, prefix=settings.api_prefix)
    app.include_router(orders_router, prefix=settings.api_prefix)
    app.include_router(notifications_router, prefix=settings.api_prefix)
    app.include_router(admin_router, prefix=settings.api_prefix)
    return app


app = create_app()
