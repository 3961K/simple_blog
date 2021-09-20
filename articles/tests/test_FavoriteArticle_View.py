from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Article

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class FavoriteArticleView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='fav_view_tester',
                            email='fav_view_tester@test.com',
                            password='favtester')

        User.objects.create(username='author',
                            email='author@test.com',
                            password='auth0r1234')
        author = User.objects.get(username='author')
        Article.objects.create(author=author,
                               title='test_title',
                               content='test_content')

    # GETメソッドを利用した場合は302が返される
    def test_fail_get_method(self):
        article = Article.objects.get(title='test_title')
        response = self.client.get(reverse('articles:favorite',
                                           kwargs={'pk': article.pk}))
        self.assertEqual(response.status_code, 302)

    # ログインせずにPOSTした場合は302が返される
    def test_fail_favorite_nologin(self):
        article = Article.objects.get(title='test_title')

        payload = {
            'username': 'fav_view_tester'
        }

        url = reverse('articles:favorite', kwargs={'pk': article.pk})
        response = self.client.post(url,
                                    payload,
                                    **{
                                        'Content-Type': 'application/json',
                                        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                    })
        self.assertEqual(response.status_code, 302)

    # ログインを行った状態でAjaxリクエストを送信するとお気に入りに追加・削除する事が出来る
    def test_success_favorite(self):
        import json

        article = Article.objects.get(title='test_title')

        user = User.objects.get(username='fav_view_tester')
        payload = {
            'username': 'fav_view_tester'
        }

        url = reverse('articles:favorite', kwargs={'pk': article.pk})
        self.client.force_login(user)

        # 登録していないのでお気に入りに追加した事を示す'favorited'が返される
        response = self.client.post(url,
                                    payload,
                                    **{
                                        'Content-Type': 'application/json',
                                        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                    })
        first_json_response = json.loads(response.content)
        favorite_status = first_json_response['data']['status']
        self.assertEquals(favorite_status, 'favorited')

        # 登録済みなのでお気に入りから削除した事を示す'notfavorited'が返される
        response = self.client.post(url,
                                    payload,
                                    **{
                                        'Content-Type': 'application/json',
                                        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                    })
        second_json_response = json.loads(response.content)
        favorite_status = second_json_response['data']['status']
        self.assertEquals(favorite_status, 'notfavorited')
