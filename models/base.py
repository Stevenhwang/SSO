from tortoise import fields
from tortoise.models import Model
from tortoise.query_utils import Q
import ciso8601
from models.patch import NewDateTimeField


class TimestampMixin:
    created_at = NewDateTimeField(auto_now_add=True)
    updated_at = NewDateTimeField(auto_now=True)


class BaseModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(128, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def to_dict(self, only=None, exclude=None):
        if only:
            fs = only
        elif exclude:
            fs = [f for f in self._meta.fields if f not in exclude]
        else:
            fs = self._meta.fields

        data = {}
        for f in fs:
            if isinstance(self._meta.fields_map[f], fields.DatetimeField):
                data.update({f: str(getattr(self, f))})
            else:
                data.update({f: getattr(self, f)})
        return data

    @classmethod
    async def search(cls, attributes=None, **query):
        fs_map = cls._meta.fields_map
        search = query.get('search')
        page = int(query.pop('page')) if query.get('page') else 1
        limit = int(query.pop('limit')) if query.get('limit') else 15
        order_by = query.pop('order_by') if query.get('order_by') else 'id'
        if not attributes:
            attributes = [a for a in fs_map.keys() if isinstance(fs_map[a], fields.CharField)]
        for k, v in query.items():
            if isinstance(fs_map.get(k.split('__')[0]), fields.DatetimeField):
                query[k] = ciso8601.parse_datetime(v)
        if search:
            query.pop('search')
            if isinstance(search, list):
                attr_dict_list = [{a + '__in': search} for a in attributes]
            else:
                attr_dict_list = [{a + '__icontains': search} for a in attributes]
            q_list = [Q(**a) for a in attr_dict_list]
            return await cls.filter(Q(*q_list, join_type="OR")).filter(**query) \
                .limit(limit).offset((page - 1) * limit).order_by(order_by)
        else:
            return await cls.filter(**query).limit(limit).offset((page - 1) * limit) \
                .order_by(order_by)
