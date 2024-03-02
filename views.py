from django.shortcuts import render,redirect
from django.conf import settings
import stripe
from suganmarket.form import CustomUserForm
from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import json
from django.http import  JsonResponse

# Create your views here.
def home(request):
    return render(request,"shop/index.html")

def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
   

def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")
 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")

   

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
   
def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"shop/cart.html",{"cart":cart})
  else:
    return redirect("/")
  
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")

def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged Out Successfully...")
    return redirect('/')

def about(request):
    return render(request,"shop/about.html")

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully...")
                return redirect('/')
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect('/login')

    return render(request,"shop/login.html")


def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registeration Success You can login now..!!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"catagory":catagory})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request,"NO Such Catagory Found")
        return redirect('collections')


def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"shop/products/product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')
    



def get_cart_contents(request):
    # Your logic to retrieve cart contents goes here
    # For example, you might retrieve items from the session
    cart = request.session.get('cart', [])
    return cart

def calculate_total_amount(cart):
    # Your logic to calculate the total amount based on cart items
    total_amount = sum(item.get('total_cost', 0) for item in cart)
    return total_amount



def payment(request):
    cart = get_cart_contents(request)  # Assuming you have a function to get cart contents
    total_amount = calculate_total_amount(cart)

    if request.method == "POST":
        # Token is created using Stripe.js or Checkout!
        # Get the payment token submitted by the form:
        token = request.POST['stripeToken']

        # Create a charge: this will charge the user's card
        try:
            charge = stripe.Charge.create(
                amount=int(total_amount * 100),  # Amount in cents
                currency="usd",
                source=token,
                description="Example charge"
            )
        except stripe.error.CardError as e:
            # The card has been declined
            pass

        # Handle the successful payment (e.g., mark the order as paid)

    return render(request, 'shop/payment.html', {'total_amount': total_amount})