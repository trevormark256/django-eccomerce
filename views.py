from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from django.db.models import Sum  # Import the Sum function
from django.http import JsonResponse
from django.views.decorators.http import require_POST  # Import the decorator
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem
from django.shortcuts import render, redirect
from .models import CartItem, Order
from django.shortcuts import get_object_or_404
from .forms import ProfileUpdateForm,editProductForm, OrderForm,OrderSearchForm,ProductForm,CategoryForm
from django.db.models import Q
from django.http import JsonResponse
from .models import Product,Category,Favorite,CartItem,Order,OrderItem,Profile
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from .forms import UserForm
from .decorators import unauthenticated,allowedusers
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.


def Home (request):

    order= Order.objects.all().count()

    return render ( request, 'Home.html',{'order':order}  )


@unauthenticated
def login_user(request):
    page = 'login'
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check if the user has a profile
            try:
                profile = user.profile  # Assuming you have a OneToOneField named 'profile' in your User model
            except Profile.DoesNotExist:
                # User doesn't have a profile, so redirect to the profile update page
                return redirect('update_profile')  # Replace 'update_profile' with the actual URL name for the profile update view
        
            # Check user's group and redirect accordingly
            if user.groups.filter(name='admin').exists():
                return redirect('adminhome')  # Replace 'adminhome' with the actual URL for admin users
        
            elif user.groups.filter(name='customer').exists():
                return redirect('customerhome')  # Replace 'customerhome' with the actual URL for basic users
           
        else:
            messages.error(request, "Login failed. Check your credentials.")
    
    return render(request, 'login_register.html', {'page': page})

@unauthenticated
def register_user(request):
    form = UserForm()
    page = 'register'
   
    if request.method == 'POST':
       form = UserForm(request.POST)  # Pass request.FILES
       if form.is_valid():
           user = form.save(commit=False)  # Create user instance without saving to the database
           user.save()  # Save user to the database
           basic_group, created = Group.objects.get_or_create(name='customer')
           user.groups.add(basic_group)

           # Authenticate the user
           user = authenticate(request, username=user.username, password=request.POST['password1'])
           if user:
                messages.success(request, 'Registration successful. You can now log in.')
                # Redirect to a different page, or use reverse to redirect to a URL
                return redirect('login')  # Redirect to the login page or wherever you want
         
    context = {'form': form, 'page': page} 
    return render(request, 'login_register.html', context)


def logout_user(request):
    logout(request)
    messages.success(request, 'logout successful. ')   
    return redirect('login')

def chart (request):

    return render( request, 'admin/charts.html', {} )

@login_required(login_url='login')
@allowedusers( allowed_roles=['admin'] )
def admin_home(request):
    order= Order.objects.all()
    g_order= Order.objects.filter(status='completed')
    most_ordered_items = OrderItem.objects.values('product__name', 'product__product_image1').annotate(total_ordered=Sum('quantity')).order_by('-total_ordered')

    total_sales = sum(order.total_amount for order in g_order)
  
    context = {'g_order':g_order ,
                'total_sales':total_sales,
                'order':order,
                'most_ordered_items':most_ordered_items,}
    return render ( request , 'admin/Home.html',context )

@login_required(login_url='login')
def customer_home(request):
    
    latest_products = Product.objects.order_by('-created_at')[:4]
    popular_products = Product.objects.order_by('created_at')[:4]

    return render( request , 'customer/home.html', {  'latest_products': latest_products,'popular_products':popular_products})
   

def favorite(request):
    user_favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'customer/Favourites.html', { 'user_favorites': user_favorites, })

def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect('favourites')  # Redirect back to the favorites page

