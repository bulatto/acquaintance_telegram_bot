from tortoise import fields
from tortoise.models import Model
from telegram_bot.constants import MAX_TELEGRAM_MESSAGE_LENGTH


class CreatedDateModel(Model):
    """Модель для хранения даты и времени создания объекта."""
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedDateModel(Model):
    """Модель для хранения даты и времени обновления объекта."""
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class DateAwareModel(CreatedDateModel, UpdatedDateModel):
    """Модель для хранения даты и времени создания и обновления объекта."""
    class Meta:
        abstract = True


class Story(CreatedDateModel):
    """Модель для хранения историй"""

    id = fields.IntField(pk=True)
    text = fields.CharField(max_length=MAX_TELEGRAM_MESSAGE_LENGTH)
    # Опубликована ли история
    is_published = fields.BooleanField(default=False)
    # Пользователь отправивший историю
    user_id = fields.BigIntField()


class StoryView(CreatedDateModel):
    """Модель для хранения просмотров историй"""
    id = fields.IntField(pk=True)
    story = fields.ForeignKeyField(
        'models.Story', related_name='story_views')
    # Никнейм телеграм человека, который получил историю
    telegram_nickname = fields.CharField(max_length=100)


class PersonInformation(DateAwareModel):
    """Модель для хранения анкеты"""

    id = fields.IntField(pk=True)
    text = fields.CharField(max_length=MAX_TELEGRAM_MESSAGE_LENGTH)
    # id изображения в системе телеграма (нужно, чтобы быстрее пересылать файл,
    # потому что не надо загружать его на сервера Telegram - он уже там)
    image_file_id = fields.CharField(default='', max_length=200)
    # Опубликована ли анкета
    is_published = fields.BooleanField(default=False)
    # Пользователь отправивший анкету
    user_id = fields.BigIntField()


class AdminUserId(DateAwareModel):
    """
    Модель для хранения связи админских логинов и его user_id, для возможности
    отправки админам сообщений.
    """
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=32)
    user_id = fields.BigIntField()


class AnonymousDialog(DateAwareModel):
    """Модель для хранения пользователей, ищущих диалог в анонимном чате."""
    user_id = fields.BigIntField()
    to_user_id = fields.BigIntField(null=True)


class ClickStats(CreatedDateModel):
    """Модель для хранения статистики нажатий на кнопки бота."""
    user_id = fields.BigIntField()
    button = fields.IntField()
