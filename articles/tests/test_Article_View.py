from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Article

User = get_user_model()


class ArticleViewTest(TestCase):
    # 表示する記事を作成
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='article_view',
                                 email='article_view@test.com',
                                 password='art1clev1ew')
        for i in range(1, 6):
            Article.objects.create(author_id=User.objects.first().pk,
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))

    # 存在する記事へアクセスする事が出来る
    def test_success_access_page(self):
        for article in Article.objects.all():
            response = self.client.get(reverse('articles:article',
                                               kwargs={'pk': article.pk}))
            self.assertEqual(response.status_code, 200)

    # 存在しない記事へはアクセスする事が出来ない
    def test_fail_access_notexist_page(self):
        response = self.client.get(reverse('articles:article',
                                           kwargs={'pk': 10000}))
        self.assertEqual(response.status_code, 404)
