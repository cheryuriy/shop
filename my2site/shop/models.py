from django.db import models
from django.utils import timezone

#python manage.py runserver

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Tовары относятся к разным категориям.
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=4000, default='')
    quantity = models.IntegerField(default=1)
    incoming_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# It's not using for now:
class Provider(models.Model):
    product = models.ManyToManyField(Product)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=24)  #  IntegerField(default=0)
    email = models.EmailField(default = None)

    def __str__(self):
        return self.name

