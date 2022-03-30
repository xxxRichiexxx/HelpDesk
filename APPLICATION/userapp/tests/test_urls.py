import datetime as dt

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from userapp.models import Service, Work, Request, ResponsibilityGroup

User = get_user_model()


class UserappUrlsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create(username='test_user')
        cls.service = Service.objects.create(Name='Тестовый сервис')
        cls.work = Work.objects.create(
            Name='Тестовая работа',
            IDService=cls.service,
            Type='Инцедент',
            Complexity=10,
            ReactionTime=dt.timedelta(minutes=60),
            TimeOfExecution=dt.timedelta(minutes=60),
        )
        cls.ResponsibilityGroup = ResponsibilityGroup.objects.create(
            Name='Тестовая группа',
            Default=True,
        )
        cls.request = Request.objects.create(
            IDWork=cls.work,
            Name='Тестовая заявка',
            Comment='Комментарий',
            IDResponsibilityGroup=cls.ResponsibilityGroup,
            IDAuthor=cls.auth_user
        )

    def setUp(self):
        self.auth_client = Client()
        self.guest_client = Client()
        self.auth_client.force_login(self.auth_user)

    def test_my_requests(self):
        urls = {
            '/user-app/my-requests/new/': HTTPStatus.OK,
            '/user-app/my-requests/in_work/': HTTPStatus.OK,
            '/user-app/my-requests/on_check': HTTPStatus.MOVED_PERMANENTLY,
            '/user-app/my-requests/lost/': HTTPStatus.OK,
            '/user-app/my-requests/completed/': HTTPStatus.OK,
        }
        for url, status in urls.items():
            with self.subTest(f'Страница с заявками пользователя не работает: {url}.'):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_i_executor(self):
        urls = {
            '/user-app/i_executor/new/': HTTPStatus.OK,
            '/user-app/i_executor/in_work/': HTTPStatus.OK,
            '/user-app/i_executor/on_check': HTTPStatus.MOVED_PERMANENTLY,
            '/user-app/i_executor/lost/': HTTPStatus.OK,
            '/user-app/i_executor/completed/': HTTPStatus.OK,
        }
        for url, status in urls.items():
            with self.subTest(f'Страница с заявками, в которых пользователь исполнитель, не работает: {url}.'):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_group_requests(self):
        urls = {
            '/user-app/group_requests/new/': HTTPStatus.OK,
            '/user-app/group_requests/in_work/': HTTPStatus.OK,
            '/user-app/group_requests/on_check': HTTPStatus.MOVED_PERMANENTLY,
            '/user-app/group_requests/lost/': HTTPStatus.OK,
            '/user-app/group_requests/completed/': HTTPStatus.OK,
        }
        for url, status in urls.items():
            with self.subTest(f'Страница с заявками группы не работает: {url}.'):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_requests_by_category(self):
        url = '/user-app/requests-by-category/'
        response = self.auth_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Страница с категориями заявок не работает: {url}.'
        )

    def test_all_requests(self):
        urls = {
            '/user-app/all_requests/new/': HTTPStatus.OK,
            '/user-app/all_requests/in_work/': HTTPStatus.OK,
            '/user-app/all_requests/on_check': HTTPStatus.MOVED_PERMANENTLY,
            '/user-app/all_requests/lost/': HTTPStatus.OK,
            '/user-app/all_requests/completed/': HTTPStatus.OK,
        }
        for url, status in urls.items():
            with self.subTest(f'Страница с всеми заявками не работает: {url}.'):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_request_info(self):
        url = f'/user-app/my-requests/new/{self.request.id}/info/?page=1'
        response = self.auth_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Страница с детализацией заявки не работает: {url}.'
        )

    def test_request_messages(self):
        url = f'/user-app/my-requests/new/{self.request.id}/messages/?page=1'
        response = self.auth_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Страница с перепиской по заявке не работает: {url}.'
        )

    def test_request_logs(self):
        url = f'/user-app/my-requests/new/{self.request.id}/logs/?page=1'
        response = self.auth_client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Страница с логами заявки не работает: {url}.'
        )

    def test_guest_user(self):
        urls = {
            '/user-app/my-requests/new/': HTTPStatus.FOUND,
            '/user-app/i_executor/new/': HTTPStatus.FOUND,
            '/user-app/group_requests/new/': HTTPStatus.FOUND,
            '/user-app/requests-by-category/': HTTPStatus.FOUND,
            '/user-app/all_requests/new/': HTTPStatus.FOUND,
        }
        for url, status in urls.items():
            with self.subTest(f'{url} не возвращает должный код под гостем.'):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)
