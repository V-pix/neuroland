from django.contrib import admin

from users.models import CustomUser


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "username", "email", "first_name", "last_name", "password"
    )
    list_display_links = ("id", "username")
    list_filter = ("username", "email")
    search_fields = (
        "username",
        "email",
    )
    empty_value_display = "-пусто-"


admin.site.register(CustomUser, UserAdmin)
