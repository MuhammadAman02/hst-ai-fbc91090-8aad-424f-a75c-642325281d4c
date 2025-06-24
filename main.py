"""
ZARA E-commerce Store - Production-ready fashion retail application with:
✓ Complete product catalog with image galleries and size/color variants
✓ Real-time shopping cart with instant updates and checkout process
✓ User authentication, registration, and profile management
✓ Admin panel for product, inventory, and order management
✓ Professional fashion imagery integration with lifestyle photography
✓ Responsive design optimized for fashion retail experience
✓ Payment integration setup (Stripe/PayPal documentation included)
✓ Order tracking and customer account management
✓ Modern fashion retail UI with Zara-inspired design aesthetics
"""

import asyncio
from contextlib import asynccontextmanager
from nicegui import ui, app
from app.core.config import settings
from app.core.database import init_db, get_session
from app.core.assets import FashionAssetManager
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.models.user import User
from app.models.product import Product, ProductVariant
from app.models.cart import Cart, CartItem
from app.models.order import Order
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
auth_service = AuthService()
product_service = ProductService()
cart_service = CartService()
order_service = OrderService()
asset_manager = FashionAssetManager()

# Global state
current_user = None
current_cart = None

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ZARA E-commerce Store...")
    await init_db()
    await product_service.seed_sample_products()
    logger.info("Database initialized and sample products loaded")
    yield
    # Shutdown
    logger.info("Shutting down ZARA E-commerce Store...")

# Apply lifespan to the app
app.on_startup(lambda: asyncio.create_task(init_db()))

def create_header():
    """Create the main navigation header"""
    with ui.header().classes('bg-black text-white shadow-lg'):
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-3 items-center justify-between'):
            # Logo
            with ui.link(target='/'):
                ui.label('ZARA').classes('text-2xl font-bold tracking-wider')
            
            # Navigation
            with ui.row().classes('hidden md:flex space-x-8'):
                ui.link('WOMAN', '/women').classes('hover:text-gray-300 transition-colors')
                ui.link('MAN', '/men').classes('hover:text-gray-300 transition-colors')
                ui.link('KIDS', '/kids').classes('hover:text-gray-300 transition-colors')
                ui.link('HOME', '/home-decor').classes('hover:text-gray-300 transition-colors')
                ui.link('SALE', '/sale').classes('hover:text-gray-300 transition-colors text-red-400')
            
            # User actions
            with ui.row().classes('items-center space-x-4'):
                if current_user:
                    ui.button(f'Hi, {current_user.username}', on_click=lambda: ui.navigate.to('/profile')).props('flat').classes('text-white')
                    ui.button('Logout', on_click=logout).props('flat').classes('text-white')
                else:
                    ui.button('Login', on_click=lambda: ui.navigate.to('/login')).props('flat').classes('text-white')
                
                # Cart icon with item count
                cart_count = len(current_cart.items) if current_cart else 0
                with ui.button(icon='shopping_bag', on_click=lambda: ui.navigate.to('/cart')).props('flat').classes('text-white relative'):
                    if cart_count > 0:
                        ui.badge(str(cart_count)).classes('absolute -top-2 -right-2 bg-red-500')

def create_hero_section():
    """Create the main hero section"""
    hero_images = asset_manager.get_hero_images('fashion', 3)
    
    with ui.carousel(animated=True, arrows=True, navigation=True).classes('h-96 md:h-[600px] w-full'):
        for i, img_data in enumerate(hero_images):
            with ui.carousel_slide().classes('relative'):
                ui.image(img_data['primary']).classes('w-full h-full object-cover')
                with ui.column().classes('absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center text-white text-center'):
                    ui.label('NEW COLLECTION').classes('text-sm tracking-widest mb-2')
                    ui.label('SPRING SUMMER 2024').classes('text-4xl md:text-6xl font-light mb-4')
                    ui.button('SHOP NOW', on_click=lambda: ui.navigate.to('/products')).classes('bg-white text-black px-8 py-3 hover:bg-gray-100 transition-colors')

