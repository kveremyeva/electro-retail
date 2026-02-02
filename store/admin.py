from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Provider, Product, Contact


class CityFilter(admin.SimpleListFilter):
    title = 'Город'
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = Contact.objects.values_list('city', flat=True).distinct()
        return [(city, city) for city in cities]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contact_info__city=self.value())
        return queryset


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_node_type_display',
        'get_supplier_link',
        'get_city',
        'debt_to_supplier',
        'created_at'
    ]

    list_filter = [
        CityFilter,
        'contact_info__country',
    ]

    search_fields = ['name', 'contact_info__city']

    actions = ['clear_debt']

    def clear_debt(self, request, queryset):
        """Admin action для очистки задолженности"""
        queryset.update(debt_to_supplier=0)
        self.message_user(request, f'Задолженность очищена у {queryset.count()} объектов')

    clear_debt.short_description = 'Очистить задолженность перед поставщиком'

    def get_supplier_link(self, obj):
        """Ссылка на поставщика"""
        if obj.supplier:
            url = reverse('admin:store_provider_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return 'Нет поставщика'

    get_supplier_link.short_description = 'Поставщик'

    def get_city(self, obj):
        """Город для отображения в списке"""
        return obj.contact_info.city if obj.contact_info else '-'

    get_city.short_description = 'Город'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'country', 'city']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_model', 'release_date']
