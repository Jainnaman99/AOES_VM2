from django.contrib import admin
from .models import UserRole, ApplicationUser
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(UserRole)
admin.site.register(ApplicationUser)
