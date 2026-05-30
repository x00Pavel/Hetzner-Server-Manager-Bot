from collections.abc import Callable, Awaitable
from typing import Any
from eiogram.middleware import BaseMiddleware
from eiogram.types import Update
from src.db import GetDB, User, UserMessage


class Middleware(BaseMiddleware):
    def __init__(self, priority: int = 0):
        super().__init__(priority)

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: dict[str, Any],
    ):
        async with GetDB() as db:
            user = update.origin.from_user
            dbuser = await User.upsert(db, user=user)
            if update.message:
                await UserMessage.add(update.message)
            data["dbuser"] = dbuser
            data["db"] = db
            try:
                return await handler(update, data)
            except Exception as e:
                if e == "Access Denied":
                    return
                raise e
