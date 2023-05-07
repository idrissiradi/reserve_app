from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    PermissionRequiredMixin,
)


class EmailLoginOnlyView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.login_method == "email"  # type: ignore

    def handle_no_permission(self):
        messages.error(self.request, "Can't go there")  # type: ignore
        return redirect(reverse("reserve:home"))


class LoggedOutOnlyView(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated  # type: ignore

    def handle_no_permission(self):
        messages.error(self.request, "Can't go there")  # type: ignore
        return redirect(reverse("reserve:home"))


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy("users:login")


class AdminOnlyView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.admin  # type: ignore

    def handle_no_permission(self):
        messages.error(self.request, "Can't go there")  # type: ignore
        return redirect(reverse("reserve:home"))
