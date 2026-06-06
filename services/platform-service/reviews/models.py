from django.db import models

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

    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=255, default='')
    
    product_id = models.BigIntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255, default='')
    
    course_id = models.BigIntegerField(null=True, blank=True)
    course_name = models.CharField(max_length=255, default='')
    
    delivery_id = models.BigIntegerField(null=True, blank=True)
    supplier_id = models.BigIntegerField(null=True, blank=True)
    
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
            models.UniqueConstraint(fields=['user_id', 'product_id'], condition=models.Q(product_id__isnull=False), name='unique_product_review'),
            models.UniqueConstraint(fields=['user_id', 'course_id'], condition=models.Q(course_id__isnull=False), name='unique_course_review'),
            models.UniqueConstraint(fields=['user_id', 'supplier_id'], condition=models.Q(supplier_id__isnull=False), name='unique_supplier_review'),
            models.UniqueConstraint(fields=['user_id', 'delivery_id'], condition=models.Q(delivery_id__isnull=False), name='unique_delivery_review'),
        ]