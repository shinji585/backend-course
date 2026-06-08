from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.route import router

app = FastAPI()

app.include_router(router)


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI with Scalar!"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="BuyPlanner Documentation Scalar")
