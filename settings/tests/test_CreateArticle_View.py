from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from articles.models import Article, Tag

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class CreateArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='create_article_view',
                                 email='create_article_view@test.com',
                                 password='createart1cle')
        Tag.objects.create(tag='create_article_view_test')

    # ログインしている状態でビューにアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='create_article_view',
                          password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではビューにアクセスする事が出来ない
    def test_fail_access_not_logined(self):
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 302)

    # 正しい形式のタイトル・内容で記事を登録する事が出来る
    def test_success_post_article(self):
        self.client.login(username='create_article_view',
                          password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

        article_tag = Tag.objects.get(tag='create_article_view_test')
        article_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [article_tag.pk]
        }
        post_response = self.client.post(reverse('settings:newarticle'),
                                         article_data,
                                         format='text/html')
        self.assertEqual(post_response.status_code, 302)

        posted_article = Article.objects.get(title='A' * 1000)
        self.assertIsNotNone(posted_article)

    # 誤った形式のタイトル・内容では記事を登録する事が出来ない
    def test_fail_post_article_wrongformat(self):
        self.client.login(username='create_article_view', password='createart1cle')
        response = self.client.get(reverse('settings:newarticle'))
        self.assertEqual(response.status_code, 200)

        article_tag = Tag.objects.get(tag='create_article_view_test')
        wrong_format_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'A' * 10000,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1000,
                'content': 'A' * 10001,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001,
                'tags': []
            }
        ]

        for wrong_format_data in wrong_format_data_list:
            post_response = self.client.post(reverse('settings:newarticle'),
                                             wrong_format_data,
                                             format='text/html')
            self.assertEqual(post_response.status_code, 200)
