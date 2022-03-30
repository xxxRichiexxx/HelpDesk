from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class IndexTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create(username='test_user')

    def setUp(self):
        self.auth_client = Client()
        self.guest_client = Client()
        self.auth_client.force_login(self.auth_user)

    def test_auth_index(self):
        response = self.auth_client.get('/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Главная страница не работает.'
        )

    def test_guest_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            f'главная страница не возвращает должный код под гостем.',
        )