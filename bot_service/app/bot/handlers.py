from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Сначала отправь JWT командой:\n"
        "/token <your_jwt>\n\n"
        "Потом можешь писать обычные сообщения."
    )


@router.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1) if message.text else []
    if len(parts) < 2:
        await message.answer("Использование: /token <jwt>")
        return

    token = parts[1].strip()

    try:
        decode_and_validate(token)
    except ValueError as exc:
        await message.answer(f"Токен невалиден: {str(exc)}")
        return

    redis = get_redis()
    key = f"token:{message.from_user.id}"
    await redis.set(key, token)

    await message.answer("Токен сохранён. Теперь можешь отправить вопрос.")


@router.message(F.text)
async def handle_text(message: Message):
    redis = get_redis()
    key = f"token:{message.from_user.id}"
    token = await redis.get(key)

    if not token:
        await message.answer(
            "JWT не найден. Сначала авторизуйся через Auth Service и отправь:\n"
            "/token <jwt>"
        )
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer(
            "JWT невалиден или истёк. Получи новый токен в Auth Service и отправь снова:\n"
            "/token <jwt>"
        )
        return

    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят в обработку. Жди ответ.")