from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from ..models import Article, Comment

User = get_user_model()


class CommentTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
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
