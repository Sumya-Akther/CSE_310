from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order, OrderItem,RateProduct
from django.utils.timezone import now
from .models import Product, CartItem
from django.http import JsonResponse
from django.contrib import messages
from . import forms



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    return redirect('shop')


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')



def update_quantity(request, cart_item_id):

    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if cart_items.exists():
        # Create a new order
        order = Order.objects.create(user=user)

        # Create order items and clear cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
        cart_items.delete()  # Clear the cart

        # Add success message
        messages.success(request, 'Checkout successful!!')

        return redirect('order_history')  # Redirect to order history
    else:
        messages.error(request, 'Your cart is empty. Please add items before checkout.')
        return redirect('cart')


def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


from .forms import ProductForm


def create_product(request):


    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'products/create_product.html', {'form': form})


def update_product(request, pk):


    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/create_product.html', {'form': form})


def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('home')

    return render(request, 'products/delete_products.html', {'product': product})
def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_details.html', {'product': product})

# For Review
def product_detail(request,p_id):
    product = get_object_or_404(Product, pk=p_id)
    reviews = product.reviews.all()
    average_rating= reviews.aggregate(Avg('rating'))['rating__avg'] if reviews else 0
    # average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews() else 0
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', p_id=product.id)
        else:
            return redirect('login')
    else:
        form = ReviewForm()

    return render(request, 'components/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating
    }

                  )


from django.urls import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Order, Payment
import uuid  

def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    amount = order.quantity * order.product.price  


    payment = Payment.objects.create(
        user=request.user,
        order=order,
        amount=amount,
        transaction_id=str(uuid.uuid4()),  
    )

    context = {
        'payment': payment,
        'order': order,
    }
    return render(request, 'payments/initiate_payment.html', context)

def confirm_payment(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id, user=request.user)


    payment.status = 'completed'
    payment.save()

    return redirect('payment_success', payment.id)

def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})