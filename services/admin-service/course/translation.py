from modeltranslation.translator import register, TranslationOptions
from .models import Course, CourseVideos

@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ('CourseTitle', 'Description', 'address')

@register(CourseVideos)
class CourseVideosTranslationOptions(TranslationOptions):
    fields = ('LectureTitle', 'Description')
