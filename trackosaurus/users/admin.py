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
    list_display = ('user_email', 'key', 'created')

    def get_queryset(self, request):
        return APIKey.objects.select_related('user')

    def user_email(self, instance):
        return instance.user.email
