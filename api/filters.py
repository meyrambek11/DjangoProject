from django_filters import rest_framework as filters

from api.models import Product


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='contains')
    price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(lookup_expr='exact')
    # shopName = filters.

    class Meta:
        model = Product
        fields = ('name', 'price', 'category',)
