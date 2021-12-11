from django.contrib.auth.models import User
from django.db import models
from userapp.models import ResponsibilityGroup


class Profile(models.Model):
    User = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                related_name='Profile')
    Department = models.CharField(max_length=30)
    Phone = models.IntegerField(null=True)
    Photo = models.ImageField(null=True)
    IDResponsibilityGroup = models.ForeignKey(ResponsibilityGroup,
                                              null=True,
                                              blank=True,
                                              on_delete=models.CASCADE,
                                              related_name='profile')

    def __str__(self):
        return self.User.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