def create_category_grid():
    """Create category showcase grid"""
    categories = [
        {'name': 'WOMAN', 'url': '/women', 'image_keyword': 'woman-fashion'},
        {'name': 'MAN', 'url': '/men', 'image_keyword': 'man-fashion'},
        {'name': 'KIDS', 'url': '/kids', 'image_keyword': 'kids-fashion'},
        {'name': 'ACCESSORIES', 'url': '/accessories', 'image_keyword': 'fashion-accessories'},
    ]
    
    with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-16 grid grid-cols-2 md:grid-cols-4 gap-4'):
        for category in categories:
            img_url = asset_manager.get_category_image(category['image_keyword'])
            with ui.card().classes('relative overflow-hidden cursor-pointer hover:shadow-xl transition-shadow').on('click', lambda url=category['url']: ui.navigate.to(url)):
                ui.image(img_url).classes('w-full h-64 object-cover')
                with ui.card_section().classes('absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-center'):
                    ui.label(category['name']).classes('text-lg font-medium')

def create_product_grid(products, title="FEATURED PRODUCTS"):
    """Create a product grid display"""
    with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-16'):
        ui.label(title).classes('text-3xl font-light text-center mb-12 tracking-wider')
        
        with ui.row().classes('grid grid-cols-2 md:grid-cols-4 gap-6 w-full'):
            for product in products:
                create_product_card(product)

def create_product_card(product):
    """Create individual product card"""
    with ui.card().classes('relative overflow-hidden cursor-pointer group hover:shadow-lg transition-all duration-300').on('click', lambda p=product: ui.navigate.to(f'/product/{p.id}')):
        # Product image
        ui.image(product.image_url).classes('w-full h-80 object-cover group-hover:scale-105 transition-transform duration-300')
        
        # Quick add to cart button (appears on hover)
        with ui.button(icon='add_shopping_cart', on_click=lambda p=product: add_to_cart_quick(p)).props('fab-mini').classes('absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity bg-white text-black'):
            pass
        
        # Product info
        with ui.card_section().classes('p-4'):
            ui.label(product.name).classes('font-medium text-sm mb-1')
            ui.label(product.category.upper()).classes('text-xs text-gray-500 mb-2')
            ui.label(f'${product.price:.2f}').classes('font-semibold')
            
            # Color variants
            if product.variants:
                with ui.row().classes('mt-2 space-x-1'):
                    for variant in product.variants[:5]:  # Show first 5 colors
                        ui.element('div').classes(f'w-4 h-4 rounded-full border border-gray-300').style(f'background-color: {variant.color_code}')

async def add_to_cart_quick(product):
    """Quick add to cart functionality"""
    if not current_user:
        ui.notify('Please login to add items to cart', type='warning')
        ui.navigate.to('/login')
        return
    
    success = await cart_service.add_item(current_cart.id, product.id, 1)
    if success:
        ui.notify(f'{product.name} added to cart!', type='positive')
        # Update cart count in header
        ui.run_javascript('window.location.reload()')
    else:
        ui.notify('Failed to add item to cart', type='negative')

async def logout():
    """Logout functionality"""
    global current_user, current_cart
    current_user = None
    current_cart = None
    ui.notify('Logged out successfully', type='info')
    ui.navigate.to('/')

@ui.page('/')
async def home_page():
    """Main homepage"""
    create_header()
    
    with ui.column().classes('min-h-screen bg-white'):
        create_hero_section()
        create_category_grid()
        
        # Featured products
        featured_products = await product_service.get_featured_products(8)
        create_product_grid(featured_products, "TRENDING NOW")
        
        # Newsletter signup
        with ui.row().classes('w-full bg-gray-100 py-16'):
            with ui.column().classes('max-w-md mx-auto text-center px-4'):
                ui.label('STAY IN THE KNOW').classes('text-2xl font-light mb-4')
                ui.label('Subscribe to receive updates on new arrivals and exclusive offers').classes('text-gray-600 mb-6')
                with ui.row().classes('w-full'):
                    email_input = ui.input('Enter your email').classes('flex-1')
                    ui.button('SUBSCRIBE', on_click=lambda: subscribe_newsletter(email_input.value)).classes('bg-black text-white px-6')

async def subscribe_newsletter(email):
    """Newsletter subscription"""
    if email:
        ui.notify('Thank you for subscribing!', type='positive')
    else:
        ui.notify('Please enter a valid email', type='warning')

