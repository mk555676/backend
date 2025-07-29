# menu_utils.py
from .models import Category, MenuItem, Cart  # Make sure you have these models defined

# C:\backend\myproject\transcribe\menu_utils.py

from .models import MenuItem  # Import your MenuItem model

def get_category_data():
    # Fetch the menu items from the database
    menu_data = {
        "pizza": list(MenuItem.objects.filter(category='Pizza').values('name', 'price')),
        "burgers": list(MenuItem.objects.filter(category='Burgers').values('name', 'price')),
        "pasta": list(MenuItem.objects.filter(category='Pasta').values('name', 'price')),
        "drinks": list(MenuItem.objects.filter(category='Drinks').values('name', 'price')),
    }
    return menu_data


def add_item_to_cart(item_id):
    """
    Add the specified item to the user's cart.
    """
    try:
        item = MenuItem.objects.get(id=item_id)
        # Assuming you have a user authentication system and request.user is available
        cart, created = Cart.objects.get_or_create(user=request.user)  
        cart.items.add(item)
        return True
    except MenuItem.DoesNotExist:
        return False
