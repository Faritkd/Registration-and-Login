from django.urls import path
from . import views
urlpatterns = [
    path("", views.home_view, name="home"),
    path("registration/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("account_activation/<verification_code>", views.activate_account, name="account_activation"),
    path("forget_password/", views.ForgetPasswordView.as_view(), name="forget_password"),
    path("reset_password/<verification_code>", views.ResetPasswordView.as_view(), name="reset_password"),
]