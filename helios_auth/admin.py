from django.contrib import admin

from .models import User


@admin.register(User)
class HeliosAuthUserAdmin(admin.ModelAdmin):
    list_display = ("id", "user_type", "user_id", "name", "admin_p")
    list_filter = ("user_type", "admin_p")
    search_fields = ("user_id", "name")
