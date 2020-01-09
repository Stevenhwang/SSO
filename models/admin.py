from tortoise import fields
from models.base import TimestampMixin, BaseModel


class User(BaseModel, TimestampMixin):
    # 用户表
    password = fields.CharField(128)
    email = fields.CharField(50, unique=True, null=True)
    tel = fields.CharField(11, null=True)  # 手机号
    no = fields.CharField(50, null=True)  # 工号
    department = fields.CharField(64, null=True)  # 部门
    google_key = fields.CharField(80, null=True)  # 谷歌动态认证
    is_super = fields.BooleanField(default=False)  # 是否为超级用户
    status = fields.BooleanField(default=False)  # 是否启用
    last_login_ip = fields.CharField(32, null=True)  # 记录登录ip
    last_login_time = fields.DatetimeField(null=True)  # 记录登录时间
    roles: fields.ManyToManyRelation["Role"]  # 关联

    class Meta:
        table = "users"


class Role(BaseModel, TimestampMixin):
    # 角色表
    status = fields.BooleanField(default=False)  # 是否启用
    users = fields.ManyToManyField('models.User', related_name='roles', through='role_user')
    components = fields.ManyToManyField('models.Component', related_name='roles', through='role_component')
    menus = fields.ManyToManyField('models.Menu', related_name='roles', through='role_menu')
    functions = fields.ManyToManyField('models.Function', related_name='roles', through='role_function')

    class Meta:
        table = "roles"


class Component(BaseModel, TimestampMixin):
    # 前端权限组件表
    remark = fields.CharField(128, null=True)
    status = fields.BooleanField(default=False)  # 是否启用
    roles: fields.ManyToManyRelation[Role]  # 关联

    class Meta:
        table = "components"


class Menu(BaseModel, TimestampMixin):
    # 前端权限菜单表
    remark = fields.CharField(128, null=True)
    status = fields.BooleanField(default=False)  # 是否启用
    roles: fields.ManyToManyRelation[Role]  # 关联

    class Meta:
        table = "menus"


class Function(BaseModel, TimestampMixin):
    # 后端权限路由表
    uri = fields.CharField(128)
    method_type = fields.CharField(16)
    status = fields.BooleanField(default=False)  # 是否启用
    roles: fields.ManyToManyRelation[Role]  # 关联

    class Meta:
        table = "functions"


class SysLog(BaseModel, TimestampMixin):
    # 系统日志
    name = fields.CharField(128)
    method = fields.CharField(16)
    uri = fields.CharField(512)
    data = fields.TextField(null=True)
    login_ip = fields.CharField(64, null=True)

    class Meta:
        table = "sys_log"
