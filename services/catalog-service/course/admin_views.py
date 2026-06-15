from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from craft_common.auth.permissions import HasRole
from django.db.models import Count
from .models import Course

class AdminCoursesView(APIView):
    permission_classes = [IsAuthenticated, HasRole("admin")]

    def get(self, request):
        courses = Course.objects.annotate(enrollments_count=Count('enrollments')).all().order_by('-CourseID')[:100]
        data = [{
            'CourseID': c.CourseID,
            'CourseTitle': getattr(c, 'CourseTitle_en', c.CourseTitle) or c.CourseTitle,
            'Thumbnail': c.Thumbnail.url if c.Thumbnail else None,
            'supplier_name': c.supplier_name,
            'enrollments_count': c.enrollments_count,
            'CourseHours': c.CourseHours,
            'Price': float(c.Price) if c.Price else 0.0,
            'Rating': float(c.Rating) if c.Rating else 0.0,
            'completed': getattr(c, 'completed', False)
        } for c in courses]
        return Response(data)
