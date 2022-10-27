from email.policy import default
from django.db import models

class Money(models.Model):
        id = models.AutoField(primary_key=True)

        CHOCES =(
            ('EUR','Euro'),
            ('USD','US Dollar'),
            ('MDL','Moldavian Leu'),
        )
        amount = models.DecimalField(max_digits=11,decimal_places=2)
        currency = models.CharField(max_length=4,choices=CHOCES,default='MDL')

    # TBD: type

class Product(models.Model):
        id = models.AutoField(primary_key=True)
        name = models.CharField(max_length=100)
        image = models.CharField(max_length=150)
        description = models.CharField(max_length=300, default='')
        bar_code= models.CharField(max_length=13, default='')
        created = models.DateTimeField(auto_now_add=True)    #RELATIONSHIP
        updated = models.DateTimeField(auto_now_add=True)
        price=models.ForeignKey(Money, on_delete=models.CASCADE, null=True) # TODO: forbit3 cascading

class ProductStock(models.Model):
        quantity = models.IntegerField()
        created = models.DateTimeField(auto_now_add=True)
        updated = models.DateTimeField(auto_now_add=True)        # REL
        product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)


class Client(models.Model):
        id = models.AutoField(primary_key=True)
        name = models.CharField(max_length=60,default='')
        email = models.CharField(max_length=100,default='')
        phone= models.CharField(max_length=15,default='')
        is_vip= models.BooleanField()
        pasword= models.CharField(max_length=160,default='')
        created = models.DateTimeField(auto_now_add=True)
        updated = models.DateTimeField(auto_now_add=True)

class Bag(models.Model):
        id = models.AutoField(primary_key=True)
        created = models.DateTimeField(auto_now_add=True)
        updated = models.DateTimeField(auto_now_add=True)
        # REL
        cost = models.ForeignKey(Money,on_delete=models.CASCADE, null=True)
        client = models.ForeignKey(Client,on_delete=models.CASCADE, null=True)

class BagItem(models.Model):
        id = models.AutoField(primary_key=True)
        quantity = models.IntegerField()

        #REL
        product = models.name = models.ForeignKey(Product,on_delete=models.CASCADE, null=True)
        bag = models.ForeignKey(Bag,on_delete=models.CASCADE, null=True)
        

