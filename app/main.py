from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()


@app.get("/shipment")
async def get_shipment() -> dict: 
    return {
        "product_name": "Portatil Asus Vivobook",
        "status": "in order to be send"
    }
    
@app.get("/scalar", include_in_schema=False)
async def get_scalar_doct() -> HTMLResponse: 
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
    
@app.post("/shipment/buy")
async def post_shipment(name: str) -> dict: 
    return {
        "product_name": name,
        "status": "product added to leave soon"
    }