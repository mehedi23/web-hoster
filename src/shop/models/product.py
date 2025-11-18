from django.db import models
from base.models import BaseModel
from shop.models.shop import Shop
from utils.compress_and_resize_image import compress_and_resize_image


class Category(BaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class DeliveryOption(BaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='delivery_options')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Product(BaseModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products_category'
    )

    youtube_link = models.URLField(null=True, blank=True)
    delivery_options = models.ManyToManyField(
                        DeliveryOption, 
                        related_name='products_delivery_options', 
                        blank=True,
                        null=True
                    )
    return_and_warranty_time = models.CharField(max_length=100, null=True, blank=True)
    return_and_warranty_policy = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    images = models.ImageField(upload_to='product_images/lg/')
    small_images = models.ImageField(upload_to='product_images/sm/')

    def __str__(self):
        return f'Image for {self.product.name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        compress_and_resize_image(self.images.path, max_size=(800, 800), max_file_size_kb=80)
        compress_and_resize_image(self.small_images.path, max_size=(200, 200), max_file_size_kb=20)



class ProductOption(BaseModel):
    product = models.ForeignKey(Product, related_name='product_options', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_multiple_choice = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} for {self.product.name}'
    
    

class ProductOptionValue(BaseModel):
    product_option = models.ForeignKey(ProductOption, related_name='option_values', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='option_icons/', null=True, blank=True)
    value = models.CharField(max_length=100)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.value} of {self.product_option.name}'