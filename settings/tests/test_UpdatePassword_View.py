from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class UpdatePasswordViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='update_password_view',
                                 email='updatepasswordview@test.com',
                                 password='update0123')

    # ログインしている状態でアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        response = self.client.get(reverse('settings:password'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access(self):
        response = self.client.get(reverse('settings:password'))
        self.assertEqual(response.status_code, 302)

    # 正しい形式の新しいパスワードによって更新する事が出来る
    def test_success_update(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        update_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        response = self.client.post(reverse('settings:password'),
                                    update_data, format='text/html')
        self.assertEqual(response.status_code, 302)

    # 現在のパスワードが間違っている場合は更新出来ない
    def test_fail_update_wrong_password(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        wrong_password_data = {
            'old_password': 'wrong_password',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        response = self.client.post(reverse('settings:password'),
                                    wrong_password_data, format='text/html')
        self.assertNotEqual(response.status_code, 302)

    # 1つ目と2つ目の新しいパスワードが一致しない場合は更新出来ない
    def test_fail_update_missmatched_password(self):
        self.client.login(username='update_password_view',
                          password='update0123')
        missmatched_password = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated01234',
        }
        response = self.client.post(reverse('settings:password'),
                                    missmatched_password, format='text/html')
        self.assertNotEqual(response.status_code, 302)
