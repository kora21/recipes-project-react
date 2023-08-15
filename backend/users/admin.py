from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'password')
    # list_editable = ('password', 'username')
    list_filter = ('email', 'first_name', 'last_name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
