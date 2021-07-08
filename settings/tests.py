from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urlencode

from .forms import UpdateUsernameForm, UpdateEmailForm
from authenticate.models import Relation

# Create your tests here.
User = get_user_model()


class UpdateUsernameFormTest(TestCase):
    # 30文字以内の文字列はユーザ名として妥当である
    def test_valid(self):
        correct_data = {
            'username': 'A' * 30
        }
        form = UpdateUsernameForm(correct_data)
        self.assertTrue(form.is_valid())

    # 31文字以上の文字列及び空文字はユーザ名として妥当でない
    def test_invalid(self):
        wrong_data_list = [
            {
                'username': 'A' * 31
            },
            {
                'username': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateUsernameForm(wrong_data)
            self.assertFalse(form.is_valid())


class UpdateUsernameViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='uuv_tester',
                                 email='uuv_test@test.com',
                                 password='uuvtester0512')
        User.objects.create_user(username='uuv_tester2',
                                 email='uuv_test2@test.com',
                                 password='uuvtester0512')
        return super().setUpClass()

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


class UpdateEmailFormTest(TestCase):
    # 一般的なメールアドレスに近しい文字列はメールアドレスとして妥当である
    def test_valid(self):
        correct_data = {
            'email': 'ueftest@test.com'
        }
        form = UpdateEmailForm(correct_data)
        self.assertTrue(form.is_valid())

    # 一般的なメールアドレスからかけ離れている文字列と空文字はメールアドレスとして妥当である
    def test_invalid(self):
        wrong_data_list = [
            {
                'email': 'A'
            },
            {
                'email': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateEmailForm(wrong_data)
            self.assertFalse(form.is_valid())


class UpdateEmailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='uev_tester',
                                 email='uevtest@test.com',
                                 password='uevtester0512')
        User.objects.create_user(username='uev_tester2',
                                 email='uevtest2@test.com',
                                 password='uevtester0512')
        return super().setUpClass()

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


class UpdateFolloweeViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='ufvtester{}'.format(i),
                                     email='ufvtester{}@test.com'.format(i),
                                     password='ufvtester0721')

        user1 = User.objects.filter(username='ufvtester1').get()
        for i in range(2, 11):
            followee = User.objects.get(username='ufvtester{}'.format(i))
            Relation.objects.create(followee=followee, follower=user1)

        return super().setUpClass()

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:followees'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:followees'))
        self.assertEqual(response.status_code, 200)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        user = User.objects.get(username='ufvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followees'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)
