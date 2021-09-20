from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from urllib.parse import urlencode

from authenticate.models import Relation

User = get_user_model()


class FolloweeListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(1, 11):
            User.objects.create_user(username='followee_tester_{}'.format(i),
                                     email='followee_tester_{}@test.com'.format(i),
                                     password='f0ll0weetester')

        user1 = User.objects.filter(username='followee_tester_1').get()
        for i in range(2, 11):
            followee = User.objects.filter(username='followee_tester_{}'.format(i)).get()
            Relation.objects.create(followee=followee, follower=user1)

    # favorite_list_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:followees',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)
