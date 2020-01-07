from views.users_view import UsersView, UserView
from views.roles_view import RolesView, RoleView
from views.menus_view import MenusView, MenuView

routers = [
    (UsersView.as_view(), '/users'),
    (UserView.as_view(), '/user/<uid:int>'),
    (RolesView.as_view(), '/roles'),
    (RoleView.as_view(), '/role/<rid:int>'),
    (MenusView.as_view(), '/menus'),
    (MenuView.as_view(), '/menu/<mid:int>'),
]
