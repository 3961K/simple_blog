from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from ..models import Tag, Article

User = get_user_model()


class ArticleTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Tag.objects.create(tag='article_test')
        User.objects.create_user(username='article_tester',
                                 email='article@test.com',
                                 password='article1234')

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
