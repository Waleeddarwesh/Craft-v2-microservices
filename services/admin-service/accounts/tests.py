from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from .models import User, Customer, Supplier, OneTimePassword, Follow

class AccountsTests(APITestCase):
    def setUp(self):
        # 1. Setup Base URLs
        self.register_url = reverse('register_customer')
        self.verify_url = reverse('verify_email')
        self.login_url = reverse('login')
        self.password_reset_req_url = reverse('password-reset')
        self.password_reset_set_url = reverse('set-new-password')
        self.customer_profile_url = reverse('customer-profile')
        
        # 2. Base test data
        self.customer_data = {
            "email": "testcustomer@crafteg.com",
            "first_name": "Test",
            "last_name": "Customer",
            "password": "Password123!",
            "password2": "Password123!",
            "PhoneNO": "01012345678"
        }

    def test_full_customer_lifecycle(self):
        # --- 1. Registration ---
        response = self.client.post(self.register_url, self.customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.customer_data['email'])

        user = User.objects.get(email=self.customer_data['email'])
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_customer)

        # Retrieve the OTP generated during registration
        otp_obj = OneTimePassword.objects.get(user=user)
        otp = otp_obj.otp

        # --- 2. OTP Verification ---
        verify_data = {
            "email": user.email,
            "otp": otp,
            "password": self.customer_data['password']
        }
        response = self.client.post(self.verify_url, verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        # --- 3. Login ---
        login_data = {
            "email": user.email,
            "password": self.customer_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        # --- 4. Profile Access ---
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.customer_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], "Test")
        self.client.credentials()  # clear auth

    def test_password_reset_idor_prevention(self):
        # Create victim
        victim = User.objects.create_user(
            email="victim@crafteg.com", first_name="Victim", last_name="V",
            PhoneNO="01111111111", password="OldPassword123!"
        )
        OneTimePassword.objects.create(user=victim, otp="1234")

        # Create attacker
        attacker = User.objects.create_user(
            email="attacker@crafteg.com", first_name="Attacker", last_name="A",
            PhoneNO="01222222222", password="AttackerPassword123!"
        )

        # Attacker tries to use victim's OTP (1234) but supplies attacker's email OR victim's email 
        # Wait, if they supply victim's email, it's just a normal password reset, but they don't own the email.
        # IDOR prevention was specifically fixing the issue where they send Attacker's Email + Victim's OTP.
        
        # Attack scenario: Attacker sends their own email, but brute forces OTP (1234).
        # This should fail because the OTP '1234' belongs to victim@crafteg.com, not attacker@crafteg.com
        reset_data = {
            "email": attacker.email,
            "otp": "1234",
            "new_password": "HackedPassword123!",
            "confirm_password": "HackedPassword123!"
        }
        response = self.client.patch(self.password_reset_set_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid OTP", str(response.data))

        # Check victim password is not changed
        self.assertTrue(victim.check_password("OldPassword123!"))

    def test_password_reset_success(self):
        user = User.objects.create_user(
            email="reset@crafteg.com", first_name="Reset", last_name="User",
            PhoneNO="01555555555", password="OldPassword123!"
        )
        OneTimePassword.objects.create(user=user, otp="4321")

        reset_data = {
            "email": user.email,
            "otp": "4321",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = self.client.patch(self.password_reset_set_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword123!"))

    def test_follow_supplier(self):
        # 1. Create a customer
        customer_user = User.objects.create_user(
            email="fan@crafteg.com", first_name="Fan", last_name="User",
            PhoneNO="01000000001", password="Password123!", is_customer=True, is_verified=True
        )
        customer_profile = Customer.objects.create(user=customer_user)

        # 2. Create a supplier
        supplier_user = User.objects.create_user(
            email="star@crafteg.com", first_name="Star", last_name="Supplier",
            PhoneNO="01000000002", password="Password123!", is_supplier=True, is_verified=True
        )
        supplier_profile = Supplier.objects.create(user=supplier_user, CategoryTitle="Art", ExperienceYears=5)

        # 3. Follow Supplier API
        login_res = self.client.post(self.login_url, {"email": customer_user.email, "password": "Password123!"})
        token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        follow_url = reverse('follow_supplier', kwargs={'supplier_id': supplier_profile.id})
        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify Follow object exists
        customer_ct = ContentType.objects.get_for_model(Customer)
        follow_exists = Follow.objects.filter(
            follower_content_type=customer_ct,
            follower_object_id=customer_profile.id,
            supplier=supplier_profile
        ).exists()
        self.assertTrue(follow_exists)

        # Unfollow
        response = self.client.delete(follow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        follow_exists = Follow.objects.filter(
            follower_content_type=customer_ct,
            follower_object_id=customer_profile.id,
            supplier=supplier_profile
        ).exists()
        self.assertFalse(follow_exists)
