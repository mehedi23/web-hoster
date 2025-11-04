from django.contrib import admin
from .models import User, OTP, MerchantProfile

admin.site.register([User, OTP, MerchantProfile])
