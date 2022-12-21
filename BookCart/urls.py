'''
This is where the url routing is handled
Each valid url is associated with a name
and a views function to handle processing the page
Last modified: 11/01
'''
from django.contrib import admin
from django.urls import path
import Cart.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('account', views.account, name='account'),
    path('account/create', views.createAccount, name='createAccount'),
    path('cart', views.cart, name='cart'),
    path('cart/add', views.addCartItem, name='addItem'),
    path('cart/remove', views.removeCartItem, name='removeItem'),
    path('cart/purchase', views.purchase, name='purchase'),
    path('publisher', views.publisher, name='publisher'),
    path('publisher/<str:p>', views.publisher, name='publisher'),
    path('author', views.author, name='author'),
    path('author/<str:a>', views.author, name='author'),
    path('about', views.about, name='about')
]