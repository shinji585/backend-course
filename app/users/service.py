import uuid

from fastapi_users.password import PasswordHelper

from app.users.schemas import CreateUser, DetailUser, OutUser, UpdateUser


class UserService:
    repository: list[DetailUser] = []

    def __init__(self, password_helper: PasswordHelper) -> None:
        self.password_helper = password_helper

    def createUser(
        self,
        userCreate: CreateUser,
    ) -> OutUser:
        hashed_password = self.password_helper.hash(userCreate.password)

        user_data = userCreate.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        detail_user = DetailUser.model_validate(user_data)
        self.repository.append(detail_user)

        return OutUser.model_validate(detail_user)

    def update_data(self, id: uuid.UUID, user_update: UpdateUser) -> DetailUser | None:
        for user in self.repository:
            if user.id == id:
                assert user_update.password is not None
                hashed_password = self.password_helper.hash(user_update.password)
                update_data_user = user_update.model_dump(exclude_unset=True, exclude={"password"})
                update_data_user["hashed_password"] = hashed_password

                for field, value in update_data_user.items():
                    setattr(user, field, value)

            return DetailUser.model_validate(user)
        return None

    def get_user_by_id(self, id: uuid.UUID) -> OutUser | None:
        for user in self.repository:
            if user.id == id:
                return OutUser.model_validate(user)
        return None

    def listUsers(self) -> list[OutUser]:
        return [OutUser.model_validate(x) for x in self.repository]

    def deleteUser(self, user_id: uuid.UUID) -> dict[str, DetailUser] | None:
        for i, user in enumerate(self.repository):
            if user.id == user_id:
                user_eliminated = self.repository.pop(i)
                return {"User success eliminated": DetailUser.model_validate(user_eliminated)}
        return None
