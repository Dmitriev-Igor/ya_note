from http import HTTPStatus

from django.contrib.auth import get_user_model
from .base_test_case import BaseTestCase

User = get_user_model()


class TestRoutes(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.add_url,
            self.list_url,
            self.success_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def check_status_code(self, url, client, expected_status):
        response = client.get(url)
        self.assertEqual(response.status_code, expected_status)

    def test_pages_availability(self):
        for name in (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url
        ):
            with self.subTest(name=name):
                self.check_status_code(name, self.client, HTTPStatus.OK)

    def test_authenticated_user_access(self):
        for name in (self.list_url, self.add_url, self.success_url):
            with self.subTest(name=name):
                self.check_status_code(name, self.author_client, HTTPStatus.OK)

    def test_note_access_for_users(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (self.edit_url, self.delete_url):
                with self.subTest(user=user, name=name):
                    response = user.get(name)
                    self.assertEqual(response.status_code, status)
