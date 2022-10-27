from contextlib import nullcontext
from email.policy import HTTP
from lib2to3.pgen2.pgen import ParserGenerator
from tkinter import N
from unicodedata import name
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from urllib3 import HTTPResponse
from .models import *
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt # < --- helps activate or desactivate
from django.core.mail import send_mail
import time 

import json
import os
import stripe

stripe.api_key = 'sk_test_51Lt29IL5ApivNSuEe7C1hMyGj05XnUKeqBsxnl8m1FIz2wGju7qjFqW3Yphy3cWm1Eqdj6ciYP6OWVg1JQmqF3Mi001Wbl5BU1'

#  controller / views
def homePage(request):
    return render(request,'home.html',{'version':'1.0.0','bag_items_count':countItemsInBag(request)})



def countItemsInBag(request):
      if  request.session.get('bag_id',False):
          bag_id = request.session['bag_id']
          items = BagItem.objects.filter(bag_id = bag_id)
          items_count = len(items)
          return items_count

      

def catalogPage(request):
     products  = Product.objects.all()
     paginator = Paginator(products,4)# create the paginator object
     
     selected_page_number = request.GET.get('page') or 1

     page      = paginator.page(selected_page_number)         # select first page
     products  = page.object_list

     return render(request,'catalog.html',{'products':products,
             'paginator': paginator, 'page_number': page.number,'bag_items_count':countItemsInBag(request)})





def checkOut(request):
  # HW20* Check if client_id exist in sesion 
#         skip this page redirect to confirm order
      
     # if  request.session.get('client_id', False):
     #      client_id = request.session['client_id']
     #      client = Bag.objects.get(pk= client_id)    
     #      return render(request,'order-confirm.html') 
     # else:
          return render(request,'checkout.html',{'bag_items_count':countItemsInBag(request)})



@csrf_exempt # < ---@ helps activate or desactivate 
def CreatePaymentIntent(request):
    
     try:
          
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk = bag_id)

          total_cost =int(bag.cost.amount*100)
          intent = stripe.PaymentIntent.create(
               amount= total_cost,
               currency='eur',
               automatic_payment_methods={
                    'enabled': True,
               },
          )

          return JsonResponse({
               'clientSecret': intent['client_secret']
          })
     except Exception as e:
          return JsonResponse(error=str(e),status = 403)
          
     

def viewBag(request): 
     items = []
     if request.session.get('bag_id', False):
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk= bag_id)
          items = BagItem.objects.filter(bag_id=bag_id)
          for item in items:
               
               item.cost = item.quantity * item.product.price.amount
               return render(request,'bag.html',{'bag_items_count':countItemsInBag(request), 'items': items, 'bag':bag,})
          # HW 18 BAG is empty if no products in bag
     else:
         #return HttpResponse('Your Bag is empty! BUY PRODUCT!')
          return redirect(request.META.get('HTTP_REFERER'))



def completePayment(request):
     # get bag from session
     if  request.session.get('bag_id', False):
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk= bag_id)
          
          
          # sendind email
          # send_mail(
          #           'Payment Confirmation for order | e-shop',
          #           'Here is the message.', #HW 22 include amoun payment gateway (stripe) list items 
          #           'brownlaw911@gmail.com',   # <--- settings.EMAIL_HOST_USER 
          #           ['staver37@gmail.com'], # substitute  with clien email adres
          #           fail_silently=False,
          #           ) 



          # HW* 23 :  create a model named  Payment(id,created,updated,client_id,gateway_id)     
          # check get parameter in url
          # delete bag
          bag.delete()
          # delete bag id from session
          request.session.pop('bag_id')
          # send email
     return render(request,'payment-completed.html',{})


# def delleteBag(request):
#      # delete bag
#      if  request.session.get('bag_id', False):
#           bag_id = request.session['bag_id']
#           bag = Bag.objects.get(pk= bag_id)
#           bag.delete()
#           # delete bag id from session
#           request.session.pop('bag_id')
#           # send email
#      return render(request,'bag.html',{'bag_items_count':countItemsInBag(request),})








def confirmOrdedr(request):
     # create new client
     fullName = request.POST.get('fullName')
     phoneNumber = request.POST.get('phoneNumber') 
     emailAddress = request.POST.get('emailAddress')
     password = request.POST.get('password')

     client = Client.objects.create(name=fullName,email=emailAddress,phone=phoneNumber,pasword=password,is_vip = False)
     # extract the curent  client_id from sesion and added in bag
     request.session['client_id'] = client.id      
     bag_id = request.session['bag_id']
     bag = Bag.objects.get(pk= bag_id)
     bag.client = client
     bag.save()
     return render(request,'order-confirm.html')





