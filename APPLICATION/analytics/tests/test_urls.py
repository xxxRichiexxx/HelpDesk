from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class AnalyticsUrlsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create(username='test_user')

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.auth_user)

    def test_analytics(self):
        url = '/analytics/'
        response = self.auth_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Страница с аналитикой не работает: {url}.'
        )
