from typing import List
from typing import Optional
from typing import Type

from telegram_bot.constants import AdminConsts
from telegram_bot.models import AdminUserId
from telegram_bot.models import PersonInformation
from telegram_bot.models import Story
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save


@post_save(Story)
async def story_post_save(
        sender: Type[Story], instance: Story, created: bool,
        using_db: Optional[BaseDBAsyncClient], update_fields: List[str]
) -> None:
    """Отправляем всем админам оповещение о создании новой истории у бота."""

    from telegram_bot.bot import bot

    admins_user_ids = await AdminUserId.exclude(user_id=instance.user_id)
    for admin_user in admins_user_ids:
        await bot.send_message(admin_user.user_id, AdminConsts.NEW_STORY_MSG)


@post_save(PersonInformation)
async def person_info_post_save(
        sender: Type[PersonInformation], instance: PersonInformation,
        created: bool, using_db: Optional[BaseDBAsyncClient],
        update_fields: List[str],
) -> None:
    """Отправляем всем админам оповещение о создании новой анкеты у бота."""

    from telegram_bot.bot import bot

    admins_user_ids = await AdminUserId.exclude(user_id=instance.user_id)
    for admin_user in admins_user_ids:
        await bot.send_message(
            admin_user.user_id, AdminConsts.NEW_PERSON_INFO_MSG)
