from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class DeleteUserViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='delete_user_view',
                                 email='deleteuserview@test.com',
                                 password='delete0123')

    # ログインしている状態でアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='delete_user_view',
                          password='delete0123')
        response = self.client.get(reverse('settings:deleteuser'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access(self):
        response = self.client.get(reverse('settings:deleteuser'))
        self.assertEqual(response.status_code, 302)

    # ログインしている状態でPOSTリクエストを送信する事でそのユーザを削除する
    def test_success_delete(self):
        self.client.login(username='delete_user_view',
                          password='delete0123')
        response = self.client.post(reverse('settings:deleteuser'))

        self.assertEqual(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username='delete_user_view')
