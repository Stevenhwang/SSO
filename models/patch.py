from tortoise.fields import DatetimeField
from typing import Optional
from datetime import datetime


class NewDateTimeField(DatetimeField):
    def to_db_value(
            self, value: Optional[datetime], instance
    ) -> Optional[datetime]:
        if hasattr(instance, "_saved_in_db"):
            if self.auto_now or (
                    self.auto_now_add and getattr(instance, self.model_field_name) is None
            ):
                value = datetime.now()
                setattr(instance, self.model_field_name, value)
                return value
        return value
