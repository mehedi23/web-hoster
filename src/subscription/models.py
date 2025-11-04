from django.db import models
from base.models import BaseModel



class SubscriptionPlan(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    product_quota = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class UserSubscription(BaseModel):
    user = models.ForeignKey('user.MerchantProfile', on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    product_quota = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.plan.name}'