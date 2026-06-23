import uuid

from fastapi_users.password import PasswordHelper

from app.users.schemas.create import CreateUser
from app.users.schemas.detail import DetailUser
from app.users.schemas.out import OutUser
from app.users.schemas.update import UpdateUser


class UserService:
    repository: list[DetailUser] = []

    def __init__(self, password_helper: PasswordHelper) -> None:
        self.password_helper = password_helper

    def createUser(
        self,
        userCreate: CreateUser,
    ) -> OutUser:
        hashed_password = self.password_helper.hash(userCreate.password)

        user_data = userCreate.model_dump()
        user_data["hashed_password"] = hashed_password
        user_data.pop("password", None)
        detail_user = DetailUser.model_validate(user_data)
        self.repository.append(detail_user)

        return OutUser.model_validate(detail_user)

    def update_data(self, id: uuid.UUID, user_update: UpdateUser) -> OutUser | None:
        for user in self.repository:
            if user.id == id:
                update_data_user = user_update.model_dump(exclude_unset=True)

                for field, value in update_data_user.items():
                    setattr(user, field, value)
            return OutUser.model_validate(user)
        return None

    def get_user_by_id(self, id: uuid.UUID) -> OutUser | None:
        for user in self.repository:
            if user.id == id:
                return OutUser.model_validate(user)
        return None

    def listUsers(self) -> list[OutUser]:
        return [OutUser.model_validate(x) for x in self.repository]
