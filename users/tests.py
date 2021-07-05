from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from urllib.parse import urlencode

from articles.models import Article
from authenticate.models import Relation

# Create your tests here.

User = get_user_model()


class PostedArticleListView(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='posted_view',
                                 email='posted_view@test.com',
                                 password='t0pp0gev1ew')
        user = User.objects.get(username='posted_view')
        for i in range(1, 7):
            Article.objects.create(author=user,
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
            article = Article.objects.filter(title='test_title{}'.format(i))[0]
            article.save()

        return super().setUpClass()

    # posted_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:articles',
                                           kwargs={'username': 'posted_view'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:articles',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:articles',
                                           kwargs={'username': 'posted_view'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:articles',
                                                     kwargs={'username': 'posted_view'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:articles',
                                           kwargs={'username': 'posted_view'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class FavoriteListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='favorite_list_view',
                                 email='favorite_list_view@test.com',
                                 password='t0pp0gev1ew')
        user = User.objects.get(username='favorite_list_view')
        for i in range(1, 7):
            Article.objects.create(author=User.objects.first(),
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
            article = Article.objects.filter(title='test_title{}'.format(i))[0]
            article.favorite_users.add(user)
            article.save()

        return super().setUpClass()

    # favorite_list_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:favorites',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:favorites',
                                             kwargs={'username': 'favorite_list_view'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class FolloweesList(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='followee_tester_{}'.format(i),
                                     email='followee_tester_{}@test.com'.format(i),
                                     password='f0ll0weetester')

        user1 = User.objects.filter(username='followee_tester_1').get()
        for i in range(2, 11):
            followee = User.objects.filter(username='followee_tester_{}'.format(i)).get()
            Relation.objects.create(followee=followee, follower=user1)

        return super().setUpClass()

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

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:followees',
                                             kwargs={'username': 'followee_tester_1'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)
