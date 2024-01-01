from django.urls import path
from . import views
urlpatterns = [
    path("", views.home_view, name="home"),
    path("registration/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("account_activation/<email_active_code>", views.activate_account, name="account_activation"),
]