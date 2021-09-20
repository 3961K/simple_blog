from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urlencode

from authenticate.models import Relation

User = get_user_model()


class UpdateFollowerViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(1, 11):
            User.objects.create_user(username='ufrvtester{}'.format(i),
                                     email='ufrvtester{}@test.com'.format(i),
                                     password='ufrvtester0721')

        user1 = User.objects.filter(username='ufrvtester1').get()
        for i in range(2, 11):
            follower = User.objects.get(username='ufrvtester{}'.format(i))
            Relation.objects.create(followee=user1, follower=follower)

    # ログインしていない場合は302が返される
    def test_redirect_nologin(self):
        response = self.client.get(reverse('settings:followers'))
        self.assertEqual(response.status_code, 302)

    # ログインしている場合は200を返される
    def test_success_access(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)
        response = self.client.get(reverse('settings:followers'))
        self.assertEqual(response.status_code, 200)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        user = User.objects.get(username='ufrvtester1')
        self.client.force_login(user)

        response = self.client.get(''.join([reverse('settings:followers'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)
