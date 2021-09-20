from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from articles.models import Article, Tag

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class UpdateArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='updatearticleview_tester',
                                 email='updatearticleview@test.com',
                                 password='postarticle0123')
        User.objects.create_user(username='updatearticleview_tester2',
                                 email='updatearticleview2@test.com',
                                 password='postarticle0123')

        user = User.objects.get(username='updatearticleview_tester')
        user2 = User.objects.get(username='updatearticleview_tester2')

        Tag.objects.create(tag='updatearticleview_test_tag')
        article_tag = Tag.objects.get(tag='updatearticleview_test_tag')

        Article.objects.create(author_id=user.pk, title='test_title',
                               content='test_content')
        article = Article.objects.filter(title='test_title').first()
        article.tags.add(article_tag)
        article.save()

        Article.objects.create(author_id=user2.pk, title='test_title2',
                               content='test_content2')
        article2 = Article.objects.filter(title='test_title2').first()
        article2.tags.add(article_tag)
        article2.save()

    # ログインしているユーザに関連している記事のページへアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access_notlogin(self):
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)

    # ログインをしている状態で存在しない記事のページへアクセスする事が出来ない
    def test_fail_access_notexist(self):
        self.client.login(username='updatearticleview_tester2',
                          password='postarticle0123')
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': 1000}))
        self.assertEquals(response.status_code, 404)

    # ログインしているユーザが作成していない記事のページへアクセスする事が出来ない
    def test_fail_access_notauthor(self):
        self.client.login(username='updatearticleview_tester2',
                          password='postarticle0123')
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': 1}))
        self.assertEquals(response.status_code, 403)

    # 正しい形式のタイトル・内容によって記事を変更する事が出来る
    def test_success_edit(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

        # タグの形式が間違っていると表示されている
        tag = Tag.objects.get(tag='updatearticleview_test_tag')
        edit_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [tag.pk],
        }
        response = self.client.post(reverse('settings:updatearticle',
                                            kwargs={'pk': article.pk}),
                                    edit_data, format='text/html')
        self.assertEquals(response.status_code, 302)

    # 誤った形式のタイトル・内容によって記事を変更する事が出来ない
    def test_fail_edit_wrongformat(self):
        self.client.login(username='updatearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='updatearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:updatearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 200)

        wrong_format_edit_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'sample_content'
            },
            {
                'title': 'sample_title',
                'content': 'A' * 10001
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001
            }
        ]
        for wrong_format_edit_data in wrong_format_edit_data_list:
            response = self.client.post(reverse('settings:updatearticle',
                                                kwargs={'pk': article.pk}),
                                        wrong_format_edit_data,
                                        format='text/html')
            self.assertEquals(response.status_code, 200)
