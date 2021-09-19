from django.test import TestCase
from django.urls import reverse

from ..models import User


class LoginViewTest(TestCase):
    # ログイン用のユーザを作成
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='loginviewtester',
                                 email='loginview@test.com',
                                 password='l0g1nt3st3r')

    # ログインビューにアクセスする事が出来る
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:login'))
        self.assertEqual(response.status_code, 200)

    # 正しいユーザ名・パスワードの組み合わせを用いてログインする事が出来る
    def test_success_login(self):
        login_data = {
            'username': 'loginviewtester',
            'password': 'l0g1nt3st3r'
        }
        response = self.client.post(reverse('authenticate:login'),
                                    login_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # 正しくないユーザ名・パスワードの組み合わせではログインする事が出来ず,
    # 4回目のログイン失敗によってアカウントがロックされる
    def test_fail_login(self):
        err_message = '正しいユーザー名とパスワードを入力してください。'\
            'どちらのフィールドも大文字と小文字は区別されます。'

        wrong_value_list = [
            ['loginviewtester', 'wrongpassword'],
            ['wrongusername', 'l0g1nt3st3r'],
            ['wrongusername', 'wrongpassword']
        ]

        for wrong_value in wrong_value_list:
            response = self.client.post(reverse('authenticate:login'),
                                        {'username': wrong_value[0],
                                        'password': wrong_value[1]},
                                        format='text/html')
            self.assertContains(response, err_message)

        # 4回目においてアカウントロックが行われる
        forth_response = self.client.post(reverse('authenticate:login'),
                                          {'username': wrong_value[0],
                                           'password': wrong_value[1]},
                                          format='text/html')

        self.assertEquals(forth_response.status_code, 403)
