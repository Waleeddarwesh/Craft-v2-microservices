import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

# Import Models
from accounts.models import User, Customer, Supplier, Delivery
from products.models import Category, MatCategory, Product
from orders.models import Order, OrderItem, Shipment, Warehouse
from payment.models import PaymentHistory
from reviews.models import Review
from support_tickets.models import Ticket, TicketMessage
from disputes.models import Dispute
from notifications.models import Notification
from returnrequest.models import Transaction

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data for the Craft ecosystem'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database seed... this may take a moment."))

        self._seed_users()
        self._seed_categories()
        self._seed_products()
        self._seed_warehouses()
        self._seed_orders_and_returns()
        self._seed_reviews()
        self._seed_tickets_and_disputes()

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Database successfully seeded with demo data!"))

    def _seed_users(self):
        self.stdout.write("- Seeding Users...")
        # Create Admin
        if not User.objects.filter(email='admin@craft.com').exists():
            admin = User.objects.create_superuser(
                email='admin@craft.com', password='craftpassword123',
                first_name='System', last_name='Admin', is_verified=True
            )
            self.admin_user = admin
        else:
            self.admin_user = User.objects.get(email='admin@craft.com')

        # Create Finance/Support (using permissions later, for now just staff)
        if not User.objects.filter(email='support@craft.com').exists():
            self.support_user = User.objects.create_user(
                email='support@craft.com', password='craftpassword123',
                first_name='Support', last_name='Agent', is_verified=True, is_staff=True
            )
        else:
            self.support_user = User.objects.get(email='support@craft.com')

        # Create Suppliers
        self.suppliers = []
        for i in range(1, 6):
            email = f'supplier{i}@craft.com'
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(
                    email=email, password='craftpassword123',
                    first_name=f'Supplier', last_name=f'{i}', is_supplier=True, is_verified=True
                )
                sup = Supplier.objects.create(
                    user=u, CategoryTitle=f'Craft Category {i}', Orders=random.randint(10, 500)
                )
                self.suppliers.append(sup)
            else:
                self.suppliers.append(User.objects.get(email=email).supplier)

        # Create Customers
        self.customers = []
        for i in range(1, 11):
            email = f'customer{i}@craft.com'
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(
                    email=email, password='craftpassword123',
                    first_name=f'Customer', last_name=f'{i}', is_customer=True, is_verified=True
                )
                cust = Customer.objects.create(user=u)
                self.customers.append(cust)
            else:
                self.customers.append(User.objects.get(email=email).customer)

        # Create Delivery
        self.delivery_users = []
        for i in range(1, 3):
            email = f'delivery{i}@craft.com'
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(
                    email=email, password='craftpassword123',
                    first_name=f'Delivery', last_name=f'{i}', is_delivery=True, is_verified=True
                )
                deliv = Delivery.objects.create(
                    user=u
                )
                self.delivery_users.append(deliv)
            else:
                self.delivery_users.append(User.objects.get(email=email).delivery)

    def _seed_categories(self):
        self.stdout.write("- Seeding Categories...")
        cats = ['Woodworking', 'Pottery', 'Textiles', 'Jewelry', 'Leather']
        self.categories = []
        for cat in cats:
            obj, _ = Category.objects.get_or_create(Title=cat, defaults={'Description': f'{cat} goods'})
            self.categories.append(obj)
            
        mats = ['Oak Wood', 'Clay', 'Cotton', 'Silver', 'Full Grain Leather']
        self.materials = []
        for mat in mats:
            obj, _ = MatCategory.objects.get_or_create(Title=mat)
            self.materials.append(obj)

    def _seed_products(self):
        self.stdout.write("- Seeding Products...")
        self.products = []
        for i in range(30):
            sup = random.choice(self.suppliers)
            cat = random.choice(self.categories)
            mat = random.choice(self.materials)
            prod_name = f'Handcrafted {mat.Title} Item {i}'
            
            if not Product.objects.filter(ProductName=prod_name).exists():
                prod = Product.objects.create(
                    ProductName=prod_name,
                    ProductDescription=f'A beautiful handcrafted item made of {mat.Title}.',
                    Supplier=sup,
                    Category=cat,
                    MatCategory=mat,
                    QuantityPerUnit='1 piece',
                    UnitPrice=Decimal(random.randint(50, 500)),
                    UnitWeight=Decimal(random.uniform(0.5, 5.0)),
                    Stock=random.randint(0, 50),
                    Rating=Decimal(random.uniform(3.5, 5.0))
                )
                self.products.append(prod)
            else:
                self.products.append(Product.objects.get(ProductName=prod_name))

    def _seed_warehouses(self):
        self.stdout.write("- Seeding Warehouses...")
        from accounts.models import Address
        address, _ = Address.objects.get_or_create(
            user=self.admin_user, 
            defaults={'BuildingNO': '1A', 'Street': 'Craft St', 'City': 'Cairo', 'State': 'Cairo'}
        )
        for i in range(1, 3):
            Warehouse.objects.get_or_create(
                name=f'Central Hub {i}',
                defaults={'Address': address, 'contact_person': f'Manager {i}', 'contact_phone': '0123456789', 'delivery_fee': Decimal('50.00')}
            )

    def _seed_orders_and_returns(self):
        self.stdout.write("- Seeding Orders...")
        self.orders = []
        status_choices = ['created', 'ready_to_ship', 'on my way', 'delivered successfully', 'cancelled']
        
        for i in range(20):
            cust = random.choice(self.customers)
            from accounts.models import Address
            address = Address.objects.filter(user=cust.user).first()
            if not address:
                address = Address.objects.create(user=cust.user, BuildingNO='1', Street='Main St', City='Cairo', State='Cairo')

            order = Order.objects.create(
                user=cust.user,
                total_amount=Decimal(0),
                status=random.choice(status_choices),
                address=address
            )
            self.orders.append(order)
            
            total = Decimal(0)
            for _ in range(random.randint(1, 4)):
                prod = random.choice(self.products)
                qty = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    price=prod.UnitPrice
                )
                total += prod.UnitPrice * qty
            
            order.total_amount = total
            order.final_amount = total
            order.save()

            if order.status in ['delivered successfully', 'on my way']:
                PaymentHistory.objects.create(order=order, user=cust.user, payment_status='succeeded')
                
                if order.status == 'delivered successfully':
                    for item in order.items.all():
                        Transaction.objects.create(
                            user=item.product.Supplier.user,
                            transaction_type=Transaction.TransactionType.PURCHASED_PRODUCTS,
                            amount=item.price * item.quantity
                        )

    def _seed_reviews(self):
        self.stdout.write("- Seeding Reviews...")
        for _ in range(30):
            prod = random.choice(self.products)
            cust = random.choice(self.customers)
            Review.objects.get_or_create(
                product=prod,
                customer=cust,
                defaults={'rating': random.randint(3, 5), 'comment': 'Great craftsmanship!', 'status': 'APPROVED'}
            )

    def _seed_tickets_and_disputes(self):
        self.stdout.write("- Seeding Tickets & Disputes...")
        for _ in range(5):
            cust = random.choice(self.customers)
            t = Ticket.objects.create(
                user=cust.user,
                subject=f'Issue with my account',
                description='I cannot update my email address.',
                priority=random.choice(['low', 'medium', 'high']),
                status='open'
            )
            TicketMessage.objects.create(ticket=t, sender=cust.user, message='Please help me fix this.')

        # Create Disputes
        delivered_orders = [o for o in self.orders if o.status == 'delivered successfully']
        for _ in range(min(3, len(delivered_orders))):
            order = random.choice(delivered_orders)
            Dispute.objects.get_or_create(
                order=order,
                customer=order.user,
                supplier=order.items.first().product.Supplier.user,
                defaults={'reason': 'Late delivery', 'status': 'open'}
            )
