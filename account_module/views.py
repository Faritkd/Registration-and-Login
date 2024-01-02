import random
import string
from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import View
from .forms import RegisterForm, LoginForm, ForgetPasswordForm, ChangePasswordForm
from .models import User
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.


def home_view(request):
    return render(request, "account_module/home.html")


def generate_activation_code():
    code = "".join(random.choices(string.ascii_letters + string.digits, k=72))
    return code


def send_verification_code(subject, to, context, template_name):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def activate_account(request, verification_code):
    user: User = User.objects.filter(verification_code=verification_code).first()
    if user is not None:
        if not user.is_active:
            user.is_active = True
            user.verification_code = generate_activation_code()
            user.save()
            return redirect(reverse("login"))
        messages.error(request, "your account has already been activated. so fuck off.💩")
    messages.error(request, "user not found")


class RegisterView(View):

    def get(self, request):
        registration_form = RegisterForm()
        context = {"registration_form": registration_form}
        return render(request, "account_module/registration.html", context)

    def post(self, request):
        registration_form = RegisterForm(request.POST)
        if registration_form.is_valid():
            user_email = registration_form.cleaned_data.get("email")
            user = User.objects.filter(email__iexact=user_email).exists()
            if user:
                registration_form.add_error("email", "This email is already taken")
            else:
                new_user = registration_form.save(commit=False)
                new_user.is_active = False
                new_user.verification_code = generate_activation_code()
                new_user.save()
                send_verification_code(
                    "account activation",
                    new_user.email,
                    {"verification_code": new_user.verification_code},
                    "account_module/activation.html",
                )
                messages.success(request, "please check your account for verification code.")
                return redirect(reverse("login"))
        context = {"registration_form": registration_form}
        return render(request, "account_module/registration.html", context)


class LoginView(View):
    def get(self, request):
        login_form = LoginForm()
        context = {"login_form": login_form}
        return render(request, "account_module/login.html", context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = User.objects.get(username=username)
            if user.check_password(password):
                if user.is_active:
                    login(request, user)
                    return HttpResponse(f"Hello {user}. You are logged in!")
                else:
                    return HttpResponse(f'Dear {user}, please activate your account.')
            else:
                login_form.add_error("username", "Invalid username or password")
        context = {"login_form": login_form}
        return render(request, "account_module/login.html", context)


class ForgetPasswordView(View):
    def get(self, request):
        forget_password_form = ForgetPasswordForm()
        context = {"forget_password_form": forget_password_form}
        return render(request, "account_module/forget_password.html", context)

    def post(self, request):
        forget_password_form = ForgetPasswordForm(request.POST)
        if forget_password_form.is_valid():
            user_email = forget_password_form.cleaned_data.get("email")
            user: User = User.objects.filter(email=user_email).first()
            if user is not None:
                user.verification_code = generate_activation_code()
                user.save()
                send_verification_code("Change Password",
                                       user_email,
                                       {"verification_code": user.verification_code},
                                       "account_module/change_pass_code.html",
                                       )

                return HttpResponse("Verification code has sent to your email.")
            else:
                messages.error(request, "User not found.")
        context = {"forget_password_form": forget_password_form}
        return render(request, "account_module/forget_password.html", context)


class ChangePasswordView(View):
    def get(self, request, verification_code):
        user = User.objects.filter(verification_code=verification_code).first()
        if user is None:
            return redirect(reverse("login"))
        change_password_form = ChangePasswordForm()
        context = {"change_password_form": change_password_form}
        return render(request, "account_module/change_password.html", context)

    def post(self, request, verification_code):
        change_password_form = ChangePasswordForm(request.POST)
        user = User.objects.filter(verification_code=verification_code).first()
        if change_password_form.is_valid():
            new_password = change_password_form.cleaned_data.get("password")
            new_confirm_password = change_password_form.cleaned_data.get("confirm_password")
            if new_password == new_confirm_password:
                user.set_password(new_password)
                user.is_active = True
                user.verification_code = generate_activation_code()
                user.save()
                return redirect(reverse("login"))

        context = {"change_password_form": change_password_form}
        return render(request, "account_module/change_password.html", context)
