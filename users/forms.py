from django import forms
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
    ReadOnlyPasswordHashField,
)

from .models import User


class NewUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class NewUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class UserCreateForm(forms.ModelForm):
    first_name = forms.CharField(label="Nom")
    last_name = forms.CharField(label="Prénom")
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="mot de passe", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Confirmez le mot de passe", widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Le mot de passe incorrect")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
        )

    def clean_password(self):
        return self.initial["password"]


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="mot de passe", widget=forms.PasswordInput())

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error(
                    "password", forms.ValidationError("Le mot de passe incorrect!")
                )
        except User.DoesNotExist:
            self.add_error(
                "email", forms.ValidationError("L'utilisateur n'existe pas!")
            )
