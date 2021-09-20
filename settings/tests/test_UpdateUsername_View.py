from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UpdateUsernameViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='uuv_tester',
                                 email='uuv_test@test.com',
                                 password='uuvtester0512')
        User.objects.create_user(username='uuv_tester2',
                                 email='uuv_test2@test.com',
                                 password='uuvtester0512')

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:username'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:username'))
        self.assertEqual(response.status_code, 200)

    # 既存のユーザ名では更新する事が出来ない
    def test_fail_update_diplicated_username(self):
        err_message = "同じユーザー名が既に登録済みです。"

        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)

        post_data = {
            'username': 'uuv_tester2'
        }
        response = self.client.post(reverse('settings:username'),
                                    post_data,
                                    format='text/html')
        self.assertContains(response, err_message)

    # 新たなユーザ名によってユーザ名を更新する事が出来る
    def test_success_update_username(self):
        user = User.objects.get(username='uuv_tester')
        self.client.force_login(user)

        post_data = {
            'username': 'uuv_tester3'
        }
        response = self.client.post(reverse('settings:username'),
                                    post_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

        # メールアドレスが同一であるかによってユーザ名が変更されたか確認する
        user = User.objects.get(username='uuv_tester3')
        self.assertEquals(user.email, 'uuv_test@test.com')
