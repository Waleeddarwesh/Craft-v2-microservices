from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category, MatCategory, Collection

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('Title', 'Description')

@register(MatCategory)
class MatCategoryTranslationOptions(TranslationOptions):
    fields = ('Title',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('ProductName', 'ProductDescription')

@register(Collection)
class CollectionTranslationOptions(TranslationOptions):
    fields = ('name',)
