from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("create_user/", views.CreateUser.as_view(), name="create_user"),
    path("register/", views.register_once, name="register"),
    path("logout/", views.log_out, name="logout"),
]
