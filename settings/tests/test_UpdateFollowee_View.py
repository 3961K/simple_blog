from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urlencode

from authenticate.models import Relation

User = get_user_model()


class UpdateFolloweeViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(1, 11):
            User.objects.create_user(username='ufvtester{}'.format(i),
                                     email='ufvtester{}@test.com'.format(i),
                                     password='ufvtester0721')

        user1 = User.objects.filter(username='ufvtester1').get()
        for i in range(2, 11):
            followee = User.objects.get(username='ufvtester{}'.format(i))
            Relation.objects.create(followee=followee, follower=user1)

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
