from django.db import models
from django.contrib.auth.models import User

class astroResponse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username