from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Article

User = get_user_model()


@override_settings(AXES_ENABLED=False)
class PostCommentView(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='post_comment_tester',
                                 email='post_comment_test@test.com',
                                 password='c0mmentt3st')
        author = User.objects.get(username='post_comment_tester')
        Article.objects.create(author=author,
                               title='post_comment_test_title',
                               content='post_comment_test_content')

    # ログイン状態に関わらずGETを利用した場合はリダイレクトされる
    def test_success_ridrect(self):
        # ログインをしていない場合
        article = Article.objects.get(title='post_comment_test_title')
        response = self.client.get(reverse('articles:comments',
                                           kwargs={'pk': article.pk}))
        self.assertEqual(response.status_code, 302)

        # ログインしている場合
        self.client.login(username='post_comment_tester',
                          password='c0mmentt3st')
        response2 = self.client.get(reverse('articles:comments',
                                            kwargs={'pk': article.pk}))
        self.assertEqual(response2.status_code, 302)

    # ログインしている状態で正しい形式のコメントを登録する事が出来る
    def test_success_post_comment(self):
        self.client.login(username='post_comment_tester',
                          password='c0mmentt3st')

        comment_data = {
            'content': 'A' * 1000,
        }
        article = Article.objects.get(title='post_comment_test_title')
        response = self.client.post(reverse('articles:comments',
                                            kwargs={'pk': article.pk}),
                                    comment_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # ログインしていない状態ではコメントを登録する事が出来ない
    def test_fail_post_notlogin(self):
        comment_data = {
            'content': 'A' * 1000,
        }
        article = Article.objects.get(title='post_comment_test_title')
        response = self.client.post(reverse('articles:comments',
                                            kwargs={'pk': article.pk}),
                                    comment_data,
                                    format='text/html')
        self.assertEqual(response.status_code, 302)

    # ログインしている状態でも誤った形式のコメントは投稿する事が出来ない
    def test_fail_post_comment(self):
        self.client.login(username='post_comment_tester',
                          password='c0mmentt3st')

        comment_data = {
            'content': 'A' * 1001,
        }
        article = Article.objects.get(title='post_comment_test_title')
        with self.assertRaises(IsADirectoryError):
            self.client.post(reverse('articles:comments',
                                     kwargs={'pk': article.pk}),
                             comment_data, format='text/html')
