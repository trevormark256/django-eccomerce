from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Import the timezone module
from django.db import migrations, models



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Image = models.ImageField(default='profile_pics/userr.svg', upload_to='profile_pics')
    address = models.CharField(max_length=40, null=True)  # Allow null values
    mobile = models.CharField(max_length=20, null=True)


    def __str__(self):
        return f'{self.user} Profile'


class Category(models.Model):
    name= models.CharField(max_length=50,null=False,default='Clothing')

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image1= models.ImageField(upload_to='product_image/',default='product_image/userr.svg')
    product_image2= models.ImageField(upload_to='product_image/',default='product_image/userr.svg')
    created_at = models.DateTimeField(auto_now_add=True  )
    status_choices = [
        ('available', 'Available'),
        ('limited', 'Limited'),
        ('unavailable', 'out of stock '),
    ]
    status = models.CharField(max_length=20, choices=status_choices, null=True)
    product_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.product_quantity <= 0:
            self.status = 'out of stock'
        elif self.product_quantity <= 10:
            self.status = 'limited'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)


class QuantityChangeHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_added = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity_added} added to {self.product.name} by {self.user.username} at {self.timestamp}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link the cart to a user
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link the cart to a product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product in the cart

    def __str__(self):
        return f"Cart item for {self.user.username}: {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2 , null=True )  # Total order amount
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    shipping_address = models.CharField(max_length=100 ,default='kyengera' )
    city = models.CharField(max_length=50 ,default='kampala'  )
    state = models.CharField(max_length=50 ,null=True )
    postal_code = models.CharField(max_length=10 , null=True )
    phone_number = models.CharField(max_length=15, null=True  )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to your Product model
    quantity = models.PositiveIntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2 ,null=True )  # Price per item
    total_price = models.DecimalField(max_digits=10, decimal_places=2 ,null=True )  # Total price for the quantity of this item
   
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


    # ...

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[   (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),])
    comment = models.TextField()
    # ...

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)



