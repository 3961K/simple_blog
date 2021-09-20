from django.test import TestCase
from django.urls import reverse

from ..models import User


class RegisterViewTest(TestCase):
    # ユーザ登録ページにアクセス出来る
    def test_success_access(self):
        response = self.client.get(reverse('authenticate:register'))
        self.assertEqual(response.status_code, 200)

    # 必須フィールドのみ入力する事でユーザ登録する事が出来る
    def test_success_register(self):
        register_info = {
            'username': 'viewtester',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    register_info,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # 誤った形式のユーザ名・メールアドレスでは登録する事が出来ない
    def test_fail_register_wrongformat(self):
        err_message_username = 'この値は 30 文字以下でなければなりません'
        err_message_email = '有効なメールアドレスを入力してください。'

        wrong_format_username = {
            'username': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    wrong_format_username,
                                    format='text/html')
        self.assertContains(response, err_message_username)

        wrong_format_email = {
            'username': 'viewtester',
            'email': 'viewtester@a.a',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    wrong_format_email,
                                    format='text/html')
        self.assertContains(response, err_message_email)

    # 既に登録済みのユーザ名・メールアドレスでは登録する事が出来ない
    def test_fail_register_duplicated(self):
        User.objects.create_user(username='viewtester',
                                 email='viewtester@test.com',
                                 password='v1ewt3st3r1234')

        err_message_duplicated_username = '同じユーザー名が既に登録済みです。'
        duplicated_username = {
            'username': 'viewtester',
            'email': 'viewtester2@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    duplicated_username,
                                    format='text/html')
        self.assertContains(response, err_message_duplicated_username)

        err_message_duplicated_email = 'この メールアドレス を持った ユーザー '\
            'が既に存在します。'
        duplicated_email = {
            'username': 'viewtester2',
            'email': 'viewtester@test.com',
            'password1': 'v1ewt3st3r1234',
            'password2': 'v1ewt3st3r1234',
        }
        response = self.client.post(reverse('authenticate:register'),
                                    duplicated_email,
                                    format='text/html')
        self.assertContains(response, err_message_duplicated_email)
