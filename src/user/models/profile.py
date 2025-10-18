from django.db import models
from base.models import BaseModel
from user.models.auth import User


class MerchantProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Profile of {self.user.email}'
