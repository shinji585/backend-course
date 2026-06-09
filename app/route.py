import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.create import CreateItem
from app.schemas.detail import DetailItem
from app.schemas.out import OutItem
from app.schemas.update import UpdateItem
from app.service import ItemController

router = APIRouter(prefix="/items", tags=["items"])


@router.post(
    "/items/",
    response_model=OutItem,
    summary="Create a new Item",
    description="Creates a new item record using the provided name and description.",
    status_code=status.HTTP_201_CREATED,
)
async def create_item(item_in: CreateItem, controller: Annotated[ItemController, Depends()]):
    return controller.createItem(item_in)


@router.get(
    "/items/",
    response_model=list[OutItem],
    description="Retrieves a lightweight list of all tracked items.",
    status_code=status.HTTP_200_OK,
    summary="List all items",
)
async def list_items(controller: Annotated[ItemController, Depends()]):
    items = controller.listItems()

    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There aren't items on the list")

    return items


@router.get(
    "/items/{item_id}",
    response_model=DetailItem,
    summary="Get item by ID",
    status_code=status.HTTP_200_OK,
    description="This route retrieves the full details of a specific item by its unique identifier.",
)
async def get_item(item_id: uuid.UUID, controller: Annotated[ItemController, Depends()]):
    item = controller.getItemDetail(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


@router.delete(
    "/items/{item_id}",
    response_model=dict[str, DetailItem] | None,
    summary="Delete item by ID",
    status_code=status.HTTP_200_OK,
    description="This route delete an item by its id",
)
async def delete_item(item_id: uuid.UUID, controller: Annotated[ItemController, Depends()]):
    item = controller.deleteItem(item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.patch(
    "/items/{item_id}",
    response_model=DetailItem,
    status_code=status.HTTP_200_OK,
    summary="Partially update an item",
    description="This route allows modifying specific fields of an existing item by its ID without overwriting the entire resource.",
)
async def update_item(item_id: uuid.UUID, item_update: UpdateItem, controller: Annotated[ItemController, Depends()]):
    updated_item = controller.updateItem(item_id, item_update)

    if updated_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated_item
