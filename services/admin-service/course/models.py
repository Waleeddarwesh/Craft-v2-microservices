from django.db import models
from accounts.models import Supplier,User,Customer
from products.models import Category
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from Handcrafts.utils.translation import translate_text

class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    Thumbnail = models.ImageField(upload_to='course_thumbnails/%Y/%m/%d', blank=True, null=True)
    CourseTitle = models.CharField(max_length=100)
    CategoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    Rating =  models.DecimalField(max_digits=10, decimal_places=2,default= 5.0,validators=(MinValueValidator(0.0), MaxValueValidator(5.0))) 
    completed = models.BooleanField(default=False)
    NumberOfRatings = models.IntegerField(default=0)
    FromDate = models.DateTimeField(blank=True, null=True)
    ToDate = models.DateTimeField(blank=True, null=True)
    CourseHours = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    NumberOfLec = models.IntegerField(default=0,blank=True, null=True)
    NumberOfUploadedLec = models.IntegerField(default=0,blank=True, null=True)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Description = models.TextField()
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True,null=True,related_name='sub', db_column='supplier_id')
    
    def __str__(self):
        return f"{self.CourseTitle}"

    def update_rating(self):
        avg_rating = self.course_rating.aggregate(models.Avg('rating'))['rating__avg']
        self.Rating = avg_rating if avg_rating is not None else 0
        self.save()
    
class CourseVideos(models.Model):
    VideoID = models.AutoField(primary_key=True)
    CourseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    LectureTitle = models.CharField(max_length=100)
    VideoNo = models.IntegerField()
    Description = models.TextField()
    VideoFile = models.FileField(upload_to='videos/%y/%m/%d')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['CourseID', 'VideoNo'], name='unique_lecture_per_course')
        ]

    def __str__(self):
        return f"{self.LectureTitle}"

class Enrollment(models.Model):
    EnrollmentID = models.AutoField(primary_key=True)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    EnrolledUser = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    EnrollmentDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Course', 'EnrolledUser'], name='unique_enrollment')
        ]

    def __str__(self):
        return f"Enrollment ID: {self.EnrollmentID}, Course: {self.Course.CourseTitle}"

@receiver(pre_save, sender=Course)
def auto_translate_course(sender, instance, **kwargs):
    if not instance.CourseTitle_ar and instance.CourseTitle_en:
        instance.CourseTitle_ar = translate_text(instance.CourseTitle_en, source='en', target='ar')
    elif not instance.CourseTitle_en and instance.CourseTitle_ar:
        instance.CourseTitle_en = translate_text(instance.CourseTitle_ar, source='ar', target='en')

    if not instance.Description_ar and instance.Description_en:
        instance.Description_ar = translate_text(instance.Description_en, source='en', target='ar')
    elif not instance.Description_en and instance.Description_ar:
        instance.Description_en = translate_text(instance.Description_ar, source='ar', target='en')

    if not instance.address_ar and instance.address_en:
        instance.address_ar = translate_text(instance.address_en, source='en', target='ar')
    elif not instance.address_en and instance.address_ar:
        instance.address_en = translate_text(instance.address_ar, source='ar', target='en')

@receiver(pre_save, sender=CourseVideos)
def auto_translate_coursevideo(sender, instance, **kwargs):
    if not instance.LectureTitle_ar and instance.LectureTitle_en:
        instance.LectureTitle_ar = translate_text(instance.LectureTitle_en, source='en', target='ar')
    elif not instance.LectureTitle_en and instance.LectureTitle_ar:
        instance.LectureTitle_en = translate_text(instance.LectureTitle_ar, source='ar', target='en')

    if not instance.Description_ar and instance.Description_en:
        instance.Description_ar = translate_text(instance.Description_en, source='en', target='ar')
    elif not instance.Description_en and instance.Description_ar:
        instance.Description_en = translate_text(instance.Description_ar, source='ar', target='en')