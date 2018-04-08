from django.contrib import admin

from .models import Product, Provider, Category, Guest, Product_in_cart, Photo

admin.site.register(Product)
admin.site.register(Provider)
admin.site.register(Category)
admin.site.register(Guest)
admin.site.register(Product_in_cart)
admin.site.register(Photo)