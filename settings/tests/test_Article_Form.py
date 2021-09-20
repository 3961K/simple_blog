from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import ArticleForm
from articles.models import Tag

User = get_user_model()


class ArticleFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Tag.objects.create(tag='post_article_post_test')

    # 正しいタイトル・記事内容は妥当である
    def test_valid_form(self):
        article_tag = Tag.objects.get(tag='post_article_post_test')
        article_data = {
            'title': 'A' * 1000,
            'content': 'A' * 10000,
            'tags': [article_tag]
        }

        form = ArticleForm(data=article_data)
        self.assertTrue(form.is_valid())

    # 誤った形式のタイトル・記事内容は妥当でない
    def test_invalid_wrongformat(self):
        article_tag = Tag.objects.get(tag='post_article_post_test')

        wrong_format_data_list = [
            {
                'title': 'A' * 1001,
                'content': 'sample_content',
                'tags': [article_tag]
            },
            {
                'title': 'sample_title',
                'content': 'A' * 10001,
                'tags': [article_tag]
            },
            {
                'title': 'A' * 1001,
                'content': 'A' * 10001,
                'tags': []
            }
        ]

        for wrong_format_data in wrong_format_data_list:
            form = ArticleForm(data=wrong_format_data)
            self.assertFalse(form.is_valid())
