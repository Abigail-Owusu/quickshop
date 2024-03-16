from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetail)
# admin.site.register(CustomUserManager)