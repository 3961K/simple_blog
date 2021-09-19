from django.test import TestCase
from django.urls import reverse


class LogoutViewTest(TestCase):
    # ログアウトページ自体に対するアクセスが可能か確認するテスト
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:logout'))
        self.assertEqual(response.status_code, 302)
