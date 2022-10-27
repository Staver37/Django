from django.test import SimpleTestCase
import requests
from ..models import *
import random

class DbFakeData(SimpleTestCase):

    databases= '__all__'

    # 1. setup - import from data 
    def setUp(self):
        
        # HW7: truncate all the tables: ba, bagitem, ... BEFORE IMPORTING DATA
        # hint use django access to DB or djando ORM
       
       
        Bag.         objects.all().delete()
        BagItem.     objects.all().delete()
        Client.      objects.all().delete()
        Money.       objects.all().delete()
        Product.     objects.all().delete()
        ProductStock.objects.all().delete()


        self.totalCount = 0
        print ("Starting database seeding...PRODUCTS")
        for id in range(1,11):
            r = requests.get(f"https://fakestoreapi.com/products/{id}")
            json_data = r.json()

            # map the JSON data to our MODEL
            price = Money.objects.create(
                amount = json_data['price'], currency = 'EUR'
                )
            product = Product.objects.create(
                id= json_data['id'],
                name= json_data['title'],
                description= json_data['description'][:280],
                price = price
                )
            stock = ProductStock.objects.create(quantity =10 * id, product=product)
            self.totalCount += 1    
        print("Done!")
    
    
        print ("Starting database seeding...CLIENTS")
        for id in range(1,6):

            r= requests.get(f"https://fakestoreapi.com/users/{id}")
            json_data = r.json() 
            Client.objects.create(
                id= json_data['id'],
                name= json_data['name']['firstname'] + ' ' + json_data['name']['lastname'],
                email=json_data['email'],
                phone= json_data['phone'], 
                is_vip= random.choice([True, False]),
                pasword=json_data['password'],
                )
            self.totalCount += 1    
            
        print("Done!")   




        print ("Starting database seeding...BAGS")
        for id in range(1,4):

            r= requests.get(f"https://fakestoreapi.com/carts/{id}")
            json_data = r.json()

            client_id = json_data['userId']
            client = Client.objects.get(pk=client_id)

            bag = Bag.objects.create(
                id= json_data['id'],
                client=client,
            # with out cost                
            )
            bag_cost = 0

            for item in json_data['products']:
                product_id = item['productId']
                quantity = item['quantity']
                product = Product.objects.get(pk=product_id)
                
                bag_cost += product.price.amount * quantity
                
                bag_items = BagItem.objects.create(
                    quantity = quantity,
                    bag = bag,
                    product = product
                )
            self.totalCount += 1    

            bag.cost = Money.objects.create(amount=bag_cost, currency="EUR")
            bag.save()

  
  
    # 2. the actual test - count the data
    def test_data_integrity(self):
        print("Checking generated data integrity...")
        self.assertEquals(self.totalCount,18, msg =f"only{self.totalCount}items were imported!!!")
    
    # 3. clear - IGNORE!!!
    def tearDown(self):
        print("Test data generated!")

