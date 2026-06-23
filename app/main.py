from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.items import items_router
from app.users import users_router

app = FastAPI()

routers = [items_router, users_router]


for router in routers:
    app.include_router(router=router)


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI with Scalar!"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="BuyPlanner Documentation Scalar")
