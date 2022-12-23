from django.urls import path
from .views import *
# list of app routes
urlpatterns = [
    path('',homePage),
    path('products',catalogPage),
    path('products/seed',seedData),
    path('buy', buyProduct),
    path('decreasesProd', decreasesProductInBag),
    path('deleteBag', deleteBag),
    path('product/details',viewProduct),
    path('cart',viewBag),  
    path('checkout',checkOut),      
    path('order-confirm',confirmOrdedr),   
    path('create-payment-intent',CreatePaymentIntent),   
    path('payment-completed',completePayment), 
    path('contact', coontact_view),
    path('sent-message', sendMessage),

    
    # admin routes
    path('admin/product/add/form', addProductForm),
    path('admin/product/add/submit', saveProduct),
]
