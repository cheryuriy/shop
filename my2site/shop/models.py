from django.db import models
from django.utils import timezone



class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Tовары относятся к разным категориям.
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # description = models.CharField(max_length=4000)
    # quantity = models.IntegerField(default=1)
    incoming_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# It's not using for now:
class Provider(models.Model):
    product = models.ManyToManyField(Product)
    name = models.CharField(max_length=200)
    phone = models.IntegerField(default=0)
    # email = models.EmailField()

    def __str__(self):
        return self.name

