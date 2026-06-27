from django.contrib import admin
from .models import User, Customer, Supplier, Delivery, Address, Follow, OneTimePassword, PaymentCard

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'is_customer', 'is_supplier', 'is_delivery')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'PhoneNO', 'Balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Role flags', {'fields': ('is_customer', 'is_supplier', 'is_delivery')}),
        ('Security & Auth', {
            'classes': ('collapse',),
            'fields': ('auth_provider', 'fcm_token', 'must_change_password', 'failed_login_attempts', 'locked_until')
        }),
        ('Important dates', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined', 'last_password_reset_request')
        }),
    )
    readonly_fields = (
        'last_login', 'date_joined', 'fcm_token', 'auth_provider', 
        'failed_login_attempts', 'locked_until', 'last_password_reset_request'
    )

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'masked_number_display', 'expiry_month', 'expiry_year', 'is_default')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'card_number')
    list_filter = ('card_type', 'is_default')
    readonly_fields = ('card_number', 'cvv', 'expiry_month', 'expiry_year', 'created_at')

    def masked_number_display(self, obj):
        return obj.masked_number
    masked_number_display.short_description = 'Card Number'

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('user', 'CategoryTitle', 'Rating', 'Orders', 'FollowersNo', 'accepted_supplier')
    list_editable = ('accepted_supplier',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'CategoryTitle')
    list_filter = ('accepted_supplier', 'CategoryTitle', 'Rating')
    ordering = ('-Rating',)
    fieldsets = (
        (None, {'fields': ('user', 'accepted_supplier')}),
        ('Info', {'fields': ('CategoryTitle', 'ExperienceYears')}),
        ('Stats', {'fields': ('Rating', 'Orders', 'FollowersNo')}),
        ('Media & Documents', {'fields': ('Logo', 'SupplierCover', 'SupplierContract', 'SupplierIdentity')})
    )

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'VehicleModel', 'plateNO', 'Rating', 'Orders', 'governorate', 'accepted_delivery')
    list_editable = ('accepted_delivery',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'VehicleModel', 'plateNO', 'governorate')
    list_filter = ('accepted_delivery', 'governorate', 'Rating')
    ordering = ('-Rating',)
    fieldsets = (
        (None, {'fields': ('user', 'accepted_delivery')}),
        ('Vehicle Info', {'fields': ('VehicleModel', 'VehicleColor', 'plateNO')}),
        ('Location & Stats', {'fields': ('governorate', 'ExperienceYears', 'Rating', 'Orders')}),
        ('Documents', {'fields': ('DeliveryContract', 'DeliveryIdentity')})
    )

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'BuildingNO', 'Street', 'City', 'State')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'Street', 'City', 'State')
    list_filter = ('City', 'State')

class FollowAdmin(admin.ModelAdmin):
    # Display the follower's name and the supplier's name in the admin list
    def get_follower_name(self, obj):
        return obj.follower.user.get_full_name if obj.follower else 'No follower'

    get_follower_name.admin_order_field = 'follower'  # Allows sorting by follower name
    get_follower_name.short_description = 'Follower'  # Custom column header

    list_display = ('get_follower_name', 'supplier')

    # Search functionality: allows searching by follower's ID and supplier's info
    search_fields = (
        'follower_object_id',  # Allows searching by the ID of the follower
        'supplier__user__email',
        'supplier__user__first_name',
        'supplier__user__last_name',
        'follower__user__email',  # To allow searching by the follower's email
        'follower__user__first_name',  # To allow searching by the follower's first name
        'follower__user__last_name'  # To allow searching by the follower's last name
    )

    # Filter options: allows filtering by follower type (Customer/Supplier) and supplier
    list_filter = ('follower_content_type', 'supplier')

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'otp')
    readonly_fields = ('otp',)

admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(OneTimePassword, OneTimePasswordAdmin)
admin.site.register(PaymentCard, PaymentCardAdmin)
