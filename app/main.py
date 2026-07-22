from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

from app.db.database import init_db
from app.routers import trackedProductRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="TrackBuy API",
    description="""
A REST API for managing tracked products.

Users can create tracked products with specific criteria such as target price,
condition, color, and other preferences. The API is designed to support
future integrations with online marketplaces (e.g., Amazon and Mercado Libre)
to monitor product availability and pricing.
""",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router=trackedProductRouter.router)


@app.get("/")
async def root():
    return {"name": "TrackBuy API", "version": "0.1.0"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html() -> HTMLResponse:
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Tracked product Documentation Scalar")
