from django.core.management.base import BaseCommand
from accounts.models import User, Customer, Supplier, Delivery

class Command(BaseCommand):
    help = 'Seeds the database with all types of accounts using a specific password'

    def handle(self, *args, **kwargs):
        password = "Wdshs192002"

        # 1. Superuser
        if not User.objects.filter(email='superuser@example.com').exists():
            su = User.objects.create_superuser(
                email='superuser@example.com',
                first_name='Super',
                last_name='User',
                password=password,
                PhoneNO='1234567890',
                is_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser created: superuser@example.com"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser already exists."))

        # 2. Staff / Dashboard User
        if not User.objects.filter(email='staff@example.com').exists():
            staff = User.objects.create_user(
                email='staff@example.com',
                first_name='Staff',
                last_name='User',
                password=password,
                PhoneNO='1234567891',
                is_staff=True,
                is_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f"Staff user created: staff@example.com"))
        else:
            self.stdout.write(self.style.WARNING(f"Staff user already exists."))

        # 3. Customer
        if not User.objects.filter(email='customer@example.com').exists():
            customer_user = User.objects.create_user(
                email='customer@example.com',
                first_name='Customer',
                last_name='User',
                password=password,
                PhoneNO='1234567892',
                is_customer=True,
                is_verified=True
            )
            Customer.objects.create(user=customer_user)
            self.stdout.write(self.style.SUCCESS(f"Customer user created: customer@example.com"))
        else:
            self.stdout.write(self.style.WARNING(f"Customer user already exists."))

        # 4. Supplier
        if not User.objects.filter(email='supplier@example.com').exists():
            supplier_user = User.objects.create_user(
                email='supplier@example.com',
                first_name='Supplier',
                last_name='User',
                password=password,
                PhoneNO='1234567893',
                is_supplier=True,
                is_verified=True
            )
            Supplier.objects.create(user=supplier_user, CategoryTitle='General', accepted_supplier=True)
            self.stdout.write(self.style.SUCCESS(f"Supplier user created: supplier@example.com"))
        else:
            self.stdout.write(self.style.WARNING(f"Supplier user already exists."))

        # 5. Delivery
        if not User.objects.filter(email='delivery@example.com').exists():
            delivery_user = User.objects.create_user(
                email='delivery@example.com',
                first_name='Delivery',
                last_name='User',
                password=password,
                PhoneNO='1234567894',
                is_delivery=True,
                is_verified=True
            )
            Delivery.objects.create(user=delivery_user, VehicleModel='Van', plateNO='123-ABC', accepted_delivery=True)
            self.stdout.write(self.style.SUCCESS(f"Delivery user created: delivery@example.com"))
        else:
            self.stdout.write(self.style.WARNING(f"Delivery user already exists."))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with all account types!"))