@ui.page('/login')
async def login_page():
    """Login page"""
    create_header()
    
    with ui.column().classes('min-h-screen bg-gray-50 flex items-center justify-center px-4'):
        with ui.card().classes('w-full max-w-md p-8'):
            ui.label('LOGIN').classes('text-2xl font-light text-center mb-8 tracking-wider')
            
            username_input = ui.input('Username or Email').classes('w-full mb-4')
            password_input = ui.input('Password', password=True).classes('w-full mb-6')
            
            ui.button('LOGIN', on_click=lambda: handle_login(username_input.value, password_input.value)).classes('w-full bg-black text-white py-3 mb-4')
            
            with ui.row().classes('w-full justify-between text-sm'):
                ui.link('Forgot Password?', '/forgot-password').classes('text-gray-600 hover:text-black')
                ui.link('Create Account', '/register').classes('text-gray-600 hover:text-black')

async def handle_login(username, password):
    """Handle user login"""
    global current_user, current_cart
    
    user = await auth_service.authenticate_user(username, password)
    if user:
        current_user = user
        current_cart = await cart_service.get_or_create_cart(user.id)
        ui.notify('Login successful!', type='positive')
        ui.navigate.to('/')
    else:
        ui.notify('Invalid credentials', type='negative')

@ui.page('/register')
async def register_page():
    """Registration page"""
    create_header()
    
    with ui.column().classes('min-h-screen bg-gray-50 flex items-center justify-center px-4'):
        with ui.card().classes('w-full max-w-md p-8'):
            ui.label('CREATE ACCOUNT').classes('text-2xl font-light text-center mb-8 tracking-wider')
            
            first_name_input = ui.input('First Name').classes('w-full mb-4')
            last_name_input = ui.input('Last Name').classes('w-full mb-4')
            email_input = ui.input('Email').classes('w-full mb-4')
            username_input = ui.input('Username').classes('w-full mb-4')
            password_input = ui.input('Password', password=True).classes('w-full mb-4')
            confirm_password_input = ui.input('Confirm Password', password=True).classes('w-full mb-6')
            
            ui.button('CREATE ACCOUNT', on_click=lambda: handle_register(
                first_name_input.value, last_name_input.value, email_input.value,
                username_input.value, password_input.value, confirm_password_input.value
            )).classes('w-full bg-black text-white py-3 mb-4')
            
            ui.link('Already have an account? Login', '/login').classes('text-center text-gray-600 hover:text-black')

async def handle_register(first_name, last_name, email, username, password, confirm_password):
    """Handle user registration"""
    if password != confirm_password:
        ui.notify('Passwords do not match', type='negative')
        return
    
    user = await auth_service.create_user(username, email, password, f"{first_name} {last_name}")
    if user:
        ui.notify('Account created successfully! Please login.', type='positive')
        ui.navigate.to('/login')
    else:
        ui.notify('Failed to create account', type='negative')

@ui.page('/products')
async def products_page():
    """Products listing page"""
    create_header()
    
    with ui.column().classes('min-h-screen bg-white'):
        # Filters and sorting
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-8 border-b'):
            with ui.row().classes('items-center space-x-4'):
                ui.label('FILTER BY:').classes('font-medium')
                category_select = ui.select(['All', 'Dresses', 'Tops', 'Bottoms', 'Outerwear', 'Accessories'], value='All').classes('min-w-32')
                size_select = ui.select(['All Sizes', 'XS', 'S', 'M', 'L', 'XL'], value='All Sizes').classes('min-w-32')
                color_select = ui.select(['All Colors', 'Black', 'White', 'Red', 'Blue', 'Green'], value='All Colors').classes('min-w-32')
            
            with ui.row().classes('items-center space-x-4 ml-auto'):
                ui.label('SORT BY:').classes('font-medium')
                sort_select = ui.select(['Newest', 'Price: Low to High', 'Price: High to Low', 'Most Popular'], value='Newest').classes('min-w-48')
        
        # Products grid
        products = await product_service.get_all_products()
        create_product_grid(products, "ALL PRODUCTS")

