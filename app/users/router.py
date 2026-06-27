import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.dependencies.security import get_user_service
from app.users.schemas import CreateUser, OutUser, UpdateUser
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=OutUser,
    summary="Create a new User",
    description="Creates a new user record using the provided name and description.",
    status_code=status.HTTP_201_CREATED,
)
async def create_users(user_in: CreateUser, service: Annotated[UserService, Depends(get_user_service)]):
    return service.createUser(user_in)


@router.get(
    "/",
    response_model=list[OutUser],
    description="Retrieves a lightweight list of all tracked users.",
    status_code=status.HTTP_200_OK,
    summary="List all users",
)
async def get_users(
    service: Annotated[UserService, Depends(get_user_service)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of users to return")] = 20,
):
    users = service.listUsers(offset, limit)

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There aren't users on the list")

    return users


@router.get(
    "/{user_id}",
    response_model=OutUser,
    summary="Get user by ID",
    status_code=status.HTTP_200_OK,
    description="This route retrieves the full details of a specific user by its unique identifier.",
)
async def get_user_by_id(
    user_id: Annotated[uuid.UUID, Path(description="The id of the user")],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.patch(
    "/{user_id}",
    response_model=OutUser,
    status_code=status.HTTP_200_OK,
    summary="Partially update an item",
    description="Updates selected fields of an existing item by ID without replacing the entire resource.",
)
async def update_user(
    user_id: Annotated[uuid.UUID, Path(description="The id of the user")],
    user_update: UpdateUser,
    service: Annotated[UserService, Depends(get_user_service)],
):
    updated_user = service.update_data(user_id, user_update)

    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return updated_user


@router.delete(
    "/{user_id}",
    response_model=dict[str, OutUser] | None,
    summary="Delete user by ID",
    status_code=status.HTTP_200_OK,
    description="This route delete an user by its id",
)
async def delete_user(
    user_id: Annotated[uuid.UUID, Path(description="The id of the user")],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = service.deleteUser(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
