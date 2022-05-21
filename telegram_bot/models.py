from tortoise import fields
from tortoise.models import Model


class TimedBaseModel(Model):
    class Meta:
        abstract = True

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


# class User(Model):
#     nickname = fields.CharField(max_length=50, null=False)
