from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

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
