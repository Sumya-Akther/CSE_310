from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image=models.ImageField(default='default.jpg',upload_to="profile_pics/")
    def _str_(self):
        return f'{self.user.username} Profile'
