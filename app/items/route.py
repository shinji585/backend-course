import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.items.schemas import CreateItem, OutItem, UpdateItem
from app.items.service import ItemServices

router = APIRouter(prefix="/items", tags=["items"])


@router.post(
    "/",
    response_model=OutItem,
    summary="Create a new Item",
    description="Creates a new item record using the provided name and description.",
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item_in: CreateItem, service: Annotated[ItemServices, Depends()]):
    return service.createItem(item_in)


@router.get(
    "/",
    response_model=list[OutItem],
    description="Retrieves a lightweight list of all tracked items.",
    status_code=status.HTTP_200_OK,
    summary="List all items",
)
async def list_items(
    service: Annotated[ItemServices, Depends()],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of items to return")] = 20,
):
    items = service.listItems(offset, limit)

    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There aren't items on the list")

    return items


@router.get(
    "/{item_id}",
    response_model=OutItem,
    summary="Get item by ID",
    status_code=status.HTTP_200_OK,
    description="This route retrieves the full details of a specific item by its unique identifier.",
)
async def get_item(
    item_id: Annotated[uuid.UUID, Path(description="ID of the item")],
    service: Annotated[ItemServices, Depends()],
):
    item = service.getItemDetail(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


@router.delete(
    "/{item_id}",
    response_model=dict[str, OutItem] | None,
    summary="Delete item by ID",
    status_code=status.HTTP_200_OK,
    description="This route delete an item by its id",
)
async def delete_item(
    item_id: Annotated[uuid.UUID, Path(description="ID of the item")],
    service: Annotated[ItemServices, Depends()],
):
    item = service.deleteItem(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.patch(
    "/{item_id}",
    response_model=OutItem,
    status_code=status.HTTP_200_OK,
    summary="Partially update an item",
    description="Updates selected fields of an existing item by ID without replacing the entire resource.",
)
async def update_item(
    item_id: Annotated[uuid.UUID, Path(description="ID of the item")],
    item_update: UpdateItem,
    service: Annotated[ItemServices, Depends()],
):
    updated_item = service.updateItem(item_id, item_update)

    if updated_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated_item
