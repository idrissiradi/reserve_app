from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.views.generic import FormView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from users.forms import LoginForm, UserCreateForm
from users.mixins import LoggedInOnlyView, LoggedOutOnlyView
from users.models import User


class LoginView(LoggedOutOnlyView, FormView):
    template_name = "auth/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next", None)
        if next_arg is not None:
            return next_arg

        return reverse("reserve:home")


class CreateUser(LoggedInOnlyView, FormView):
    """New user creation page"""

    template_name = "auth/create_newuser.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("reserve:home")

    def form_valid(self, form):
        form.save()  # type: ignore
        return super().form_valid(form)


@login_required(login_url=reverse_lazy("users:login"))
def log_out(request):
    logout(request)
    return redirect(reverse("users:login"))


@require_http_methods(["GET", "POST"])
def register_once(request):
    user = User.objects.filter(is_superuser=False)
    if user:
        return redirect(reverse("users:login"))

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            admin_user = form.save(commit=False)
            admin_user.admin = True
            admin_user.save()
            return redirect(reverse("users:login"))
    else:
        form = UserCreateForm()

    context = {
        "form": form,
    }
    return render(request, "auth/register.html", context)
