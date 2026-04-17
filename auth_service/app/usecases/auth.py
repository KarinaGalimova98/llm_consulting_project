from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def register(self, email: str, password: str):
        existing = await self.users_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        password_hash = hash_password(password)
        user = await self.users_repo.create(email=email, password_hash=password_hash)
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.users_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        return create_access_token(sub=str(user.id), role=user.role)

    async def me(self, user_id: int):
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user