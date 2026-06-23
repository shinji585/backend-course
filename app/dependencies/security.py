from app.core.security import password_helper
from app.users.service import UserService


def get_password_helper() -> UserService:
    return UserService(password_helper=password_helper)
