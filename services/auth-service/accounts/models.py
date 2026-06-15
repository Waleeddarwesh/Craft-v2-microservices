from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.maneger import UserManager

AUTH_PROVIDERS = {'email': 'email', 'google': 'google', 'github': 'github', 'linkedin': 'linkedin'}


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False)
    email = models.EmailField(max_length=255, verbose_name=_("Email Address"), unique=True)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    PhoneNO = models.CharField(max_length=14, verbose_name=_("Phone number"))
    Balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_customer = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, null=True, blank=True, verbose_name="FCM Token")
    last_password_reset_request = models.DateTimeField(null=True, blank=True)
    auth_provider = models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["first_name", "last_name", "password"]
    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        permissions = [
            ("can_approve_withdrawals", "Can approve withdrawals"),
            ("can_refund_orders", "Can refund orders"),
            ("can_suspend_users", "Can suspend users"),
            ("can_verify_suppliers", "Can verify suppliers"),
            ("can_manage_courses", "Can manage courses"),
            ("can_manage_products", "Can manage products"),
            ("can_manage_disputes", "Can manage disputes"),
            ("can_view_financial_reports", "Can view financial reports"),
            ("can_view_audit_logs", "Can view audit logs"),
            ("can_manage_support_tickets", "Can manage support tickets"),
            ("can_moderate_reviews", "Can moderate reviews"),
        ]

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        
        # Inject roles into the token payload so that other microservices can use HasRole
        roles = []
        if self.is_superuser or getattr(self, 'is_staff', False):
            roles.append('admin')
        if getattr(self, 'is_supplier', False):
            roles.append('supplier')
        if getattr(self, 'is_delivery', False):
            roles.append('delivery')
        if getattr(self, 'is_customer', False) or not roles:
            roles.append('customer')
            
        refresh['roles'] = roles
        
        # IMPORTANT: Also set roles on the access token explicitly.
        # simplejwt does NOT propagate refresh claims to access_token automatically.
        access = refresh.access_token
        access['roles'] = roles
        
        return {
            "refresh": str(refresh),
            "access": str(access)
        }

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if User.objects.filter(email__iexact=self.email).exclude(pk=self.pk).exists():
            raise ValidationError(_("This email is already in use."))

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if not self.pk or not self.password:
            if not self.pk:
                self.pk = None
            self.password = make_password(self.password)

        super().save(*args, **kwargs)


CARD_TYPE_CHOICES = (
    ('visa', 'Visa'),
    ('mastercard', 'Mastercard'),
    ('amex', 'American Express'),
    ('discover', 'Discover'),
    ('other', 'Other'),
)


