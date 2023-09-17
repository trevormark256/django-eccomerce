# context_processors.py
from .models import Product
from .models import CartItem, Profile
from django.shortcuts import get_object_or_404

def cart_items_count(request):
    cart_items_count = 0
    cart_items = []
    profile = None
    total_price = 0

    if request.user.is_authenticated:
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        profile = get_object_or_404(Profile, user=user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        cart_items_count = cart_items.count()

    return {'cart_items_count': cart_items_count, 'cart_items': cart_items, 'profile': profile, 'total_price': total_price}

def product_notification_count(request):
    limited_count = Product.objects.filter(status='limited').count()
    out_of_stock_count = Product.objects.filter(status='out of stock').count()
    total_count = limited_count + out_of_stock_count   
    return {'product_notification_count': total_count}
