from django.contrib import admin
from shop.models.shop import Shop
from shop.models.product import Product, Category, DeliveryOption, ProductImage, ProductOption, ProductOptionValue
from shop.models.order import Order, OrderProduct

# Register your models here.
admin.site.register(Shop)
admin.site.register(Product)
admin.site.register(ProductOption)
admin.site.register(ProductOptionValue)
admin.site.register(Category)
admin.site.register(DeliveryOption)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderProduct)
