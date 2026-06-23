from app.core.security import password_helper
from app.users.service import UserService


def get_user_service() -> UserService:
    return UserService(password_helper=password_helper)
