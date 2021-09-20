from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.urls import reverse

from articles.models import Article, Tag

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class DeleteArticleViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='deletearticleview_tester',
                                 email='deletearticleview@test.com',
                                 password='postarticle0123')
        User.objects.create_user(username='deletearticleview_tester2',
                                 email='deletearticleview2@test.com',
                                 password='postarticle0123')

        user = User.objects.get(username='deletearticleview_tester')
        user2 = User.objects.get(username='deletearticleview_tester2')

        Tag.objects.create(tag='deletearticleview_test_tag')
        article_tag = Tag.objects.get(tag='deletearticleview_test_tag')

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

    # GETリクエストによるHTTPアクセスはリダイレクトされる
    def test_success_redirect(self):
        self.client.login(username='deletearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.get(reverse('settings:deletearticle',
                                           kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)

    # 作者としてログインしている状態でPOSTリクエストを送信する事で削除する事ができる
    def test_success_delete_login_as_author(self):
        self.client.login(username='deletearticleview_tester',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            Article.objects.filter(title='test_title', author=author).get()

    # 作者ではないユーザとしてログインしている場合はPOSTリクエストを送信しても削除する事は出来ない
    def test_fail_delete_login_as_other(self):
        self.client.login(username='deletearticleview_tester2',
                          password='postarticle0123')
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 403)

    # ログインしていない場合はPOSTリクエストを送信しても削除する事は出来ない
    def test_fail_delete_without_login(self):
        author = User.objects.get(username='deletearticleview_tester')
        article = Article.objects.filter(title='test_title', author=author).get()
        response = self.client.post(reverse('settings:deletearticle',
                                            kwargs={'pk': article.pk}))
        self.assertEquals(response.status_code, 302)