class PaymentCard(models.Model):
    """Reusable payment card model linked to any User (Customer or Supplier)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_cards')
    card_number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r'^\d{13,16}$', 'Enter a valid card number (13-16 digits).')],
    )
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='visa')
    expiry_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    expiry_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2024), MaxValueValidator(2099)],
    )
    cvv = models.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{3,4}$', 'Enter a valid CVV (3 or 4 digits).')],
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Payment Card'
        verbose_name_plural = 'Payment Cards'

    def __str__(self):
        return f"{self.get_card_type_display()} ending in {self.card_number[-4:]}"

    @property
    def masked_number(self):
        """Return the card number with all but the last 4 digits masked."""
        return f"{'*' * (len(self.card_number) - 4)}{self.card_number[-4:]}"

    def save(self, *args, **kwargs):
        # If this card is set as default, unset any other default cards for this user
        if self.is_default:
            PaymentCard.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        # If this is the user's first card, make it default
        if not self.pk and not PaymentCard.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    CustomerPhoto = models.ImageField(upload_to='customer_photos/%y/%m/%d', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    SupplierPhoto = models.ImageField(upload_to='supplier_photos/%y/%m/%d', blank=True, null=True)
    SupplierCover = models.ImageField(upload_to='supplier_covers/%y/%m/%d', blank=True, null=True)
    CategoryTitle = models.CharField(max_length=50)
    Logo = models.ImageField(upload_to='supplier_logos/%y/%m/%d', blank=True, null=True)
    SupplierContract = models.FileField(upload_to='supplier_contracts/%y/%m/%d')
    SupplierIdentity = models.FileField(upload_to='supplier_identities/%y/%m/%d')
    FollowersNo = models.PositiveIntegerField(default=0)
    ExperienceYears = models.IntegerField(blank=True, null=True)
    Rating = models.DecimalField(max_digits=10, decimal_places=2, default=5.0,
                                 validators=(MinValueValidator(0.0), MaxValueValidator(5.0)))
    Orders = models.IntegerField(blank=True, null=True)
    accepted_supplier = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def update_rating(self):
        avg_rating = self.supplier_rating.aggregate(models.Avg('rating'))['rating__avg']
        self.Rating = avg_rating if avg_rating is not None else 0
        self.save()


class Delivery(models.Model):
    class PerformanceTier(models.TextChoices):
        BRONZE = 'bronze', 'Bronze'
        SILVER = 'silver', 'Silver'
        GOLD = 'gold', 'Gold'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="delivery")
    DeliveryPhoto = models.ImageField(upload_to='shipper_photos/%y/%m/%d')
    DeliveryContract = models.ImageField(upload_to='shipper_contracts/%y/%m/%d')
    DeliveryIdentity = models.ImageField(upload_to='shipper_identities/%y/%m/%d')
    VehicleModel = models.CharField(max_length=100)
    VehicleColor = models.CharField(max_length=100, blank=True, null=True)
    plateNO = models.CharField(max_length=100)
    Rating = models.DecimalField(max_digits=10, decimal_places=2, default=5.0,
                                 validators=(MinValueValidator(0.0), MaxValueValidator(5.0)))
    Orders = models.IntegerField(blank=True, null=True)
    ExperienceYears = models.IntegerField(blank=True, null=True)
    governorate = models.CharField(max_length=100, default='default_governorate')
    accepted_delivery = models.BooleanField(default=False)
    performance_tier = models.CharField(max_length=20, choices=PerformanceTier.choices, default=PerformanceTier.BRONZE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def update_rating(self):
        avg_rating = self.delivery_rating.aggregate(models.Avg('rating'))['rating__avg']
        self.Rating = avg_rating if avg_rating is not None else 0
        self.save()

    def update_performance_tier(self):
        from orders.models import Shipment
        total_assigned = Shipment.objects.filter(delivery_person=self).count()
        if total_assigned == 0:
            return

        success_count = Shipment.objects.filter(
            delivery_person=self, 
            status=Shipment.ShipmentStatus.DELIVERED_SUCCESSFULLY
        ).count()
        
        score = (success_count / total_assigned) * 100

        if score >= 85:
            self.performance_tier = self.PerformanceTier.GOLD
        elif score >= 60:
            self.performance_tier = self.PerformanceTier.SILVER
        else:
            self.performance_tier = self.PerformanceTier.BRONZE
        
        self.save(update_fields=['performance_tier'])

    def save(self, *args, **kwargs):
        if not self.pk and not self.ExperienceYears:
            self.ExperienceYears = timezone.now().year - self.user.date_joined.year
        super().save(*args, **kwargs)



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    BuildingNO = models.CharField(max_length=10, null=True)
    Street = models.CharField(max_length=100)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.get_full_name}"


def get_default_customer_content_type():
    return ContentType.objects.get_for_model(Customer).id

class Follow(models.Model):
    follower_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                              default=get_default_customer_content_type)
    follower_object_id = models.PositiveIntegerField(default=0)
    follower = GenericForeignKey('follower_content_type', 'follower_object_id')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.follower} follows {self.supplier.user.get_full_name}"

    class Meta:
        unique_together = ('follower_content_type', 'follower_object_id', 'supplier')
        indexes = [
            models.Index(fields=['follower_content_type', 'follower_object_id'], name='follow_follower_idx'),
            models.Index(fields=['supplier'], name='follow_supplier_idx'),
        ]


@receiver(post_save, sender=Follow)
def update_followers_count_on_create(sender, instance, created, **kwargs):
    if created:
        instance.supplier.FollowersNo += 1
        instance.supplier.save()


@receiver(post_delete, sender=Follow)
def update_followers_count_on_delete(sender, instance, **kwargs):
    instance.supplier.FollowersNo -= 1
    instance.supplier.save()


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} - otp code"

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.status} at {self.timestamp}"

class TrustedDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_devices')
    device_signature = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'device_signature')

    def __str__(self):
        return f"{self.user.email} - Device {self.id}"