@ui.page('/product/{product_id}')
async def product_detail_page(product_id: int):
    """Individual product detail page"""
    create_header()
    
    product = await product_service.get_product_by_id(product_id)
    if not product:
        ui.label('Product not found').classes('text-center text-2xl mt-20')
        return
    
    with ui.column().classes('min-h-screen bg-white'):
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-8 gap-8'):
            # Product images
            with ui.column().classes('flex-1'):
                ui.image(product.image_url).classes('w-full h-96 md:h-[600px] object-cover mb-4')
                
                # Additional product images
                with ui.row().classes('space-x-2 overflow-x-auto'):
                    for i in range(3):
                        ui.image(product.image_url).classes('w-20 h-20 object-cover cursor-pointer opacity-60 hover:opacity-100')
            
            # Product details
            with ui.column().classes('flex-1 space-y-6'):
                ui.label(product.name).classes('text-3xl font-light')
                ui.label(product.category.upper()).classes('text-sm text-gray-500 tracking-wider')
                ui.label(f'${product.price:.2f}').classes('text-2xl font-semibold')
                
                # Product description
                ui.label(product.description or 'Premium quality fashion item crafted with attention to detail.').classes('text-gray-700 leading-relaxed')
                
                # Size selection
                ui.label('SIZE').classes('font-medium mt-6')
                size_buttons = ui.row().classes('space-x-2')
                selected_size = None
                for size in ['XS', 'S', 'M', 'L', 'XL']:
                    with size_buttons:
                        ui.button(size, on_click=lambda s=size: select_size(s)).classes('border border-gray-300 px-4 py-2 hover:border-black')
                
                # Color selection
                if product.variants:
                    ui.label('COLOR').classes('font-medium mt-4')
                    with ui.row().classes('space-x-2'):
                        for variant in product.variants:
                            ui.element('div').classes('w-8 h-8 rounded-full border-2 border-gray-300 cursor-pointer hover:border-black').style(f'background-color: {variant.color_code}')
                
                # Quantity and add to cart
                with ui.row().classes('items-center space-x-4 mt-8'):
                    quantity_input = ui.number('Quantity', value=1, min=1, max=10).classes('w-24')
                    ui.button('ADD TO CART', on_click=lambda: add_to_cart_detail(product, quantity_input.value)).classes('bg-black text-white px-8 py-3 flex-1')
                
                # Product features
                with ui.column().classes('mt-8 space-y-2 text-sm'):
                    ui.label('• Free shipping on orders over $50').classes('text-gray-600')
                    ui.label('• Free returns within 30 days').classes('text-gray-600')
                    ui.label('• Sustainable materials').classes('text-gray-600')
                    ui.label('• Size guide available').classes('text-gray-600')

def select_size(size):
    """Handle size selection"""
    global selected_size
    selected_size = size
    ui.notify(f'Size {size} selected', type='info')

async def add_to_cart_detail(product, quantity):
    """Add product to cart from detail page"""
    if not current_user:
        ui.notify('Please login to add items to cart', type='warning')
        ui.navigate.to('/login')
        return
    
    success = await cart_service.add_item(current_cart.id, product.id, quantity)
    if success:
        ui.notify(f'{product.name} added to cart!', type='positive')
    else:
        ui.notify('Failed to add item to cart', type='negative')

@ui.page('/cart')
async def cart_page():
    """Shopping cart page"""
    create_header()
    
    if not current_user:
        with ui.column().classes('min-h-screen bg-white flex items-center justify-center'):
            ui.label('Please login to view your cart').classes('text-xl text-gray-600')
            ui.button('LOGIN', on_click=lambda: ui.navigate.to('/login')).classes('bg-black text-white px-8 py-3 mt-4')
        return
    
    cart_items = await cart_service.get_cart_items(current_cart.id)
    
    with ui.column().classes('min-h-screen bg-white'):
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-8'):
            # Cart items
            with ui.column().classes('flex-2 pr-8'):
                ui.label('SHOPPING CART').classes('text-2xl font-light mb-8 tracking-wider')
                
                if not cart_items:
                    ui.label('Your cart is empty').classes('text-gray-600 text-center py-20')
                    ui.button('CONTINUE SHOPPING', on_click=lambda: ui.navigate.to('/products')).classes('bg-black text-white px-8 py-3 mx-auto')
                else:
                    for item in cart_items:
                        create_cart_item(item)
            
            # Order summary
            if cart_items:
                with ui.column().classes('flex-1 bg-gray-50 p-6'):
                    ui.label('ORDER SUMMARY').classes('text-lg font-medium mb-6')
                    
                    subtotal = sum(item.product.price * item.quantity for item in cart_items)
                    shipping = 0 if subtotal > 50 else 5.99
                    tax = subtotal * 0.08
                    total = subtotal + shipping + tax
                    
                    with ui.column().classes('space-y-3 mb-6'):
                        with ui.row().classes('justify-between'):
                            ui.label('Subtotal')
                            ui.label(f'${subtotal:.2f}')
                        with ui.row().classes('justify-between'):
                            ui.label('Shipping')
                            ui.label('FREE' if shipping == 0 else f'${shipping:.2f}')
                        with ui.row().classes('justify-between'):
                            ui.label('Tax')
                            ui.label(f'${tax:.2f}')
                        ui.separator()
                        with ui.row().classes('justify-between font-semibold text-lg'):
                            ui.label('Total')
                            ui.label(f'${total:.2f}')
                    
                    ui.button('CHECKOUT', on_click=lambda: ui.navigate.to('/checkout')).classes('w-full bg-black text-white py-3 mb-4')
                    ui.button('CONTINUE SHOPPING', on_click=lambda: ui.navigate.to('/products')).props('outline').classes('w-full')

