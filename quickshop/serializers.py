from rest_framework import serializers
from .models import CustomUser, Product, Order, OrderDetail

# class CustomUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['user_id', 'email', 'name', 'password', 'role', 'is_active', 'is_staff', 'groups', 'user_permissions']

# class CustomUserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser
#         fields = ['user_id', 'email', 'name', 'password', 'role']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'name', 'password', ]
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['role'] = "Customer"
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
   
class UpdateCustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name']

class UpdateAdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'role']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'price', 'stock_quantity']

class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'date', 'total_amount']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user_id', 'date', 'total_amount']

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['order_detail_id', 'order_id', 'product_id', 'quantity', 'price']

class UpdateOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['order_id', 'product_id', 'quantity', 'price']
