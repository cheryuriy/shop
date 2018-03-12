from django.contrib import admin

from .models import Product, Provider, Category

admin.site.register(Product)
admin.site.register(Provider)
admin.site.register(Category)