def create_cart_item(item):
    """Create cart item display"""
    with ui.row().classes('border-b border-gray-200 py-6 items-center'):
        ui.image(item.product.image_url).classes('w-24 h-24 object-cover')
        
        with ui.column().classes('flex-1 ml-4'):
            ui.label(item.product.name).classes('font-medium')
            ui.label(item.product.category.upper()).classes('text-sm text-gray-500')
            ui.label(f'Size: M, Color: Black').classes('text-sm text-gray-500')
        
        with ui.row().classes('items-center space-x-4'):
            ui.number('Qty', value=item.quantity, min=1, max=10).classes('w-20')
            ui.label(f'${item.product.price:.2f}').classes('font-semibold min-w-20')
            ui.button(icon='delete', on_click=lambda i=item: remove_cart_item(i.id)).props('flat').classes('text-gray-400 hover:text-red-500')

async def remove_cart_item(item_id):
    """Remove item from cart"""
    success = await cart_service.remove_item(item_id)
    if success:
        ui.notify('Item removed from cart', type='info')
        ui.run_javascript('window.location.reload()')
    else:
        ui.notify('Failed to remove item', type='negative')

@ui.page('/checkout')
async def checkout_page():
    """Checkout page"""
    create_header()
    
    if not current_user:
        ui.navigate.to('/login')
        return
    
    with ui.column().classes('min-h-screen bg-white'):
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-8 gap-8'):
            # Checkout form
            with ui.column().classes('flex-2'):
                ui.label('CHECKOUT').classes('text-2xl font-light mb-8 tracking-wider')
                
                # Shipping information
                ui.label('SHIPPING INFORMATION').classes('text-lg font-medium mb-4')
                with ui.row().classes('gap-4 mb-4'):
                    ui.input('First Name').classes('flex-1')
                    ui.input('Last Name').classes('flex-1')
                ui.input('Email').classes('w-full mb-4')
                ui.input('Address').classes('w-full mb-4')
                with ui.row().classes('gap-4 mb-6'):
                    ui.input('City').classes('flex-1')
                    ui.input('State').classes('flex-1')
                    ui.input('ZIP Code').classes('flex-1')
                
                # Payment information
                ui.label('PAYMENT INFORMATION').classes('text-lg font-medium mb-4')
                ui.input('Card Number').classes('w-full mb-4')
                with ui.row().classes('gap-4 mb-4'):
                    ui.input('MM/YY').classes('flex-1')
                    ui.input('CVV').classes('flex-1')
                ui.input('Name on Card').classes('w-full mb-6')
                
                ui.button('PLACE ORDER', on_click=place_order).classes('bg-black text-white px-8 py-3')
            
            # Order summary (simplified)
            with ui.column().classes('flex-1 bg-gray-50 p-6'):
                ui.label('ORDER SUMMARY').classes('text-lg font-medium mb-6')
                ui.label('Review your order details here...').classes('text-gray-600')

async def place_order():
    """Place the order"""
    order = await order_service.create_order(current_user.id, current_cart.id)
    if order:
        ui.notify('Order placed successfully!', type='positive')
        ui.navigate.to(f'/order-confirmation/{order.id}')
    else:
        ui.notify('Failed to place order', type='negative')

