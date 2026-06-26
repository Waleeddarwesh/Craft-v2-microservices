from celery import shared_task
from django.shortcuts import get_object_or_404
from notifications.services import create_notification_for_user
from .models import Course, Enrollment
from accounts.models import User, Follow

@shared_task
def create_course_task(supplier_id, course_data):
    """
    Asynchronously creates a course and notifies the supplier's followers.
    """
    from .serializers import CourseSerializer
    
    supplier = get_object_or_404(User, id=supplier_id).supplier
    serializer = CourseSerializer(data=course_data)
    
    if serializer.is_valid():
        course = serializer.save(Supplier=supplier)
        
        followers = Follow.objects.filter(supplier=supplier)
        for follow in followers:
            if hasattr(follow.follower, 'user'):
                message = f"Your followed supplier {supplier.user.get_full_name} has a new course: {course.CourseTitle}"
                create_notification_for_user(
                    user=follow.follower.user,
                    message=message,
                    related_object=course,
                    image=course.Thumbnail
                )

@shared_task
def create_enrollment_task(course_id, user_id):
    """
    Asynchronously enrolls a user in a course and sends a notification.
    """
    course = get_object_or_404(Course, pk=course_id)
    user = get_object_or_404(User, pk=user_id)

    Enrollment.objects.create(Course=course, EnrolledUser=user)

    # Notify the supplier
    create_notification_for_user(
        user=course.Supplier.user,
        message=f"A new user, {user.get_full_name}, has enrolled in your course: {course.CourseTitle}.",
        related_object=course,
    )

@shared_task
def update_course_rating_task(course_id):
    """
    Asynchronously updates the average rating for a course.
    """
    try:
        course = Course.objects.get(CourseID=course_id)
        course.update_rating()
    except Course.DoesNotExist:
        pass