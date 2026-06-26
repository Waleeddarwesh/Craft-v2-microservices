import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

# Import Models
from accounts.models import User, Customer, Supplier, Delivery, Address
from products.models import Category, MatCategory, Product
from orders.models import Order, OrderItem, Shipment, Warehouse, Coupon
from payment.models import PaymentHistory
from reviews.models import Review
from support_tickets.models import Ticket, TicketMessage
from disputes.models import Dispute
from notifications.models import Notification
from returnrequest.models import Transaction, BalanceWithdrawRequest, ReturnRequest
from workflows.models import DepartmentTask, ApprovalRequest
from audit_logs.models import AuditLog, FraudAlert
from course.models import Course, CourseVideos, Enrollment

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive demo data for the Craft Operating Platform'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting comprehensive database seed..."))
        
        self._seed_users()
        self._seed_categories()
        self._seed_products()
        self._seed_courses()
        self._seed_warehouses()
        self._seed_coupons()
        self._seed_orders_and_returns()
        self._seed_withdrawals()
        self._seed_reviews()
        self._seed_tickets_and_disputes()
        self._seed_workflows_and_approvals()
        self._seed_audit_logs_and_fraud()
        self._seed_notifications()

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Database successfully seeded with comprehensive data!"))

    def _seed_users(self):
        self.stdout.write("- Seeding Users & RBAC...")
        # Create Admin
        if not User.objects.filter(email='admin@craft.com').exists():
            self.admin_user = User.objects.create_superuser(
                email='admin@craft.com', password='craftpassword123',
                first_name='System', last_name='Admin', is_verified=True
            )
        else:
            self.admin_user = User.objects.get(email='admin@craft.com')

        # Create Finance/Support users
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
                deliv = Delivery.objects.create(user=u)
                self.delivery_users.append(deliv)
            else:
                self.delivery_users.append(User.objects.get(email=email).delivery)

    def _seed_categories(self):
        self.stdout.write("- Seeding Categories...")
        cats = ['Woodworking', 'Pottery', 'Textiles', 'Jewelry', 'Leather', 'Digital Crafts']
        self.categories = []
        for cat in cats:
            try:
                obj = Category.objects.filter(Title=cat).first()
                if not obj:
                    obj = Category.objects.create(Title=cat, Description=f'{cat} goods')
                self.categories.append(obj)
            except Exception:
                pass
        if not self.categories:
            self.categories = list(Category.objects.all()[:5])
            
        mats = ['Oak Wood', 'Clay', 'Cotton', 'Silver', 'Full Grain Leather', 'Digital File']
        self.materials = []
        for mat in mats:
            try:
                obj = MatCategory.objects.filter(Title=mat).first()
                if not obj:
                    obj = MatCategory.objects.create(Title=mat)
                self.materials.append(obj)
            except Exception:
                pass
        if not self.materials:
            self.materials = list(MatCategory.objects.all()[:5])

    def _seed_products(self):
        self.stdout.write("- Seeding Products...")
        self.products = []
        for i in range(50):
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
                    Rating=Decimal(random.uniform(3.5, 5.0)),
                    publish_status='pending' if i < 15 else 'approved'
                )
                self.products.append(prod)
            else:
                prod = Product.objects.get(ProductName=prod_name)
                if i < 15:
                    prod.publish_status = 'pending'
                    prod.save()
                self.products.append(prod)

    def _seed_courses(self):
        self.stdout.write("- Seeding Courses...")
        self.courses = []
        for i in range(15):
            sup = random.choice(self.suppliers)
            cat = random.choice(self.categories)
            course_title = f'Masterclass: Advanced {cat.Title} {i}'
            
            if not Course.objects.filter(CourseTitle=course_title).exists():
                c = Course.objects.create(
                    CourseTitle=course_title,
                    Description=f"Learn everything about {cat.Title} from our expert suppliers.",
                    CategoryID=cat,
                    Supplier=sup,
                    Price=Decimal(random.randint(200, 1500)),
                    Rating=Decimal(random.uniform(4.0, 5.0)),
                    NumberOfLec=random.randint(5, 20),
                    CourseHours=random.randint(10, 50),
                    completed=random.choice([True, False])
                )
                self.courses.append(c)
                
                # Enroll some customers
                for _ in range(random.randint(1, 5)):
                    cust = random.choice(self.customers)
                    try:
                        Enrollment.objects.get_or_create(Course=c, EnrolledUser=cust.user)
                    except Exception:
                        pass
            else:
                self.courses.append(Course.objects.get(CourseTitle=course_title))

    def _seed_warehouses(self):
        self.stdout.write("- Seeding Warehouses...")
        address, _ = Address.objects.get_or_create(
            user=self.admin_user, 
            defaults={'BuildingNO': '1A', 'Street': 'Craft St', 'City': 'Cairo', 'State': 'Cairo'}
        )
        for i in range(1, 4):
            Warehouse.objects.get_or_create(
                name=f'Central Hub {i}',
                defaults={'Address': address, 'contact_person': f'Manager {i}', 'contact_phone': '0123456789', 'delivery_fee': Decimal('50.00')}
            )

    def _seed_coupons(self):
        self.stdout.write("- Seeding Coupons...")
        for code in ['SUMMER2026', 'WELCOME10', 'CRAFT50']:
            try:
                Coupon.objects.get_or_create(
                    code=code,
                    defaults={
                        'supplier': random.choice(self.suppliers),
                        'discount': Decimal(random.randint(10, 50)),
                        'active': True,
                        'valid_from': timezone.now(),
                        'valid_to': timezone.now() + timedelta(days=90),
                        'terms': 'Standard terms apply.'
                    }
                )
            except Exception:
                pass

    def _seed_orders_and_returns(self):
        self.stdout.write("- Seeding Orders and Transactions...")
        self.orders = []
        status_choices = ['created', 'ready_to_ship', 'on my way', 'delivered successfully', 'cancelled', 'returned']
        
        for i in range(50):
            cust = random.choice(self.customers)
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

            if order.status in ['delivered successfully', 'on my way', 'returned']:
                PaymentHistory.objects.create(order=order, user=cust.user, payment_status='succeeded')
                
                if order.status in ['delivered successfully', 'returned']:
                    for item in order.items.all():
                        Transaction.objects.create(
                            user=item.product.Supplier.user,
                            transaction_type=Transaction.TransactionType.PURCHASED_PRODUCTS,
                            amount=item.price * item.quantity
                        )
                        
                # Create a return request for some orders
                if order.status == 'returned' and not ReturnRequest.objects.filter(order=order).exists():
                    try:
                        item = order.items.first()
                        if item:
                            ReturnRequest.objects.create(
                                order=order,
                                user=cust.user,
                                product=item.product,
                                quantity=item.quantity,
                                supplier=item.product.Supplier,
                                amount=item.price * item.quantity,
                                reason=random.choice(['damaged', 'wrong_item', 'wrong_size', 'not_as_described', 'changed_mind']),
                                status=random.choice(["new", "accepted", "rejected", "cancelled"])
                            )
                    except Exception:
                        pass

    def _seed_withdrawals(self):
        self.stdout.write("- Seeding Withdrawals...")
        statuses = [
            BalanceWithdrawRequest.TransferStatus.REQUESTED,
            BalanceWithdrawRequest.TransferStatus.APPROVED,
            BalanceWithdrawRequest.TransferStatus.COMPLETED,
            BalanceWithdrawRequest.TransferStatus.REJECTED
        ]
        for sup in self.suppliers:
            for _ in range(random.randint(1, 3)):
                try:
                    BalanceWithdrawRequest.objects.create(
                        user=sup.user,
                        amount=Decimal(random.randint(500, 5000)),
                        transfer_number=f"TRX-{random.randint(10000, 99999)}",
                        transfer_type="Bank Transfer",
                        transfer_status=random.choice(statuses),
                        admin_notes="Looks good."
                    )
                except Exception:
                    pass

    def _seed_reviews(self):
        self.stdout.write("- Seeding Reviews...")
        for _ in range(60):
            prod = random.choice(self.products)
            cust = random.choice(self.customers)
            Review.objects.get_or_create(
                product=prod,
                customer=cust,
                defaults={
                    'rating': random.randint(1, 5), 
                    'comment': random.choice(['Great craftsmanship!', 'Loved it.', 'Arrived late but good quality.', 'Not exactly what I expected.']), 
                    'status': random.choice(['PENDING_MODERATION', 'APPROVED', 'REJECTED'])
                }
            )

    def _seed_tickets_and_disputes(self):
        self.stdout.write("- Seeding Support Tickets & Disputes...")
        for _ in range(15):
            cust = random.choice(self.customers)
            try:
                t = Ticket.objects.create(
                    user=cust.user,
                    user_name=cust.user.first_name or "Customer",
                    subject=f'Issue with order #{random.randint(100, 999)}',
                    description='I cannot find my tracking number.',
                    priority=random.choice(['low', 'medium', 'high']),
                    status=random.choice(['open', 'in_progress', 'resolved', 'closed'])
                )
                TicketMessage.objects.create(ticket=t, sender=cust.user, message='Please help me fix this.')
                if t.status != 'open':
                    TicketMessage.objects.create(ticket=t, sender=self.support_user, message='We have looked into it. The tracking number is XYZ123.')
            except Exception:
                pass

        delivered_orders = [o for o in self.orders if o.status == 'delivered successfully']
        for _ in range(min(10, len(delivered_orders))):
            order = random.choice(delivered_orders)
            if not Dispute.objects.filter(order=order).exists():
                Dispute.objects.create(
                    order=order,
                    customer=order.user,
                    supplier=order.items.first().product.Supplier.user,
                    reason=random.choice(['Late delivery', 'Item defective', 'Wrong item sent']),
                    status=random.choice(['open', 'investigating', 'resolved_customer', 'resolved_supplier'])
                )

    def _seed_workflows_and_approvals(self):
        self.stdout.write("- Seeding Tasks & Approvals...")
        departments = ['Support', 'Finance', 'Catalog', 'Admin', 'Logistics']
        
        for i in range(25):
            DepartmentTask.objects.create(
                title=f"Review Operations Report Q{i%4+1}",
                description="Please check the numbers and approve.",
                department=random.choice(departments),
                assigned_to=random.choice([self.admin_user, self.support_user, None]),
                related_object_type="Report",
                related_object_id=str(random.randint(100, 900)),
                status=random.choice(['open', 'in_progress', 'waiting_approval', 'completed']),
                priority=random.choice(['low', 'medium', 'high', 'critical']),
                created_by=self.admin_user
            )

        for i in range(30):
            ApprovalRequest.objects.create(
                request_type=random.choice(["Supplier Registration", "Large Withdrawal", "Product Moderation", "Course Publication"]),
                related_object_type=random.choice(["Supplier", "Withdrawal", "Product", "Course"]),
                related_object_id=str(random.randint(10, 500)),
                requested_by=random.choice(self.suppliers).user,
                assigned_department=random.choice(departments),
                status=random.choice(['pending', 'approved', 'rejected']),
                reviewed_by=self.admin_user if random.random() > 0.5 else None
            )

    def _seed_audit_logs_and_fraud(self):
        self.stdout.write("- Seeding Audit Logs & Fraud Alerts...")
        actions = ["User Login", "Updated Password", "Created Order", "Approved Supplier", "Processed Refund", "Changed Settings"]
        waleed = User.objects.filter(email='waleed@craft.com').first()
        users_to_seed = [self.admin_user, self.support_user, self.suppliers[0].user]
        if waleed: users_to_seed.append(waleed)
        
        for i in range(50):
            AuditLog.objects.create(
                user=random.choice(users_to_seed),
                action=random.choice(actions),
                entity_type=random.choice(["User", "Order", "Supplier", "System"]),
                entity_id=str(random.randint(1, 100)),
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 CraftBrowser/1.0"
            )

        for i in range(15):
            FraudAlert.objects.create(
                user=random.choice(self.customers).user,
                reason=random.choice(["Multiple failed logins", "Unusually large order", "Suspicious IP address", "Rapid sequential withdrawals"]),
                risk_score=random.randint(60, 100),
                status=random.choice(['pending', 'investigating', 'resolved', 'action_taken']),
                notes="Requires manual review."
            )

    def _seed_notifications(self):
        self.stdout.write("- Seeding Notifications...")
        waleed = User.objects.filter(email='waleed@craft.com').first()
        users_to_seed = [self.admin_user, self.support_user]
        if waleed: users_to_seed.append(waleed)
        for user in users_to_seed:
            for i in range(10):
                try:
                    Notification.objects.create(
                        user=user,
                        message=f"System Alert #{i}: Please check the dashboard for recent activities.",
                        is_read=random.choice([True, False])
                    )
                except Exception:
                    pass
