import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.deps import get_tracked_product_services
from app.schemas.tracked.create import TrackedProductCreate
from app.schemas.tracked.public import TrackedProductPublic
from app.schemas.tracked.update import TrackedProductUpdate
from app.services.trackedProduct import TrackedProductServices

router = APIRouter(prefix="/trackedProducts", tags=["trackedProducts"])


@router.post(
    "/",
    response_model=TrackedProductPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tracked product",
    description=(
        "Creates a new tracked product using the provided tracking criteria. "
        "The service validates the input, creates or associates any referenced tags, "
        "stores the tracked product, and returns the newly created public representation.\n\n"
        "Returns:\n"
        "- 201 if the tracked product is created successfully.\n"
        "- 400 if the tracked product cannot be created.\n"
        "- 500 if an unexpected server error occurs."
    ),
)
def create(
    payload: TrackedProductCreate, service: Annotated[TrackedProductServices, Depends(get_tracked_product_services)]
) -> TrackedProductPublic:
    result: TrackedProductPublic | None | Literal[False] = service.create(tracked_product=payload)

    if result is False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create tracked product")

    return result


@router.get(
    "/{tracked_product_id}",
    response_model=TrackedProductPublic,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a tracked product by ID",
    description=(
        "Retrieves a single tracked product by its unique identifier. "
        "Returns the public representation of the tracked product, including its "
        "associated tags.\n\n"
        "Returns:\n"
        "- 200 if the tracked product exists.\n"
        "- 404 if no tracked product with the specified ID is found."
    ),
)
def get(
    tracked_product_id: uuid.UUID, service: Annotated[TrackedProductServices, Depends(get_tracked_product_services)]
) -> TrackedProductPublic:
    result: TrackedProductPublic | None = service.get(tracked_product_id=tracked_product_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
    return result


@router.get(
    "/",
    response_model=list[TrackedProductPublic],
    status_code=status.HTTP_200_OK,
    summary="List tracked products",
    description=(
        "Returns a paginated list of tracked products. "
        "Use the 'limit' parameter to control the maximum number of returned items and "
        "'offset' to skip a number of results when browsing large collections.\n\n"
        "Pagination:\n"
        "- limit: Maximum number of products to return (default: 20, max: 100).\n"
        "- offset: Number of products to skip before returning results."
    ),
)
def get_all(
    services: Annotated[TrackedProductServices, Depends(get_tracked_product_services)],
    limit: int = Query(default=20, le=100, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
) -> list[TrackedProductPublic]:
    return services.get_all(limit=limit, offset=offset)


@router.patch(
    "/{tracked_product_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a tracked product",
    description=(
        "Updates one or more fields of an existing tracked product. "
        "Only the fields provided in the request body are modified. Fields omitted from "
        "the request remain unchanged.\n\n"
        "Returns:\n"
        "- 200 if the update succeeds.\n"
        "- 404 if the tracked product does not exist."
    ),
)
def update(
    tracked_product_id: uuid.UUID,
    payload: TrackedProductUpdate,
    service: Annotated[TrackedProductServices, Depends(get_tracked_product_services)],
) -> dict[str, Any]:
    result: bool = service.update(
        tracked_product_id=tracked_product_id, **payload.model_dump(exclude_unset=True, mode="json")
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")

    return {"message": "Tracked product updated successfully", "updated": result}


@router.delete(
    "/{tracked_product_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete a tracked product",
    description=(
        "Deletes the tracked product identified by the specified ID.\n\n"
        "Returns:\n"
        "- 200 if the tracked product is successfully removed.\n"
        "- 404 if the tracked product does not exist."
    ),
)
def delete(
    tracked_product_id: uuid.UUID, service: Annotated[TrackedProductServices, Depends(get_tracked_product_services)]
) -> dict[str, Any]:
    result: bool = service.remove(tracked_product_id=tracked_product_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")

    return {"message": "Tracked product removed successfully", "removed": result}
