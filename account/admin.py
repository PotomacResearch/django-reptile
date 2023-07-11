from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from account.models import Account
from django.db.models.functions.text import Lower


admin.site.register(User, UserAdmin)


# or admin.StackedInline for a different layout
class UserInline(admin.TabularInline):
    model = User
    extra = 1
    fields = (
        "password",
        "username",
        "groups",
        "first_name",
        "last_name",
        "email",
        "is_active"
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = "name", "user_count", "is_active"
    ordering = (Lower("name"),)

    inlines = [UserInline, ]

    fields = (
        "name",
        "is_active",
    )


    @admin.display(description="Users")
    def user_count(self, obj: Account):
        return f'{obj.users.count()}'
