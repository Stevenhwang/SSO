from views.users_view import UsersView, UserView
from views.roles_view import RolesView, RoleView

routers = [
    (UsersView.as_view(), '/users'),
    (UserView.as_view(), '/user/<uid:int>'),
    (RolesView.as_view(), '/roles'),
    (RoleView.as_view(), '/role/<rid:int>')
]
