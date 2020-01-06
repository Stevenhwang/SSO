from views.users_view import UsersView

routers = [
    (UsersView.as_view(), '/users')
]
