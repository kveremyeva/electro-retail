from django.core.validators import MinValueValidator
from django.db import models


class Contact(models.Model):
    """Контактная информация для всех звеньев сети"""
    email = models.EmailField(unique=True, verbose_name='Email')
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='Страна')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Город')
    street = models.CharField(max_length=50, blank=True, null=True, verbose_name='Улица')
    house = models.CharField(max_length=10, blank=True, null=True, verbose_name='Номер дома')

    def __str__(self):
        return f'{self.country}, {self.city}, {self.street}, {self.house}'

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'


class Product(models.Model):
    """Модель продукта"""
    name = models.CharField(max_length=255, verbose_name='Название')
    product_model = models.CharField(max_length=255, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода продукта')

    def __str__(self):
        return f'{self.name} ({self.product_model})'

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-release_date']


class Provider(models.Model):
    """Модель звена сети (завод, розничная сеть, ИП)"""

    class NodeType(models.IntegerChoices):
        FACTORY = 0, 'Завод'
        RETAIL_NETWORK = 1, 'Розничная сеть'
        INDIVIDUAL_ENTREPRENEUR = 2, 'Индивидуальный предприниматель'

    name = models.CharField(max_length=255, unique=True, verbose_name='Название звена')
    node_type = models.IntegerField(choices=NodeType.choices, default=NodeType.FACTORY, verbose_name='Тип звена')
    contact_info = models.OneToOneField(Contact, on_delete=models.CASCADE,
                                        related_name='network_node', verbose_name='Контактная информация')
    products = models.ManyToManyField(Product, related_name='network_nodes',
                                      blank=True, verbose_name='Продукты')
    supplier = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Поставщик',
                                 related_name='clients', null=True, blank=True)
    debt_to_supplier = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)],
                                           default=0, verbose_name='Задолженность перед поставщиком')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    hierarchy_level = models.PositiveIntegerField(default=0, editable=False, verbose_name='Уровень иерархии')

    class Meta:
        verbose_name = 'Звено сети'
        verbose_name_plural = 'Звенья сети'
        ordering = ['name']
        indexes = [
            models.Index(fields=['node_type']),
            models.Index(fields=['supplier']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        """Переопределяем save для вычисления уровня иерархии"""
        if self.supplier:
            self.hierarchy_level = self.supplier.hierarchy_level + 1
        else:
            self.hierarchy_level = 0

        if self.hierarchy_level == 0:
            self.node_type = self.NodeType.FACTORY
        elif self.hierarchy_level == 1:
            self.node_type = self.NodeType.RETAIL_NETWORK
        else:
            self.node_type = self.NodeType.INDIVIDUAL_ENTREPRENEUR

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_node_type_display()}: {self.name} (Уровень: {self.hierarchy_level})'

    def get_supplier_name(self):
        """Возвращает имя поставщика или None"""
        return self.supplier.name if self.supplier else 'Нет поставщика'

    @property
    def supplier_link(self):
        """Ссылка на поставщика для админ-панели"""
        if self.supplier:
            from django.urls import reverse
            return reverse('admin:store_provider_change', args=[self.supplier.id])
        return None
