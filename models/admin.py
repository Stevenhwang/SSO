from tortoise import Model, fields
from models.base import TimestampMixin, BaseModel


class User(BaseModel, TimestampMixin):
    address = fields.CharField(128, null=True)

    class Meta:
        table = "user"
