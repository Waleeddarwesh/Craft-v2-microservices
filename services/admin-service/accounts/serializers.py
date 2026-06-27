from rest_framework import serializers
from .models import Customer, Supplier, Delivery, User, Address, PaymentCard
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError 
# Mock imports for decoupled products
# from products.models import Product ,Category
# from products.serializers import ProductImageSerializer
from django.core.signing import Signer, BadSignature
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','PhoneNO','date_joined','Balance']
        read_only_fields = ['Balance','date_joined']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','BuildingNO','Street','City','State']

class PaymentCardSerializer(serializers.ModelSerializer):
    masked_number = serializers.CharField(read_only=True)

    class Meta:
        model = PaymentCard
        fields = ['id', 'card_number', 'card_type', 'expiry_month', 'expiry_year', 'cvv', 'is_default', 'masked_number', 'created_at']
        extra_kwargs = {
            'card_number': {'write_only': True},
            'cvv': {'write_only': True},
        }
        read_only_fields = ['created_at']

    def validate_expiry_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError(_("Month must be between 1 and 12."))
        return value

    def validate_expiry_year(self, value):
        current_year = timezone.now().year
        if value < current_year:
            raise serializers.ValidationError(_("Card has expired."))
        return value

    def validate(self, attrs):
        # Check if card is expired (month + year combo)
        from django.utils import timezone
        now = timezone.now()
        year = attrs.get('expiry_year')
        month = attrs.get('expiry_month')
        if year and month:
            if year < now.year or (year == now.year and month < now.month):
                raise serializers.ValidationError({"error": _("This card has expired.")})
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AccountProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ProductName = serializers.CharField()
    UnitPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    Discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    images = serializers.ListField(child=serializers.DictField(), read_only=True)

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2','PhoneNO')

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_("This email is already registered."))
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": _("Passwords do not match")})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": _("Password must be at least 8 characters long and contain at least one digit")})
        if not re.match(r'^(010|011|012|015)\d{8}$', str(attrs['PhoneNO'])):
            raise serializers.ValidationError({"error": _("Phone number must be in the format 01*********")})
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": _("Phone number already exists")})
        
        return attrs

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'].title(),
            last_name=self.validated_data['last_name'].title(),
            PhoneNO=self.validated_data['PhoneNO'],
            is_customer=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Customer.objects.create(
            user=user
        )
        return user

class CategoreyTitle(serializers.Serializer):
    Title = serializers.CharField()

class SupplierRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    CategoryTitle = serializers.CharField(required=True)
    ExperienceYears = serializers.IntegerField(required=True)
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2','PhoneNO','CategoryTitle','ExperienceYears')  

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": "Password must be at least 8 characters long and contain at least one digit"})
        if not re.match(r'^(010|011|012|015)\d{8}$', str(attrs['PhoneNO'])):
            raise serializers.ValidationError({"error": "number must be in the format 01*********"})
        # Check if PhoneNO already exists in the database
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": "Phone number already exists"})
        
        return attrs
    
    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'].title(),
            last_name=self.validated_data['last_name'].title(),
            PhoneNO=self.validated_data['PhoneNO'],
            is_supplier=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Supplier.objects.create(
           user=user,
           CategoryTitle=self.validated_data['CategoryTitle'],
            ExperienceYears=self.validated_data['ExperienceYears'],
           )
        return user
 
class DeliveryRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    plateNO = serializers.CharField(required=True)
    VehicleModel = serializers.CharField(required=True)
    governorate = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'PhoneNO', 'plateNO','VehicleModel','governorate')

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_("This email is already registered."))
        return email
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": _("Passwords do not match")})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": _("Password must be at least 8 characters long and contain at least one digit")})
        if not re.match(r'^(010|011|012|015)\d{8}$', str(attrs['PhoneNO'])):
            raise serializers.ValidationError({"error": _("Phone number must be in the format 01*********")})
        # Check if PhoneNO already exists in the database
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": _("Phone number already exists")})
        
        return attrs
    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'].title(),
            last_name=self.validated_data['last_name'].title(),
            PhoneNO=self.validated_data['PhoneNO'],
            is_delivery=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Delivery.objects.create(
            user=user,
            plateNO=self.validated_data['plateNO'],
            VehicleModel=self.validated_data['VehicleModel'],
            governorate=self.validated_data['governorate'],
        )
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    first_name=serializers.CharField(max_length=255, read_only=True)
    is_staff=serializers.BooleanField(read_only=True)
    access=serializers.CharField(max_length=255, read_only=True)
    refresh=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'is_staff', 'access', 'refresh']


    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')
        request=self.context.get('request')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed({"message": _("Invalid credentials, try again")})

        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0]
        ua = request.META.get('HTTP_USER_AGENT', '')
        from .models import LoginHistory

        from django.utils.timezone import now
        if user_obj.locked_until and now() < user_obj.locked_until:
            LoginHistory.objects.create(user=user_obj, ip_address=ip, user_agent=ua, status='FAILED')
            raise AuthenticationFailed({"message": _("Account is temporarily locked due to multiple failed login attempts. Please try again later.")})

        user = authenticate(request, email=email, password=password)
        if not user:
            user_obj.failed_login_attempts += 1
            if user_obj.failed_login_attempts >= 5:
                from datetime import timedelta
                user_obj.locked_until = now() + timedelta(minutes=15)
                user_obj.failed_login_attempts = 0
            user_obj.save(update_fields=['failed_login_attempts', 'locked_until'])
            LoginHistory.objects.create(user=user_obj, ip_address=ip, user_agent=ua, status='FAILED')
            raise AuthenticationFailed({"message": _("Invalid credentials, try again")})

        # Reset failed login attempts on successful login
        if user_obj.failed_login_attempts > 0 or user_obj.locked_until:
            user_obj.failed_login_attempts = 0
            user_obj.locked_until = None
            user_obj.save(update_fields=['failed_login_attempts', 'locked_until'])
            
        LoginHistory.objects.create(user=user_obj, ip_address=ip, user_agent=ua, status='SUCCESS')

        if not user.is_verified:
            raise AuthenticationFailed({"message": _("Email is not verified")})
        tokens=user.tokens()
        return {
            'email':user.email,
            'first_name':user.first_name,
            'is_staff': user.is_staff,
            'is_customer': getattr(user, 'is_customer', False),
            'is_supplier': getattr(user, 'is_supplier', False),
            'is_delivery': getattr(user, 'is_delivery', False),
            'must_change_password': getattr(user, 'must_change_password', False),
            "access":str(tokens.get('access')),
            "refresh":str(tokens.get('refresh'))
        }

class CustomerProfileSerializer(serializers.ModelSerializer):
 user = UserSerializer()
 class Meta:
        model = Customer
        fields =  ['user','id','CustomerPhoto']

 def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance   
 def validate(self, attrs):
    # Check if user data is present
    user_data = attrs.get('user')
    if user_data:
        phone_no = str(user_data.get('PhoneNO', ''))
        if not re.match(r'^(010|011|012|015)\d{8}$', phone_no):
            raise serializers.ValidationError({"error": _("Phone number must be in the format 01*")})
        # Exclude the current user instance from the query if it exists
        if User.objects.filter(PhoneNO=phone_no).exclude(pk=self.instance.user.pk).exists():
            raise serializers.ValidationError({"error": _("Phone number already exists")})
    return attrs

class SupplierProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    products = AccountProductSerializer(many=True, source='product_set')

    class Meta:
        model = Supplier
        fields = [
            'user', 'id', 'SupplierCover', 'SupplierPhoto', 'CategoryTitle', 
            'ExperienceYears', 'Rating', 'Orders', 'products', 'accepted_supplier',  
        ]
        read_only_fields = ['Orders', 'Rating', 'accepted_supplier']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate(self, attrs):
        # Check if user data is present
        user_data = attrs.get('user')
        if user_data:
            phone_no = str(user_data.get('PhoneNO', ''))
            if not re.match(r'^(010|011|012|015)\d{8}$', phone_no):
                raise serializers.ValidationError({"error": _("Phone number must be in the format 01*")})
            # Exclude the current user instance from the query if it exists
            if User.objects.filter(PhoneNO=phone_no).exclude(pk=self.instance.user.pk).exists():
                raise serializers.ValidationError({"error": _("Phone number already exists")})
        return attrs

class deliveryProfileSerializer(serializers.ModelSerializer):
 user = UserSerializer()
 class Meta:
        model = Delivery
        fields =  ['user','id','DeliveryPhoto','Rating','Orders','ExperienceYears','VehicleModel','plateNO']
        read_only_fields = ['Orders','Rating']
 def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
 def validate(self, attrs):
    # Check if user data is present
    user_data = attrs.get('user')
    if user_data:
        phone_no = str(user_data.get('PhoneNO', ''))
        if not re.match(r'^(010|011|012|015)\d{8}$', phone_no):
            raise serializers.ValidationError({"error": _("Phone number must be in the format 01*")})
        # Exclude the current user instance from the query if it exists
        if User.objects.filter(PhoneNO=phone_no).exclude(pk=self.instance.user.pk).exists():
            raise serializers.ValidationError({"error": _("Phone number already exists")})
    return attrs

class CraftersSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    SupplierProducts = AccountProductSerializer(many=True, read_only=True, source='product_set')
    class Meta:
        model = Supplier
        fields = ('id','user', 'CategoryTitle','SupplierPhoto', 'SupplierProducts')

    def get_user(self, obj):
        return {'full_name': obj.user.get_full_name}
    
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)
    otp = serializers.CharField(max_length=4, min_length=4, write_only=True)
    new_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    class Meta:
        fields = ['email', 'otp', 'new_password', 'confirm_password']
        
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': _('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=6)

class SocialAccountCompleteSerializer(serializers.Serializer):
    """
    Handles the final registration step for a new social user.
    Supports different fields for customer, supplier, and delivery user types.
    """
    temp_token = serializers.CharField()
    phone_no = serializers.CharField(max_length=14)
    user_type = serializers.ChoiceField(choices=["customer", "supplier", "delivery"]) 
    
    # --- Optional Supplier Fields ---
    CategoryTitle = serializers.CharField(required=False)
    ExperienceYears = serializers.IntegerField(required=False)
    SupplierPhoto = serializers.ImageField(required=False)
    SupplierCover = serializers.ImageField(required=False)

    # --- Optional Delivery Fields ---
    DeliveryPhoto = serializers.ImageField(required=False)
    VehicleModel = serializers.CharField(required=False)
    VehicleColor = serializers.CharField(required=False) 
    plateNO = serializers.CharField(required=False)
    governorate = serializers.CharField(required=False)


    def validate(self, attrs):
        signer = Signer()
        try:
            self.social_data = signer.unsign_object(attrs['temp_token'])
        except BadSignature:
            raise serializers.ValidationError(_("Invalid or expired temporary token."))

        if User.objects.filter(PhoneNO=attrs['phone_no']).exists():
            raise serializers.ValidationError({"error": _("Phone number already exists.")})
        
        user_type = attrs.get('user_type')

        # --- Conditional Validation for User Types ---
        if user_type == 'supplier':
            required_fields = ['CategoryTitle', 'ExperienceYears', 'SupplierPhoto', 'SupplierCover']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"'{field}' is required for suppliers."})
        
        elif user_type == 'delivery':
            required_fields = ['DeliveryPhoto', 'VehicleModel','VehicleColor', 'plateNO', 'governorate', 'ExperienceYears']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"'{field}' is required for delivery."})
        
        return attrs

    def save(self):
        new_user = User.objects.create_user(
            email=self.social_data['email'],
            first_name=self.social_data['first_name'],
            last_name=self.social_data['last_name'],
            password=settings.SOCIAL_AUTH_PASSWORD,
            PhoneNO=self.validated_data['phone_no'],
            auth_provider=self.social_data['provider'],
            is_verified=True
        )

        user_type = self.validated_data['user_type']
        if user_type == "customer":
            Customer.objects.create(user=new_user)
            new_user.is_customer = True
        elif user_type == "supplier":
            Supplier.objects.create(
                user=new_user, 
                CategoryTitle=self.validated_data['CategoryTitle'],
                ExperienceYears=self.validated_data['ExperienceYears'],
                SupplierPhoto=self.validated_data['SupplierPhoto'],
                SupplierCover=self.validated_data['SupplierCover']
            )
            new_user.is_supplier = True
        elif user_type == "delivery":
            # --- Populate Delivery profile with extra data ---
            Delivery.objects.create(
                user=new_user,
                DeliveryPhoto=self.validated_data['DeliveryPhoto'],
                VehicleModel=self.validated_data['VehicleModel'],
                VehicleColor=self.validated_data.get('VehicleColor', ''), # Optional field
                plateNO=self.validated_data['plateNO'],
                ExperienceYears=self.validated_data['ExperienceYears'],
                governorate=self.validated_data['governorate']
            )
            new_user.is_delivery = True
        
        new_user.save()
        return new_user

class SupplierDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['SupplierContract', 'SupplierIdentity']

    def validate_file(self, file):
        if not file:
            raise serializers.ValidationError(_("File is required."))

        valid_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
        content_type = file.content_type

        if content_type not in valid_mime_types:
            raise serializers.ValidationError(_("Only PDF or image files (JPEG, PNG) are allowed."))

        return file

    def validate_SupplierContract(self, file):
        return self.validate_file(file)

    def validate_SupplierIdentity(self, file):
        return self.validate_file(file)
        
class deliveryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['DeliveryContract', 'DeliveryIdentity']

    def validate_file(self, file):
        if not file:
            raise serializers.ValidationError("File is required.")

        valid_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
        content_type = file.content_type

        if content_type not in valid_mime_types:
            raise serializers.ValidationError("Only PDF or image files (JPEG, PNG) are allowed.")

        return file

    def validate_DeliveryContract(self, file):
        return self.validate_file(file)

    def validate_DeliveryIdentity(self, file):
        return self.validate_file(file)
        