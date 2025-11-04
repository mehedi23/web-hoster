from django.db import models
from base.models import BaseModel
from user.models.profile import MerchantProfile

class Shop(BaseModel):
    user = models.ForeignKey(MerchantProfile, on_delete=models.PROTECT, related_name='shops')
    shop_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)
    about_shop = models.TextField(null=True, blank=True)

    # contact information
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)

    # legal information
    privacy_policy = models.TextField(null=True, blank=True)
    policies = models.TextField(null=True, blank=True)
    terms_and_conditions = models.TextField(null=True, blank=True)

    # social media links
    facebook_link = models.URLField(null=True, blank=True)
    x_link = models.URLField(null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    linkedin_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.shop_name