def buyProduct(request):
     product_id = request.GET.get('pid')
     # 1. find the product
     product = Product.objects.get(pk=product_id)
    # 2. does user have a bag?
     product_stock = ProductStock.objects.get(product_id= product_id)
     if  request.session.get('bag_id',False):
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk=bag_id)
# HW16 optimize the code bellow
# if item inBag:
#          update item _q
#          update_stock_q
#else:
          # create_bag_item()
          # update_stock_q
 # HW 17*: 
          # TRANSACTION BEGIN
          # qs -= 1
          # 
          # qb += 1
          # TRANSACTION COMMIT
          
          # check if the product is in the bag
          item_in_bag = BagItem.objects.filter(product_id=product_id,bag_id=bag_id)    
          if len(item_in_bag) > 0:
               item = item_in_bag.first() # <-  extract object from [queryset]
               item.quantity += 1
               bag.cost.amount += product.price.amount
               bag.cost.save()
               item.save()

               product_stock.quantity -= 1
               product_stock.save()
   
          else:
               bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)
               bag.cost.amount += product.price.amount
               bag.cost.save()
               product_stock.quantity -= 1
               product_stock.save()
     else:
     # 2. a - create a bag
          cost = Money.objects.create(amount=0,currency="EUR")
          bag = Bag.objects.create(cost=cost) 
          request.session['bag_id'] = bag.id
          bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)
          
          bag.cost.amount += product.price.amount
          bag.cost.save()
          product_stock.quantity -= 1
          product_stock.save()

     #    2. b - load the bag
     # bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)

     # 3. add bag item withproduct to bags    
     render(request,'blank.html',{ })
     # returned to the same page
     return redirect(request.META.get('HTTP_REFERER'))



def decreasesProductInBag(request):
     product_id = request.GET.get('pid')
     # 1. find the product
     product = Product.objects.get(pk=product_id)
    # 2. does user have a bag?
     product_stock = ProductStock.objects.get(product_id= product_id)
     if  request.session.get('bag_id',False):
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk=bag_id)

# HW16 optimize the code bellow
# if item inBag:
#          update item _q
#          update_stock_q
#else:
          # create_bag_item()
          # update_stock_q
 # HW 17*: 
          # TRANSACTION BEGIN
          # qs -= 1
          # 
          # qb += 1
          # TRANSACTION COMMIT
          # check if the product is in the bag

          item_in_bag = BagItem.objects.filter(product_id=product_id,bag_id=bag_id)    
          if len(item_in_bag) > 0:
               item = item_in_bag.first() # <-  extract object from [queryset]
               item.quantity -= 1
               bag.cost.amount -= product.price.amount
               bag.cost.save()
               item.save()

               product_stock.quantity += 1
               product_stock.save()
   
          else:
               bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)
               bag.cost.amount -= product.price.amount
               bag.cost.save()
               product_stock.quantity += 1
               product_stock.save()
     else:
     # 2. a - create a bag
          cost = Money.objects.create(amount=0,currency="EUR")
          bag = Bag.objects.create(cost=cost) 
          request.session['bag_id'] = bag.id
          bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)
          
          bag.cost.amount -= product.price.amount
          bag.cost.save()
          product_stock.quantity += 1
          product_stock.save()

     #    2. b - load the bag
     # bag_item = BagItem.objects.create(quantity =1, product = product,bag = bag)

     # 3. add bag item withproduct to bags    
     render(request,'blank.html',{ })
     # returned to the same page
     return redirect(request.META.get('HTTP_REFERER'))




def deleteBag(request):
          request.session.get('bag_id', False)
          bag_id = request.session['bag_id']
          bag = Bag.objects.get(pk= bag_id)
          bag.delete()
          request.session.pop('bag_id')
          return redirect(request.META.get('HTTP_REFERER'))







def viewProduct(request):
     product_id = request.GET.get('pid')
     product = Product.objects.get(pk=product_id)
     return render(request,'ProdDetails.html',{'product':product,'products':product , 'bag_items_count':countItemsInBag(request)})
     

def seedData(request):
    return HttpResponse('Seeding done!') 




""" 
                PAYMENT METHOD

1.                       /order-confirm--------->FRONTEND(html,js)
2.              BACKEND (py)  <----------------------JS                     
                CreatePaymentIntent() 
                        \------------------>stripe API() stripe.PaymentIntent.create() ---> SRIPE API
                     intent  <------------------------------------------------ response -----/
                       intent.clientSecret ------------> JS
                                                          |
                                                     Payment Form
                                                           \---------------------> finalize payment
                                  payment-completed <---redirect  <------------------------/
                                   |        
                                   V     
                                   show success message
                                   delete the bag
                                   send confirmation email
                                        
                                        
 """