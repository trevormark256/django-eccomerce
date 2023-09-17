from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   # general urls
   path( '' , views.Home, name='home'  ),

   path( 'logout/' ,views.logout_user , name='logout'  ),
   path( 'login/' ,views.login_user , name='login'  ),
   path( 'register/' , views.register_user  , name='register' ),
   path('notallowed/', views.notallowed  , name='notallowed' ),
   path( 'customer/' ,views.customer_home , name='customerhome'  ),
   path( 'Shop/' ,views.Shop , name='Shop'  ),
       # favourites
   path( 'favourites/' ,views.favorite , name='favourites'  ),
   path('add_to_favorites/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
   path('remove_from_favorites/<int:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
        #  cart
   path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/', views.view_cart, name='cart'),
   path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

   path('update_cart/', views.update_cart, name='update_cart'),

   
   path('profile-update/', views.update_profile, name='update_profile'),
   path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),

 path('contact_us/', views.contact_us, name='contact_us'),

 path('store/', views.store, name='store'),
path('update_quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),

path('chart/', views.chart, name='chart'),
 path('checkout/', views.checkout, name='checkout'),
  path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
   path('user_orders/', views.user_orders, name='user_orders'),
   path('order_details/<int:order_id>/', views.order_details, name='order_details'),
   path('order_details_admin/<int:order_id>/', views.order_details_admin, name='order_details_admin'),
   path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

   path('adminprofile/', views.adminprofile, name='adminprofile'),
path('adminprofile-update/', views.adminupdate_profile, name='adminupdate_profile'),  
   path( 'adminhome/' ,views.admin_home , name='adminhome'  ),
   path( 'categories/' ,views.category , name='categories'  ),
   path('product-list/', views.product_list, name='product-list'),   
   path('Users/', views.Users, name='Users'),
   path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
       # URL for creating a new user
   path('users/create/', views.create_user, name='create_user'),
   path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
   path('product/<int:category_id>/delete/', views.delete_product, name='delete_product'),
   path('edit-product/<int:product_id>/', views.edit_product, name='edit-product'),
   path('Orders/', views.Orders, name='Orders'),
   path('orders/update_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
   path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
 path('fetch_cart_items/', views.fetch_cart_items, name='fetch_cart_items'),

   ]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
