from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from urllib.parse import urlencode

from articles.models import Article

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class PostedArticleListView(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='pavtester',
                                 email='pavtester@test.com',
                                 password='pavtester0123')
        user = User.objects.get(username='pavtester')
        for i in range(1, 7):
            article = Article(author=user,
                              title='test_title{}'.format(i),
                              content='test_content{}'.format(i))
            article.save()

    # ログインしている状態でビューにアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(reverse('settings:postedarticles'))
        self.assertEqual(response.status_code, 200)

    # ログインしていない状態ではビューにアクセスする事が出来ない
    def test_fail_access_not_logined(self):
        response = self.client.get(reverse('settings:postedarticles'))
        self.assertEqual(response.status_code, 302)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(''.join([reverse('settings:postedarticles'),
                                            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('settings:postedarticles'),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page12(self):
        self.client.login(username='pavtester',
                          password='pavtester0123')
        response = self.client.get(''.join([reverse('settings:postedarticles'),
                                            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)