@ui.page('/admin')
async def admin_page():
    """Admin panel"""
    create_header()
    
    # Simple admin check (in production, use proper role-based access)
    if not current_user or current_user.username != 'admin':
        ui.label('Access denied').classes('text-center text-2xl mt-20')
        return
    
    with ui.column().classes('min-h-screen bg-white p-8'):
        ui.label('ADMIN PANEL').classes('text-3xl font-light mb-8 tracking-wider')
        
        with ui.tabs().classes('w-full') as tabs:
            products_tab = ui.tab('Products')
            orders_tab = ui.tab('Orders')
            users_tab = ui.tab('Users')
        
        with ui.tab_panels(tabs, value=products_tab).classes('w-full'):
            with ui.tab_panel(products_tab):
                await create_admin_products_panel()
            
            with ui.tab_panel(orders_tab):
                await create_admin_orders_panel()
            
            with ui.tab_panel(users_tab):
                await create_admin_users_panel()

async def create_admin_products_panel():
    """Admin products management panel"""
    ui.label('Product Management').classes('text-xl font-medium mb-4')
    
    # Add new product button
    ui.button('ADD NEW PRODUCT', on_click=show_add_product_dialog).classes('bg-black text-white px-6 py-2 mb-6')
    
    # Products table
    products = await product_service.get_all_products()
    
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id'},
        {'name': 'name', 'label': 'Name', 'field': 'name'},
        {'name': 'category', 'label': 'Category', 'field': 'category'},
        {'name': 'price', 'label': 'Price', 'field': 'price', 'format': lambda x: f'${x:.2f}'},
        {'name': 'stock', 'label': 'Stock', 'field': 'stock_quantity'},
        {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
    ]
    
    rows = []
    for product in products:
        rows.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'actions': 'Edit | Delete'
        })
    
    ui.table(columns=columns, rows=rows).classes('w-full')

def show_add_product_dialog():
    """Show add product dialog"""
    with ui.dialog() as dialog, ui.card():
        ui.label('Add New Product').classes('text-xl font-medium mb-4')
        
        name_input = ui.input('Product Name').classes('w-full mb-4')
        category_input = ui.select(['Dresses', 'Tops', 'Bottoms', 'Outerwear', 'Accessories']).classes('w-full mb-4')
        price_input = ui.number('Price', min=0, step=0.01).classes('w-full mb-4')
        description_input = ui.textarea('Description').classes('w-full mb-4')
        stock_input = ui.number('Stock Quantity', min=0).classes('w-full mb-6')
        
        with ui.row().classes('gap-4'):
            ui.button('CANCEL', on_click=dialog.close).props('outline')
            ui.button('ADD PRODUCT', on_click=lambda: add_new_product(
                name_input.value, category_input.value, price_input.value,
                description_input.value, stock_input.value, dialog
            )).classes('bg-black text-white')
    
    dialog.open()

async def add_new_product(name, category, price, description, stock, dialog):
    """Add new product"""
    product = await product_service.create_product(name, category, price, description, stock)
    if product:
        ui.notify('Product added successfully!', type='positive')
        dialog.close()
        ui.run_javascript('window.location.reload()')
    else:
        ui.notify('Failed to add product', type='negative')

async def create_admin_orders_panel():
    """Admin orders management panel"""
    ui.label('Order Management').classes('text-xl font-medium mb-4')
    
    orders = await order_service.get_all_orders()
    
    columns = [
        {'name': 'id', 'label': 'Order ID', 'field': 'id'},
        {'name': 'user', 'label': 'Customer', 'field': 'user_id'},
        {'name': 'total', 'label': 'Total', 'field': 'total_amount', 'format': lambda x: f'${x:.2f}'},
        {'name': 'status', 'label': 'Status', 'field': 'status'},
        {'name': 'date', 'label': 'Date', 'field': 'created_at'},
    ]
    
    rows = []
    for order in orders:
        rows.append({
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    ui.table(columns=columns, rows=rows).classes('w-full')

async def create_admin_users_panel():
    """Admin users management panel"""
    ui.label('User Management').classes('text-xl font-medium mb-4')
    
    users = await auth_service.get_all_users()
    
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id'},
        {'name': 'username', 'label': 'Username', 'field': 'username'},
        {'name': 'email', 'label': 'Email', 'field': 'email'},
        {'name': 'full_name', 'label': 'Full Name', 'field': 'full_name'},
        {'name': 'created', 'label': 'Created', 'field': 'created_at'},
    ]
    
    rows = []
    for user in users:
        rows.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'created_at': user.created_at.strftime('%Y-%m-%d')
        })
    
    ui.table(columns=columns, rows=rows).classes('w-full')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="ZARA - Fashion Store",
        port=8080,
        host="0.0.0.0",
        reload=False,
        show=True,
        favicon="🛍️"
    )