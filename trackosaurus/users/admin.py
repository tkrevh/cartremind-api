from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User, APIKey


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    pass