def add_to_favorites(request, product_id):
    product = Product.objects.get(pk=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect('Shop')


def Shop(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    user_favorites = Favorite.objects.filter(user=request.user)
    favorite_product_ids = [favorite.product.id for favorite in user_favorites]

    # Original queryset for products
    original_products = Product.objects.all().order_by('-created_at')

    # Copy the original queryset for further filtering
    products = original_products.all()

    # Get distinct categories for filtering
    categories = Category.objects.all()
    profile = get_object_or_404(Profile, user=request.user)

    # Sorting products
    sort_option = request.GET.get('sort')
    if sort_option == 'alphabetical':
        products = products.order_by('name')
    elif sort_option == 'desc_alphabetical':
        products = products.order_by('-name')

    # Filtering by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)

    # Search form
    search_query = request.GET.get('search_query')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Price range filtering
    # Price range filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
    # Filter products with prices greater than or equal to min_price
       products = products.filter(price__gte=min_price)

    if max_price:
    # Filter products with prices less than or equal to max_price
       products = products.filter(price__lte=max_price)

    if min_price and max_price:
    # Check if max_price is greater than or equal to min_price
        if max_price < min_price:
        # Handle the case where max_price is less than min_price
        # You can set max_price to None or take any other appropriate action
           max_price = None

    context = {
        'products': products,
        'categories': categories,
        'user_favorites': favorite_product_ids,
        'cart_items': cart_items,
        'total_price': total_price,
        'profile': profile
    }

    if request.method == 'POST' and request.is_ajax():
        product_id = request.POST.get('product.id')
        user = request.user

        # Your code to add the product to favorites
        try:
            favorite = Favorite.objects.get_or_create(user=user)[0]
            favorite.products.add(product_id)
            return JsonResponse({'result': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'result': 'error'})

    return render(request, 'Shop.html', context)



@login_required
@require_POST  # Apply the decorator to allow only POST requests
def add_to_cart(request, product_id):
    user = request.user
    product = Product.objects.get(pk=product_id)

    # Create or update the cart item
    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Calculate the updated cart_items_count
    cart_items_count = CartItem.objects.filter(user=user).count()

    return JsonResponse({"success": True, "cart_items_count": cart_items_count})

@login_required
def view_cart(request):
   return render(request,'customer/cart.html',{})
# views.py
from django.http import JsonResponse

def fetch_cart_items(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        # Fetch the cart items and calculate the total price
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Serialize cart items to JSON
    cart_items_data = [
        {
            "product": {
                "name": item.product.name,
                "image_url": item.product.product_image1.url,
                "price": item.product.price,
            }
        }
        for item in cart_items
    ]

    return JsonResponse({"cart_items": cart_items_data, "total_price": total_price})


@login_required
def remove_from_cart(request, cart_item_id):
    item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    
    # Check if the request method is POST to ensure this action is triggered by a form submission.
    if request.method == 'POST':
        item.delete()
    
    return redirect('cart')  # Redirect back to the cart page or wherever you display the cart contents

def update_cart(request):
   
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')

        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            if action == 'increment':
                # Check if the new quantity exceeds the available product quantity
                if cart_item.quantity + 1 <= cart_item.product.product_quantity:
                    cart_item.quantity += 1
                else:
                    message = "Cannot increment. Product quantity limit reached."
           
                    # Optionally, you can display an error message or handle this case differently
                    pass
            elif action == 'decrement':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
            cart_item.save()

        except CartItem.DoesNotExist:
            pass

    referring_url = request.META.get('HTTP_REFERER')
    
    return redirect(referring_url)  # Redirect back to the cart page


def get_cart_count(request):
    if request.user.is_authenticated:
        # Calculate the cart count based on the user's cart items
        cart_count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({"cart_items_count": cart_count})
    else:
        return JsonResponse({"cart_items_count": 0})

def update_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product.product_quantity += quantity
        product.save()
    return redirect('store')


def store(request):
    # Fetch the product data from the database
    products = Product.objects.all()

    total_quantity = Product.objects.aggregate(Sum('product_quantity'))['product_quantity__sum'] or 0


    context = {
        'products': products,
        'total_quantity': total_quantity,

    }

    return render(request, 'admin/store.html', context)


def notifications(request):
    # Get limited and out-of-stock products
    limited_products = Product.objects.filter(status='limited')
    out_of_stock_products = Product.objects.filter(status='out of stock')
    total_out_stock=out_of_stock_products.count()+limited_products.count()

    context = {
        'limited_products': limited_products,
        'out_of_stock_products': out_of_stock_products,
    'total_out_stock':total_out_stock
    }

    return render(request, 'admin/notifications.html', context)


@login_required
def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        # Create an order instance with the required fields
        order_form = OrderForm(request.POST)  # Create the order form from POST data

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.user = user
            order.total_amount = total_price
            order.status = 'Pending'
            order.save()

            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    item_price=cart_item.product.price,  # Set the item price
                    total_price=total_price,  # Set the total price
                )

                # Update the product quantity
                product = cart_item.product
                product.product_quantity -= cart_item.quantity
                product.save()

            # Empty the cart
            cart_items.delete()

            # Redirect to a thank you or confirmation page
            return redirect('order_confirmation', order_id=order.id)
    else:
        order_form = OrderForm(initial={'user': user, 'total_amount': total_price, 'status': 'Pending'})

    context = {
        'order_form': order_form,
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'customer/checkout.html', context)


def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')

    context = {'orders': orders,}
    return render(request, 'customer/user_orders.html', context)

def order_details(request, order_id):
    # Retrieve the order based on the order_id
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # You can also add any other relevant information you want to display
    context = {
    'order': order,
        # Add any other relevant data here
    'order_items': order_items,
    }

    return render(request, 'customer/order_details.html', context)

def order_details_admin(request, order_id):
    # Retrieve the order based on the order_id
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # You can also add any other relevant information you want to display
    context = {
    'order': order,
        # Add any other relevant data here
    'order_items': order_items,
    }

    return render(request, 'admin/order_details.html', context)



@login_required
def order_confirmation(request, order_id):
    # Retrieve the order based on the order_id
    order = get_object_or_404(Order, id=order_id)

    # You can also add any other relevant information you want to display
    context = {
        'order': order,
        # Add any other relevant data here
    }

    return render(request, 'customer/confirmation.html', context)

def Orders(request):
    orders = Order.objects.all()
    search_form = OrderSearchForm(request.GET)
    no_results_message = None  # Initialize no_results_message to None

    if search_form.is_valid():
        search_query = search_form.cleaned_data['search_query']
        # Filter orders by ID or customer name
        orders = orders.filter(
            Q(id__icontains=search_query) | Q(user__username__icontains=search_query)
        )
        
        if not orders.exists():
         no_results_message = "No results found for your search query."
    else:
            # If search query is empty, show all orders
            orders = Order.objects.all()
   
    return render(request, 'admin/Order.html', {'orders': orders, 'search_form': search_form,'no_results_message':no_results_message})

def update_order_status(request, order_id):
    if request.method == 'POST':
        # Get the selected new status from the form data
        new_status = request.POST.get('new_status')
        
        try:
            # Retrieve the order by its ID
            order = Order.objects.get(pk=order_id)
            
            # Update the order status
            order.status = new_status
            order.save()
            
            # Optionally, you can add a success message
            messages.success(request, f'Order #{order_id} status updated to {new_status}.')
            
        except Order.DoesNotExist:
            # Handle the case where the order with the given ID does not exist
            messages.error(request, f'Order #{order_id} does not exist.')
    
    # Redirect back to the order list page
    return redirect('Orders')  # Replace 'order_list' with the URL name of your order list page

def delete_order(request, order_id):
    # Fetch the order to be deleted
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Check if the user confirms the deletion
       
        order.delete()
        return redirect('Orders')  # Redirect to your order list page
    else:
       
           
       return redirect('Orders')  #

def profile(request):
    user = request.user
   
    return render(request, 'customer/profile.html', { })

def adminprofile(request):
    user = request.user
   
    return render(request, 'admin/profile.html', { })

def update_profile(request):

    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    profile = get_object_or_404(Profile, user=request.user)

    
    try:
        # Get the current user's profile if it exists
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Handle the case where the user doesn't have a profile
        profile = None

    if request.method == 'POST':
        if profile:
            # Populate the form with the current profile data and the updated data from the POST request
            form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        else:
            # If the user doesn't have a profile, create a new one
            form = ProfileUpdateForm(request.POST, request.FILES)
        
        if form.is_valid():
            if profile:
                form.save()
            else:
                # Create a new profile for the user
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
            
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        # If it's a GET request, initialize the form with the current profile data if it exists
        form = ProfileUpdateForm(instance=profile)
  
    return render(request, 'customer/profile_update.html', {'form': form,'profile':profile, 'total_price':total_price})

def adminupdate_profile(request):

    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    profile = get_object_or_404(Profile, user=request.user)

    
    try:
        # Get the current user's profile if it exists
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Handle the case where the user doesn't have a profile
        profile = None

    if request.method == 'POST':
        if profile:
            # Populate the form with the current profile data and the updated data from the POST request
            form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        else:
            # If the user doesn't have a profile, create a new one
            form = ProfileUpdateForm(request.POST, request.FILES)
        
        if form.is_valid():
            if profile:
                form.save()
            else:
                # Create a new profile for the user
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
            
            return redirect('adminprofile')  # Redirect to the profile page after successful update
    else:
        # If it's a GET request, initialize the form with the current profile data if it exists
        form = ProfileUpdateForm(instance=profile)
  
    return render(request, 'admin/profile_update.html', {'form': form,'profile':profile, 'total_price':total_price})

@login_required(login_url='login')
def notallowed(request):
    return render( request ,'notallowed.html',{} )


login_required(login_url='login')
def product_list(request):
    countable=Product.objects.all().count 
    products = Product.objects.all().order_by('-created_at')
   
    
    # Product form handling
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully')  
            return redirect('product-list')
    else:
        form = ProductForm()

    # Category form handling
   
    search_query = request.GET.get('search_query')
    if search_query:
        products = products.filter(Q(name__icontains=search_query))
    else:
        products = Product.objects.all()
    
    products = list(reversed(products))
   

   
    
    return render(request, 'admin/product_list.html', {'products': products, 'form': form,'category': category,'countable':countable })


def contact_us(request):
    messo = None
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '')
        customer_email = request.POST.get('customer_email', '')
        message = request.POST.get('message', '')
        
        if customer_email and '@' in customer_email:
            try:
                subject = f"Email from {customer_name} ({customer_email})"
                email_message = f"Customer Name: {customer_name}\n"
                email_message += f"Customer Email: {customer_email}\n\nMessage:\n{message}"
                
                send_mail(subject, email_message, customer_email, [settings.EMAIL_HOST_USER], fail_silently=False)
                messo = 'sent successfully'
            except Exception as e:
                messo = 'failed'
    
    return render(request, 'customer/contact.html', {'messo': messo})

def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = editProductForm(request.POST, request.FILES, instance=product)

        # Check if it's an edit operation and disable the 'product_quantity' field if it is
        if product_id:
            form.fields['product_quantity'].widget.attrs['disabled'] = 'disabled'

        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect('product-list')
    else:
        form = editProductForm(instance=product)

    return render(request, 'admin/edit_product.html', {'form': form, 'product': product})

def Users(request):
    users = User.objects.all()  # Get all users
    query = request.GET.get('q')  # Get the search query from the URL
    
    if query:
        # If a search query is provided, filter the users based on the query
        users = users.filter(
            Q(username__icontains=query) |  # Search by username (case-insensitive)
            Q(email__icontains=query)       # Search by email (case-insensitive)
        )
    return render(request, 'admin/Users.html', {'users': users})


def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Update user attributes based on form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_group = request.POST.get('user_group')

        user.username = username
        user.email = email
        if password:
            user.set_password(password)  # Update the password securely
        user.save()

        # Update user group
        if user_group in ['customer', 'admin']:
            group = Group.objects.get(name=user_group)
            user.groups.clear()  # Remove existing groups
            user.groups.add(group)
            messages.success(request,'Update successful.')
            return redirect('Users')
    # If the user_group condition is not met or it's a GET request
    return render(request, 'admin/edit_user.html', {'user': user})


def delete_user(request, user_id):
    # Fetch the user to delete
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Check if the user is authenticated and has the permission to delete
        if request.user.is_authenticated and request.user.has_perm('auth.delete_user'):
            # Delete the user
            user.delete()
            messages.success(request, 'User deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this user.')

    return redirect('Users')
  
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)  # Use your custom form
        if form.is_valid():
            # Create a new user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_role = form.cleaned_data['user_role']

          
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # Handle user group
            if user_role == 'admin':
                group = Group.objects.get(name='admin')
            else:
                group = Group.objects.get(name='customer')
            

            user.groups.add(group)
            messages.success(request, 'User created successfully.')
            return redirect('Users')
    else:
        form = UserForm()  # Create an empty form

    return render(request, 'admin/create_user.html', {'form': form})

def category(request):
    category = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully')  
            return redirect('product_list')
    else:
        form = CategoryForm()

    return render ( request,'admin/category.html', {'category':category,'form':form } )

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('product-list')

    return render(request, 'admin/delete_category.html', {'category': category})

def delete_product(request, category_id):
    product = get_object_or_404(Product, id=category_id)

    if request.method == 'POST':
        product.delete()
        return redirect('product-list')

    return render(request, 'admin/delete_product.html', {'product': product})
