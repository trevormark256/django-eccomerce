
from django import forms
from .models import Product
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Profile,Category,Order

class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your first name.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')


    USER_ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        
    )
    
    user_role = forms.ChoiceField(choices=USER_ROLE_CHOICES,
            label=("User role"),
            required=True,
            initial="customer"  # Set the default value to "customer"
   
                         )


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'user_role']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email', 'required': True})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['user_role'].widget.attrs.update({ 'class':'form-control form-select ', })

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'address'})
        self.fields['mobile'].widget.attrs.update({'class': 'form-control ', 'placeholder': 'mobile'})
        self.fields['Image'].widget.attrs.update({'class': 'form-control mt-2 d-flex', 'placeholder': 'add image'})


class ProductSearchForm(forms.Form):
    search_query = forms.CharField(label='Search by Name', max_length=100)



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # You can specify the fields you want to include
        exclude = ['status']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control' })
        self.fields['category'].queryset = Category.objects.all() 
         # Include all available categories
        self.fields['product_quantity'].widget.attrs.update({'class':'form-control'})
    def clean_product_image1(self):
        product_image1 = self.cleaned_data.get('product_image1')
        if product_image1:
            # If a new image is provided, return it
            return product_image1
        else:
            # If no new image is provided, return the existing one
            return self.instance.product_image1


    def clean_product_image2(self):
        product_image2 = self.cleaned_data.get('product_image2')
        if product_image2:
            # If a new image is provided, return it
            return product_image2
        else:
            # If no new image is provided, return the existing one
            return self.instance.product_image2


         
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'  # You can specify the fields you want to include
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
       # Include all available categories


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ 'total_amount', 'status', 'shipping_address', 'city', 'state', 'postal_code', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
       
        self.fields['total_amount'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True
        

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Add the 'form-control' class to all fields

        # Optionally, you can add placeholders to the fields
        self.fields['shipping_address'].widget.attrs['placeholder'] = 'Shipping Address'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['postal_code'].widget.attrs['placeholder'] = 'Postal Code'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'

    def clean_user(self):
        # Ensure the user remains the currently logged-in user
        return self.instance.user
    
class OrderSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label='Search by Order ID or Customer Name',
        widget=forms.TextInput(attrs={'class': 'form-control text-center ', 'placeholder':'search by Order ID or cutomer name ......'}),
    )



    
class editProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # You can specify the fields you want to include
        exclude = ['status']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control' })
        self.fields['product_quantity'].widget.attrs.update({'class': 'form-control' })
        self.fields['category'].queryset = Category.objects.all() 
         # Include all available categories
        self.fields['product_quantity'].widget.attrs['disabled'] = 'disabled'
    def clean_product_image1(self):
        product_image1 = self.cleaned_data.get('product_image1')
        if product_image1:
            # If a new image is provided, return it
            return product_image1
        else:
            # If no new image is provided, return the existing one
            return self.instance.product_image1


    def clean_product_image2(self):
        product_image2 = self.cleaned_data.get('product_image2')
        if product_image2:
            # If a new image is provided, return it
            return product_image2
        else:
            # If no new image is provided, return the existing one
            return self.instance.product_image2

