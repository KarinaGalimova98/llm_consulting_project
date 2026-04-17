import pytest
from jose import jwt

from app.bot.handlers import cmd_token, handle_text
from app.core.config import settings


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class FakeChat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class FakeMessage:
    def __init__(self, text: str, user_id: int = 123, chat_id: int = 456):
        self.text = text
        self.from_user = FakeUser(user_id)
        self.chat = FakeChat(chat_id)
        self.answers = []

    async def answer(self, text: str):
        self.answers.append(text)


@pytest.mark.asyncio
async def test_token_command_saves_token(fake_redis):
    token = jwt.encode(
        {"sub": "1", "role": "user", "exp": 9999999999},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )
    message = FakeMessage(f"/token {token}")

    await cmd_token(message)

    saved = await fake_redis.get("token:123")
    assert saved == token
    assert "Токен сохранён" in message.answers[-1]


@pytest.mark.asyncio
async def test_handle_text_without_token(fake_redis, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    message = FakeMessage("Привет")

    await handle_text(message)

    delay_mock.assert_not_called()
    assert "JWT не найден" in message.answers[-1]


@pytest.mark.asyncio
async def test_handle_text_with_token_calls_celery(fake_redis, mocker):
    token = jwt.encode(
        {"sub": "1", "role": "user", "exp": 9999999999},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )
    await fake_redis.set("token:123", token)

    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")
    message = FakeMessage("Расскажи про Python")

    await handle_text(message)

    delay_mock.assert_called_once_with(456, "Расскажи про Python")
    assert "Запрос принят" in message.answers[-1]