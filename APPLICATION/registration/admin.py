from django.contrib import admin
from registration.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserInline(admin.StackedInline):
    model = Profile
    can_delete = False
 
# Определяем новый класс настроек для модели User
class UserAdmin(UserAdmin):
    inlines = (UserInline, )
 
# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)