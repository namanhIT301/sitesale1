#normal_django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
import json, requests
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import ContactMessage, UserToken
from django.db.models import Q
from django.conf import settings

#API_for_rest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login as auth_login
import logging
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import *

logger = logging.getLogger(__name__)

#api_view

class NewsListCreateAPIView(generics.ListCreateAPIView):
    queryset = News.objects.all().order_by('-published_date')
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class NewsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CartAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        customer = self.request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        return order

class OrderItemAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

class ContactCreateAPIView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                refresh = RefreshToken.for_user(user)
                UserToken.objects.update_or_create(
                    user=user,
                    defaults={
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token)
                    }
                )
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutUser(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                UserToken.objects.filter(refresh_token=refresh_token).delete()
                return Response({"detail": "Successfully logged out."}, status=200)
            return Response({"detail": "'refresh' parameter is missing"}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

def create_user_token(user_id):
    user = get_object_or_404(User, id=user_id)
    user_token, created = UserToken.objects.get_or_create(user=user)
    return user_token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomRefreshTokenSerializer
    
#normal
def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete = False)
        items = order.orderitem_set.all()
        cartItems =  order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total': 0}
        cartItems =  order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    id = request.GET.get('id','')    
    products = Product.objects.filter(id=id)
    categories = Category.objects.filter(is_sub = False)
    context= {'products': products, 'categories': categories,'items':items,'order':order, 'cartItems':cartItems, 'user_not_login': user_not_login, 'user_login':user_login}
    return render(request,'app/detail.html',context)

def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category_slug = request.GET.get('category', '')
    searched = request.GET.get('searched', '')

    if active_category_slug:
        active_category = Category.objects.get(slug=active_category_slug)
        products = Product.objects.filter(category__slug=active_category_slug)
    else:
        active_category = None
        products = Product.objects.all()

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'categories': categories, 'products': products, 'active_category': active_category, 'searched': searched, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/category.html', context)


def search(request):
    searched = request.POST.get("searched", "").strip()
    keys = Product.objects.filter(Q(name__icontains=searched) | Q(name__icontains=searched.capitalize()))

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    products = Product.objects.all()
    context = {"searched": searched, "keys": keys,'products': products, 'cartItems': cartItems, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, "app/search.html", context)

def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('login')    
    
    if request.user.is_authenticated:
        customer = request.user
        user_not_login = "hidden"
        user_login = "show"
        items = order.orderitem_set.all()
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    context = {'order':order,'items':items, 'cartItems': cartItems, 'categories': categories,'user_not_login': user_not_login, 'user_login': user_login, 'form':form}
    return render(request,'app/register.html',context)

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')

    categories = Category.objects.filter(is_sub=False)
    context = {'categories': categories, 'user_not_login': "show", 'user_login': "hidden"}
    return render(request, 'app/login.html', context)
        

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete = False)
        items = order.orderitem_set.all()
        cartItems =  order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total': 0}
        cartItems =  order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    
    hot_products = Product.objects.filter(is_hot=True)
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    category_id = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if category_id:
        products = products.filter(category__id=category_id)

    if price_min:
        products = products.filter(price__gte=price_min)

    if price_max:
        products = products.filter(price__lte=price_max)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'hot_products': list(hot_products.values()),
            'items': list(items.values()),
            'categories': list(categories.values()),
            'products': list(products.values()),
            'cartItems': cartItems,
        }
        return JsonResponse(response_data)
    context={'hot_products':hot_products, 'items':items, 'categories':categories,'products': products,'cartItems':cartItems, 'user_not_login': user_not_login, 'user_login':user_login}
    return render(request,'app/home.html',context)
    
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete = False)
        items = order.orderitem_set.all()
        cartItems =  order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total': 0}
        cartItems =  order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    categories = Category.objects.filter(is_sub = False)
    context= {'categories': categories,'items':items,'order':order, 'cartItems':cartItems, 'user_not_login': user_not_login, 'user_login':user_login}
    return render(request,'app/cart.html',context)


def checkout(request):
    if request.method == 'POST':
        form_data = request.POST
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        address = form_data.get('address', '')
        city = form_data.get('city', '')
        state = form_data.get('state', '')
        mobile = form_data.get('mobile', '')
        country = form_data.get('country', '')
        shipping_address = ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=address,
            city=city,
            state=state,
            mobile=mobile,
        )
        return render(request, 'app/thank_you2.html')
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        items = []
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    categories = Category.objects.filter(is_sub=False)
    products = Product.objects.all()

    context = {'items': items, 'order': order, 'cartItems': cartItems,'categories': categories, 'products': products,'user_not_login': user_not_login,'user_login': user_login}
    return render(request, 'app/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer =customer,complete = False)
    orderItem, created = OrderItem.objects.get_or_create(order =order,product = product)
    if action == 'add': 
        orderItem.quantity +=1
    elif action =='remove':
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity<=0:
        orderItem.delete()
        
    return JsonResponse('added', safe = False)

def contact(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete = False)
        items = order.orderitem_set.all()
        cartItems =  order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total': 0}
        cartItems =  order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    context={'items':items,'categories':categories,'products': products,'cartItems':cartItems, 'user_not_login': user_not_login, 'user_login':user_login}    
    return render(request, 'app/contact.html',context)

def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')

        contact_message = ContactMessage.objects.create(name=name, email=email, message=message)
        messages.info(request, 'New messages!')

        return render(request, 'app/thank_you.html')  

def checkout_process(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        mobile = request.POST.get('mobile')
        country = request.POST.get('country')

        shipping_address = ShippingAddress.objects.create(
            customer=request.user,
            order=None,
            address=address,
            city=city,
            state=state,
            mobile=mobile,
        )

        
        return redirect('cart')

    return render(request, 'app/checkout.html', {})

def news(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete = False)
        items = order.orderitem_set.all()
        cartItems =  order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total': 0}
        cartItems =  order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    news_list = News.objects.all().order_by('-published_date')
    latest_posts = News.objects.all().order_by('-published_date')[:3] 
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    context = {'categories':categories,'products': products,'items': items, 'order': order, 'cartItems': cartItems,'user_not_login': user_not_login,'user_login': user_login, 'news_list': news_list, 'latest_posts': latest_posts}
    return render(request, 'app/news.html', context)

def news_detail(request, pk):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        cartItems = order['get_cart_items']
        user_not_login = "show"
        user_login = "hidden"

    try:
        news_item = get_object_or_404(News, pk=pk)
    except News.DoesNotExist:
        news_item = None
    print("News Item:", news_item) 

    news_list = News.objects.all().order_by('-published_date')
    categories = Category.objects.filter(is_sub = False)
    products = Product.objects.all()
    latest_posts = News.objects.all().order_by('-published_date')[:3] 

    context = {'news_list': news_list,'latest_posts':latest_posts,'categories':categories,'products': products,'items': items,'order': order,'cartItems': cartItems, 'user_not_login': user_not_login, 'user_login': user_login, 'news_item': news_item}
    return render(request, 'app/news_detail.html', context)


    