'''
This is where the models that are related to the 
tables in the database are defined.
These are used as a proxy throughout the project
instead of directly accessing the database.
Last modified: 10/22
'''

from email.policy import default
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'publisher'

class Author(models.Model):
    name = models.CharField(max_length=60)
    address = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'author'

class Book(models.Model):
    isbn = models.CharField(db_column='ISBN', primary_key=True, max_length=13)
    title = models.CharField(max_length=100)
    publisher = models.ForeignKey(Publisher, models.CASCADE)
    author = models.ForeignKey(Author, models.CASCADE)
    year = models.PositiveSmallIntegerField(
        default=datetime.date.today().year,
        validators=[MinValueValidator(1500), MaxValueValidator(2022)]
    ) 
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'book'

class Customer(models.Model):
    email = models.CharField(primary_key=True, max_length=30)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    password = models.BinaryField()

    class Meta:
        managed = False
        db_table = 'customer'


class Cart(models.Model):
    customer = models.ForeignKey(Customer, models.CASCADE, db_column='customer_email')
    book = models.ForeignKey(Book, models.CASCADE, db_column='isbn')

    class Meta:
        managed = False
        db_table = 'cart'
