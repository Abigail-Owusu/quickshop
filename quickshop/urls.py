"""
URL configuration for quickshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("admin/", admin.site.urls),
     # User authentication URLs
    path('signup/', user_signup),
    path('users', view_users),
    path('login/', user_login),
    path('api/verify', verify_email),
    path('users/delete', delete_user),
    path('api/update_user', edit_user),
    
    # Product URLs
    path('products/', create_product),
    path('product', view_product),
    path('product_edit/', edit_product),
    path('products/delete/', delete_product),
    path('products', view_products),

    # Order URLs
    path('create_order/', create_order),
    path('order', view_order),
    path('orders', view_orders),
    path('orders/', edit_order),
    path('orders/delete/', delete_order),

    # OrderDetail URLs
    path('orderdetails/', create_order_detail),
    path('orderdetail', view_order_detail),
    path('orderdetails', view_order_details),
    path('edit_orderdetails/', edit_order_detail),
    path('orderdetails/delete/', delete_order_detail),


  
]
