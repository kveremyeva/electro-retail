from django_filters import rest_framework as filters
from .models import Provider


class ProviderFilter(filters.FilterSet):
    country = filters.CharFilter(field_name='contact_info__country')

    class Meta:
        model = Provider
        fields = ['country']
