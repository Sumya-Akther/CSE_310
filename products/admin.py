from django.contrib import admin
from . models import  Product,Review
from .models import Payment
# Register your models here.

admin.site.register(Product)
admin.site.register(Review)
admin.register(Payment)