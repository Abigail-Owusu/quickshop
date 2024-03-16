from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order, OrderDetail, CustomUser
from .serializers import *
from .permissions import  IsSalesPersonnel, IsInventoryManager, IsAdministrator, IsCustomer
from django.contrib.auth.tokens import default_token_generator
from Helper_func.helpers import send_verification_email
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render
from django.contrib.auth.hashers import identify_hasher, make_password


# User views
@api_view(['GET'])
def verify_email(request):
    """
    Verify a user's email address
    """
    try:
        user_idb64 = request.query_params.get('uid')
        uid = force_str(urlsafe_base64_decode(user_idb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None:
        user.email_verified = True
        user.save()
        return render(request, 'email_verified.html')
    else:
        
        return render(request, 'email_verification_failed.html')

@api_view(['POST'])
def user_signup(request):
    """
    Register a new user
    """
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(email_verified=False)  # Set email_verified to False initially

            # Generate a verification token for the user
            verification_token = default_token_generator.make_token(user)

            # Send the verification email
            send_verification_email(user, verification_token)

            return Response({'message': 'Sign up successful. Verification email sent.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def user_login(request):
    """
    Login a user
    """
    if request.method == 'POST':
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
    
        print(email)
        # Check if the password is already hashed
        if identify_hasher(user.password) is None:
            # Password is not hashed, hash it
            hashed_password = make_password('new_password')
            user.password = hashed_password
            user.save()
        
        password = request.data.get('password')

        # user = authenticate(request, email=email, password=password)
        # user = CustomUser.objects.filter(email=email).first()
    
        if user is None:
            return Response({'error': 'User does not exist!!'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the user has verified their email address
        if user.check_password(password) and user.email_verified == 1:
            print("User is authenticated")
            token, _ = Token.objects.get_or_create(user=user)
            print(token)
            return Response({
                'message': 'Login successful',
                'token': token.key, 
                'email': user.email, 
                'role': user.role,
                'name': user.name

                }, 
                status=status.HTTP_200_OK)
        
        if user.email_verified == 0:
            return Response({'error': 'Please verify your email address to login'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdministrator])
def view_users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdministrator |IsCustomer])
def edit_user(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'Customer':
        if user_id != request.user.user_id:
            return Response({"message": "You are not authorized to edit this user"}, status=status.HTTP_401_UNAUTHORIZED)
        #Customer cannot edit their role
        serializer = UpdateCustomerUserSerializer(user, data=request.data, partial=True)
    if request.user.role == 'Administrator':
        serializer = UpdateAdminUserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdministrator])
def delete_user(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


    
# Product views
@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdministrator])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsSalesPersonnel | IsAdministrator|IsInventoryManager|IsCustomer])
def view_product(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(pk=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsSalesPersonnel | IsAdministrator|IsInventoryManager|IsCustomer])
def view_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,IsAdministrator|IsInventoryManager])
def edit_product(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdministrator])
def delete_product(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


#Order views
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsSalesPersonnel | IsAdministrator | IsInventoryManager|IsCustomer])
def view_order(request):
    """
    View a particular order
    """
    user_id_order = request.query_params.get('user_id')
    user_id_auth = request.user.user_id
    if request.user.role == 'Customer':
        if user_id_order != user_id_auth:
            return Response({"message": "You are not authorized to view this order"}, status=status.HTTP_401_UNAUTHORIZED)
    if not user_id_order:
        return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
     
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({"message": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(pk=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsSalesPersonnel | IsAdministrator | IsInventoryManager])
def view_orders(request):
    """
    View all orders
    """
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def create_order(request):
    """
    Create a new order
    """
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def edit_order(request):
    """
    Edit an order
    """
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({"message": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateOrderSerializer(order, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def delete_order(request):
    """
    Delete an order
    """
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({"message": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


#OrderDetail views
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsSalesPersonnel | IsAdministrator | IsInventoryManager])
def view_order_detail(request):
    """
    View a particular order detail
    """
    order_detail_id = request.query_params.get('order_detail_id')
    if not order_detail_id:
        return Response({"message": "Order detail ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order_detail = OrderDetail.objects.get(pk=order_detail_id)
        serializer = OrderDetailSerializer(order_detail)
        return Response(serializer.data)
    except OrderDetail.DoesNotExist:
        return Response({"message": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def create_order_detail(request):
    """
    Create a new order detail
    """
    serializer = OrderDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def delete_order_detail(request):
    """
    Delete an order detail
    """
    order_detail_id = request.query_params.get('order_detail_id')
    if not order_detail_id:
        return Response({"message": "Order detail ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order_detail = OrderDetail.objects.get(pk=order_detail_id)
    except OrderDetail.DoesNotExist:
        return Response({"message": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    order_detail.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,IsAdministrator|IsSalesPersonnel])
def edit_order_detail(request):
    """
    Edit an order detail
    """
    order_detail_id = request.query_params.get('order_detail_id')
    if not order_detail_id:
        return Response({"message": "Order detail ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order_detail = OrderDetail.objects.get(pk=order_detail_id)
    except OrderDetail.DoesNotExist:
        return Response({"message": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateOrderDetailSerializer(order_detail, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)