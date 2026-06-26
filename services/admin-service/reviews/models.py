from django.db import models
from products.models import Product
from course.models import Course
from accounts.models import Customer,Delivery,Supplier

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    delivery_choices = (
        ('Dissatisfied',1),
        ('Satisfied',2),
        ('Very Satisfied',3)
    )
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='user_id')
    product = models.ForeignKey(Product, related_name='product_rating', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course,related_name='course_rating', on_delete=models.CASCADE, null=True, blank=True)
    delivery = models.ForeignKey(Delivery,related_name='delivery_rating', on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, related_name='supplier_rating',on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    image = models.ImageField(upload_to="product_reviews_images/%y/%m/%d", default="", null=True, blank=True)
    ease_of_place_order = models.CharField(choices = delivery_choices, null=True, blank=True , max_length=50)
    speed_of_delivery = models.CharField(choices = delivery_choices, null=True, blank=True, max_length=50)
    product_packaging =  models.CharField(choices = delivery_choices, null=True, blank=True, max_length=50)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'product'], condition=models.Q(product__isnull=False), name='unique_product_review'),
            models.UniqueConstraint(fields=['customer', 'course'], condition=models.Q(course__isnull=False), name='unique_course_review'),
            models.UniqueConstraint(fields=['customer', 'supplier'], condition=models.Q(supplier__isnull=False), name='unique_supplier_review'),
            models.UniqueConstraint(fields=['customer', 'delivery'], condition=models.Q(delivery__isnull=False), name='unique_delivery_review'),
        ]