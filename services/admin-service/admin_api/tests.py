from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
try:
    from accounts.models import User, Supplier, Customer
    from orders.models import Order, OrderItem
    from returnrequest.models import BalanceWithdrawRequest
    from products.models import Product
except ImportError:
    pass

class AdminAPISecurityTests(APITestCase):
    def setUp(self):
        # Create Superuser
        self.superuser = User.objects.create_superuser(
            email="super@crafteg.com", password="Password123!", PhoneNO="01011111111", first_name="Super", last_name="User", is_verified=True
        )
        
        # Create Supplier 1
        self.supplier1_user = User.objects.create_user(
            email="supplier1@crafteg.com", password="Password123!", PhoneNO="01022222222", is_supplier=True, first_name="Supp", last_name="One", is_verified=True
        )
        self.supplier1 = Supplier.objects.create(user=self.supplier1_user)
        
        # Create Supplier 2
        self.supplier2_user = User.objects.create_user(
            email="supplier2@crafteg.com", password="Password123!", PhoneNO="01033333333", is_supplier=True, first_name="Supp", last_name="Two", is_verified=True
        )
        self.supplier2 = Supplier.objects.create(user=self.supplier2_user)
        
        # Create Customer
        self.customer_user = User.objects.create_user(
            email="customer@crafteg.com", password="Password123!", PhoneNO="01044444444", is_customer=True, first_name="Cust", last_name="Omer", is_verified=True
        )

        # Create Products
        self.product1 = Product.objects.create(Supplier=self.supplier1, ProductName="Product 1", UnitPrice=100, UnitWeight=1.0, Stock=10)
        self.product2 = Product.objects.create(Supplier=self.supplier2, ProductName="Product 2", UnitPrice=100, UnitWeight=1.0, Stock=10)

        # Create Address
        from accounts.models import Address
        self.address = Address.objects.create(user=self.customer_user, Street="Main St", City="Cairo", State="Cairo")

        # Create Orders
        self.order1 = Order.objects.create(user=self.customer_user, total_amount=100, address=self.address)
        OrderItem.objects.create(order=self.order1, product=self.product1, quantity=1, price=100)

        self.order2 = Order.objects.create(user=self.customer_user, total_amount=100, address=self.address)
        OrderItem.objects.create(order=self.order2, product=self.product2, quantity=1, price=100)
        
        # Create Withdrawals
        self.withdrawal = BalanceWithdrawRequest.objects.create(
            user=self.supplier1_user, amount=50, transfer_status="Pending"
        )

        # URLs
        # Note: Depending on admin_api/urls.py routes, we might need to adjust these.
        self.orders_url = reverse('admin-orders')
        self.withdrawal_action_url = reverse('admin-withdrawal-action', kwargs={'pk': self.withdrawal.pk})
        self.login_url = reverse('login')

    def authenticate(self, user):
        res = self.client.post(self.login_url, {"email": user.email, "password": "Password123!"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])

    def test_supplier_cannot_approve_withdrawals(self):
        """Test that a supplier (without explicit permission) is forbidden from approving a withdrawal."""
        self.authenticate(self.supplier2_user)
        response = self.client.post(self.withdrawal_action_url, {"action": "approve"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_approve_withdrawals(self):
        """Test that a superuser can approve a withdrawal."""
        self.authenticate(self.superuser)
        response = self.client.post(self.withdrawal_action_url, {"action": "approve"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multi_tenant_data_isolation_orders(self):
        """Test that suppliers only see their own orders, while superusers see all."""
        # 1. Supplier 1 should only see Order 1
        self.authenticate(self.supplier1_user)
        res1 = self.client.get(self.orders_url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res1.data), 1)
        self.assertEqual(res1.data[0]['id'], str(self.order1.id))

        # 2. Supplier 2 should only see Order 2
        self.authenticate(self.supplier2_user)
        res2 = self.client.get(self.orders_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res2.data), 1)
        self.assertEqual(res2.data[0]['id'], str(self.order2.id))

        # 3. Superuser should see both orders
        self.authenticate(self.superuser)
        res3 = self.client.get(self.orders_url)
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res3.data), 2)

    def test_supplier_cannot_view_audit_logs(self):
        """Test that a supplier without can_view_audit_logs permission cannot access audit logs."""
        self.authenticate(self.supplier1_user)
        response = self.client.get(reverse('admin-audit-logs'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response_recent = self.client.get(reverse('admin-recent-activity'))
        self.assertEqual(response_recent.status_code, status.HTTP_403_FORBIDDEN)
        
        response_fraud = self.client.get(reverse('admin-fraud-alerts'))
        self.assertEqual(response_fraud.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_view_audit_logs(self):
        """Test that a superuser can access audit logs."""
        self.authenticate(self.superuser)
        response = self.client.get(reverse('admin-audit-logs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
