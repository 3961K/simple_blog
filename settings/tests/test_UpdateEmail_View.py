from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UpdateEmailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='uev_tester',
                                 email='uevtest@test.com',
                                 password='uevtester0512')
        User.objects.create_user(username='uev_tester2',
                                 email='uevtest2@test.com',
                                 password='uevtester0512')

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:email'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:email'))
        self.assertEqual(response.status_code, 200)

    # 既存のメールアドレスでは更新する事が出来ない
    def test_fail_update_diplicated_username(self):
        err_message = "この メールアドレス を持った ユーザー が既に存在します。"

        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)

        post_data = {
            'email': 'uevtest2@test.com'
        }
        response = self.client.post(reverse('settings:email'),
                                    post_data,
                                    format='text/html')
        self.assertContains(response, err_message)

    # 新たなユーザ名によってユーザ名を更新する事が出来る
    def test_success_update_username(self):
        user = User.objects.get(username='uev_tester')
        self.client.force_login(user)

        post_data = {
            'email': 'uevtest3@test.com'
        }
        response = self.client.post(reverse('settings:email'),
                                    post_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

        # ユーザ名が同一であるかによってがメールアドレス変更されたか確認する
        user = User.objects.get(email='uevtest3@test.com')
        self.assertEquals(user.username, 'uev_tester')
