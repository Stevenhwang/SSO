from views.users_view import UsersView, UserView

routers = [
    (UsersView.as_view(), '/users'),
    (UserView.as_view(), '/user/<uid:int>')
]
