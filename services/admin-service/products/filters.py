from django.contrib.postgres.search import SearchVector
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="UnitPrice", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="UnitPrice", lookup_expr='lte')
    rating = django_filters.NumberFilter(field_name="Rating", lookup_expr='gte') 
    supplier_name = django_filters.CharFilter(field_name="Supplier__user__first_name", lookup_expr='icontains', label='Supplier Name')
    
    class Meta:
        model = Product
        fields = ['Category', 'Supplier', 'min_price', 'max_price', 'rating', 'supplier_name'] 