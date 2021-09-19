from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urlencode

from ..models import Tag, Article

User = get_user_model()


class ArticleListViewTest(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='articles_view',
                                 email='articles_view@test.com',
                                 password='t0pp0gev1ew')
        for i in range(1, 6):
            Article.objects.create(author=User.objects.first(),
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))

        Tag.objects.create(tag='sample')
        tag = Tag.objects.get(tag='sample')
        User.objects.create_user(username='tag_articles_view',
                                 email='tag_articles_view@test.com',
                                 password='t0pp0gev1ew')
        for i in range(1, 6):
            Article.objects.create(author=User.objects.first(),
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
            article = Article.objects.filter(title='test_title{}'.format(i))[0]
            article.tags.add(tag)
            article.save()

    # トップページにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('articles:articles'))
        self.assertEqual(response.status_code, 200)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('articles:articles'),
                                             '?',
                                             urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6にアクセスする事が出来ない
    def test_success_access_page3(self):
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?',
                                            urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)

    # sampleカテゴリの記事を表示するページを表示する事が出来る
    def test_success_fetch_page_with_tag(self):
        article_tag = Tag.objects.get(tag='sample')
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?',
                                            urlencode(dict(tag=article_tag.pk))]))
        self.assertEqual(response.status_code, 200)

    # 存在しないカテゴリの記事一覧ページを取得しようとすると404が返ってくる
    def test_success_fetch_not_exist_tag(self):
        article_tag = Tag.objects.last()
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?tag=',
                                            urlencode(dict(tag=article_tag.pk + 1))]))
        self.assertEqual(response.status_code, 404)

    # test_titleという文字列がタイトル・内容に含まれている記事の一覧ページを取得する
    def test_success_fetch_keyword(self):
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?',
                                            urlencode(dict(keyword='test_title'))]))
        self.assertEqual(response.status_code, 200)

    # タイトル・内容に含まれていない文字列では結果を取得する事が出来ず,404が返ってくる
    def test_fail_fetch_not_exist_keyword(self):
        response = self.client.get(''.join([reverse('articles:articles'),
                                            '?',
                                            urlencode(dict(keyword='not_exist_keyword'))]))
        self.assertEqual(response.status_code, 404)
