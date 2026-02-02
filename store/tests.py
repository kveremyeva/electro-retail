from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Contact, Product, Provider


class ModelTests(TestCase):
    """Тесты моделей"""

    def test_create_factory(self):
        """Тест создания завода (уровень 0)"""
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        provider = Provider.objects.create(
            name='Завод',
            contact_info=contact
        )
        self.assertEqual(provider.hierarchy_level, 0)
        self.assertEqual(provider.node_type, Provider.NodeType.FACTORY)

    def test_hierarchy_levels(self):
        """Тест иерархии уровней"""
        contact1 = Contact.objects.create(
            email='factory@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        contact2 = Contact.objects.create(
            email='retail@example.com',
            country='Россия',
            city='Санкт-Петербург',
            street='Невский',
            house='2'
        )

        contact3 = Contact.objects.create(
            email='ip@example.com',
            country='Россия',
            city='Казань',
            street='Баумана',
            house='3'
        )

        factory = Provider.objects.create(
            name='Завод',
            contact_info=contact1
        )

        retail = Provider.objects.create(
            name='Розничная сеть',
            contact_info=contact2,
            supplier=factory
        )

        entrepreneur = Provider.objects.create(
            name='ИП',
            contact_info=contact3,
            supplier=retail
        )

        self.assertEqual(factory.hierarchy_level, 0)
        self.assertEqual(retail.hierarchy_level, 1)
        self.assertEqual(entrepreneur.hierarchy_level, 2)
        self.assertEqual(retail.node_type, Provider.NodeType.RETAIL_NETWORK)
        self.assertEqual(entrepreneur.node_type, Provider.NodeType.INDIVIDUAL_ENTREPRENEUR)


class AdminTests(TestCase):
    """Тесты админ-панели"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')

    def test_admin_provider_list(self):
        """Тест отображения поставщиков в админке"""
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        Provider.objects.create(
            name='Тестовый поставщик',
            contact_info=contact
        )

        url = reverse('admin:store_provider_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый поставщик')

    def test_admin_clear_debt_action(self):
        """Тест admin action для очистки задолженности"""
        contact = Contact.objects.create(
            email='debt@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        provider = Provider.objects.create(
            name='Поставщик с долгом',
            contact_info=contact,
            debt_to_supplier=1000.50
        )

        data = {
            'action': 'clear_debt',
            '_selected_action': [provider.id]
        }

        url = reverse('admin:store_provider_changelist')
        response = self.client.post(url, data, follow=True)

        provider.refresh_from_db()
        self.assertEqual(provider.debt_to_supplier, 0)
        self.assertEqual(response.status_code, 200)


class APITests(APITestCase):
    """Тесты API"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            is_active=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_api_requires_auth(self):
        """Тест, что API требует аутентификации"""
        client = APIClient()  # Неаутентифицированный клиент
        url = reverse('provider-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_provider_list(self):
        """Тест получения списка поставщиков"""
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        Provider.objects.create(
            name='Тестовый поставщик',
            contact_info=contact
        )

        url = reverse('provider-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_country(self):
        """Тест фильтрации по стране"""
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        Provider.objects.create(
            name='Российский поставщик',
            contact_info=contact
        )

        url = reverse('provider-list')
        response = self.client.get(url, {'country': 'Россия'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cannot_update_debt_via_api(self):
        """Тест, что нельзя обновить задолженность через API"""
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        provider = Provider.objects.create(
            name='Поставщик',
            contact_info=contact,
            debt_to_supplier=100.00
        )

        url = reverse('provider-detail', args=[provider.id])
        data = {
            'name': 'Обновленный',
            'debt_to_supplier': 0  # Попытка изменить задолженность
        }

        response = self.client.patch(url, data, format='json')
        provider.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Долг не должен измениться
        self.assertEqual(provider.debt_to_supplier, 100.00)

    def test_provider_crud(self):
        """Тест полного CRUD цикла для поставщика"""
        # Создаем необходимые объекты
        contact = Contact.objects.create(
            email='test@example.com',
            country='Россия',
            city='Москва',
            street='Ленина',
            house='1'
        )

        product = Product.objects.create(
            name='Телефон',
            product_model='X100',
            release_date='2024-01-01'
        )

        # CREATE
        url = reverse('provider-list')
        data = {
            'name': 'Новый поставщик',
            'node_type': 0,
            'contact_info': contact.id,
            'products': [product.id],
            'debt_to_supplier': 0
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        provider_id = response.data['id']

        # READ
        url = reverse('provider-detail', args=[provider_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Новый поставщик')

        # UPDATE
        data = {'name': 'Обновленное имя'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_inactive_user_cannot_access(self):
        """Тест, что неактивный пользователь не может получить доступ"""
        inactive_user = User.objects.create_user(
            username='inactive',
            password='testpass',
            is_active=False
        )

        client = APIClient()
        client.force_authenticate(user=inactive_user)

        url = reverse('provider-list')
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PermissionTests(TestCase):
    """Тесты прав доступа"""

    def test_is_active_employee_permission(self):
        """Тест permission IsActiveEmployee"""
        from .permissions import IsActiveEmployee

        permission = IsActiveEmployee()

        # Создаем мок-объекты
        class MockUser:
            def __init__(self, is_active, is_authenticated):
                self.is_active = is_active
                self.is_authenticated = is_authenticated

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Активный пользователь
        active_user = MockUser(is_active=True, is_authenticated=True)
        request = MockRequest(active_user)
        self.assertTrue(permission.has_permission(request, None))

        # Неактивный пользователь
        inactive_user = MockUser(is_active=False, is_authenticated=True)
        request = MockRequest(inactive_user)
        self.assertFalse(permission.has_permission(request, None))

        # Неаутентифицированный пользователь
        unauth_user = MockUser(is_active=True, is_authenticated=False)
        request = MockRequest(unauth_user)
        self.assertFalse(permission.has_permission(request, None))
