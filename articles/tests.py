from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.urls import reverse
from urllib.parse import urlencode

from .forms import FavoriteArticleForm, PostCommentForm
from .models import Tag, Article, Comment

# Create your tests here.

User = get_user_model()


class TagTest(TestCase):
    # タグを追加する事が出来る
    def test_success_create_tag(self):
        Tag.objects.create(tag='test')
        tag = Tag.objects.get(tag='test')
        self.assertIsNotNone(tag)

    # タグを削除する事が出来る
    def test_success_delete_tag(self):
        Tag.objects.create(tag='test2')
        tag = Tag.objects.get(tag='test2')
        self.assertIsNotNone(tag)

        tag.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Tag.objects.get(tag='test2')


class ArticleTest(TestCase):
    @classmethod
    def setUpClass(cls):
        Tag.objects.create(tag='article_test')
        User.objects.create_user(username='article_tester',
                                 email='article@test.com',
                                 password='article0324')

        return super().setUpClass()

    def create_article(self):
        user = User.objects.get(username='article_tester')
        author_id = user.pk
        article = Article(author_id=author_id,
                          title='test',
                          content='test content')
        return article

    # 記事を登録する事が出来る
    def test_success_create(self):
        user = User.objects.get(username='article_tester')
        author_id = user.pk

        article = self.create_article()
        article.save()

        tag = Tag.objects.get(tag='article_test')
        article.tags.add(tag)

        self.assertIsNotNone(Article.objects.get(author_id=author_id))

    # 記事を削除する事が出来る
    def test_success_delete(self):
        article = self.create_article()
        article.save()

        article.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Article.objects.get(title='test')

    # 作者のUserレコードが削除されたら自動的に関連するArticleレコードが削除される
    def test_success_delete_by_deleting_user(self):
        user = User.objects.get(username='article_tester')
        author_id = user.pk

        article = self.create_article()
        article.save()

        tag = Tag.objects.get(tag='article_test')
        article.tags.add(tag)

        self.assertIsNotNone(Article.objects.get(author_id=author_id))

        user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            article = Article.objects.get(author_id=author_id)

    # is_favorited()関数に対するテスト
    def test_is_favorited_method(self):
        user = User.objects.get(username='article_tester')
        author_id = user.pk
        article = Article(author_id=author_id,
                          title='test',
                          content='test content')
        article.save()

        # 初期状態にはfavroite_usersに追加されていないので,Falseが返される
        self.assertFalse(article.is_favorited(user))

        # favorite_usersに追加した場合はTrueが返される
        article.favorite_users.add(user)
        self.assertTrue(article.is_favorited(user))

        # favorite_usersから削除した場合はFalseが返される
        article.favorite_users.remove(user)
        self.assertFalse(article.is_favorited(user))


class CommentTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        User.objects.create_user(username='comment_tester',
                                 email='comment_test@test.com',
                                 password='c0mmentt3st')
        author = User.objects.get(username='comment_tester')
        Article.objects.create(author=author,
                               title='comment_test_title',
                               content='comment_test_content')

        User.objects.create_user(username='comment_tester2',
                                 email='comment_test2@test.com',
                                 password='c0mmentt3st')
        author2 = User.objects.get(username='comment_tester2')
        Article.objects.create(author=author2,
                               title='comment_test_title2',
                               content='comment_test_content2')
        return super().setUpClass()

    def get_comment_article_pk(self, title):
        article = Article.objects.get(title=title)
        return article.pk

    def get_comment_author_pk(self, username):
        user = User.objects.get(username=username)
        return user.pk

    # コメントのデータを作成して返す
    def create_comment_data(self, username, title):
        comment_author = User.objects.get(username=username)
        comment_article = Article.objects.get(title=title)

        comment_data = {
            'article': comment_article,
            'comment_author': comment_author,
            'content': 'test comment',
        }
        return comment_data

    # 正しい情報でコメントを作成する事が出来る
    def test_success_create_comment(self):
        comment_data = self.create_comment_data('comment_tester2',
                                                'comment_test_title')
        Comment.objects.create(**comment_data)

        comment_article_pk = self.get_comment_article_pk('comment_test_title')
        comment = Comment.objects.get(article=comment_article_pk)
        self.assertIsNotNone(comment)

    # コメントの作者が削除された場合,コメントも削除される
    def test_success_delete_comment_author(self):
        comment_data = self.create_comment_data('comment_tester2',
                                                'comment_test_title')
        Comment.objects.create(**comment_data)

        comment_author = User.objects.get(username='comment_tester2')
        comment = Comment.objects.get(comment_author=comment_author.pk)
        self.assertIsNotNone(comment)

        user = User.objects.get(pk=comment_author.pk)
        user.delete()

        with self.assertRaises(ObjectDoesNotExist):
            comment = Comment.objects.get(comment_author=comment_author.pk)

    # コメントした記事が削除された場合,コメントも削除される
    def test_success_delete_comment_article(self):
        comment_data = self.create_comment_data('comment_tester2',
                                                'comment_test_title')
        Comment.objects.create(**comment_data)

        comment_article_pk = self.get_comment_article_pk('comment_test_title')
        comment = Comment.objects.get(article=comment_article_pk)
        self.assertIsNotNone(comment)

        article = Article.objects.get(pk=comment_article_pk)
        article.delete()

        with self.assertRaises(ObjectDoesNotExist):
            comment = Comment.objects.get(article=comment_article_pk)


class FavoriteArticleFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create(username='fav_tester',
                            email='fav_tester@test.com',
                            password='favtester')
        return super().setUpClass()

    # 正しい形式のデータは妥当である
    def test_valid(self):
        correct_test_data = {
            'username': 'fav_tester'
        }
        form = FavoriteArticleForm(correct_test_data)
        self.assertTrue(form.is_valid())

    # 誤った形式のデータ(存在しない)は妥当である
    def test_invalid(self):
        wrong_test_data = {
            'username': 'i_am_not_exist'
        }
        form = FavoriteArticleForm(wrong_test_data)
        self.assertFalse(form.is_valid())


@override_settings(AXES_ENABLED=False)
class FavoriteArticleView(TestCase):
    @classmethod
    def setUpClass(cls):
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

        return super().setUpClass()

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


@override_settings(AXES_ENABLED=False)
class PostCommentFormTest(TestCase):
    # 正しい形式のデータは妥当である
    def test_valid(self):
        comment_data = {
            'content': 'A' * 1000
        }
        form = PostCommentForm(comment_data)
        self.assertTrue(form.is_valid())

    # 誤った形式のデータは妥当である
    def test_invalid_wrongformat(self):
        comment_data = {
            'content': 'A' * 1001
        }
        form = PostCommentForm(comment_data)
        self.assertFalse(form.is_valid())


@override_settings(AXES_ENABLED=False)
class PostCommentView(TestCase):
    @ classmethod
    def setUpClass(cls):
        User.objects.create_user(username='post_comment_tester',
                                 email='post_comment_test@test.com',
                                 password='c0mmentt3st')
        author = User.objects.get(username='post_comment_tester')
        Article.objects.create(author=author,
                               title='post_comment_test_title',
                               content='post_comment_test_content')
        return super().setUpClass()

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


class ArticleViewTest(TestCase):
    # 表示する記事を作成
    @ classmethod
    def setUpClass(cls):
        User.objects.create_user(username='article_view',
                                 email='article_view@test.com',
                                 password='art1clev1ew')
        for i in range(1, 6):
            Article.objects.create(author_id=User.objects.first().pk,
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
        return super().setUpClass()

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


class ArticleListViewTest(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
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

        return super().setUpClass()

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
