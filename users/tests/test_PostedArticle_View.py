from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from urllib.parse import urlencode

from articles.models import Article

User = get_user_model()


class PostedArticleListView(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
