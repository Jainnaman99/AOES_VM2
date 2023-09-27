from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class ApplicationUser(models.Model):
    user = models.OneToOneField(User, related_name='appusers', on_delete=models.CASCADE)
    roles = models.ManyToManyField(UserRole, related_name='user_roles')
    reset = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username