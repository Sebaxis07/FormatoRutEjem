from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.rut}"
