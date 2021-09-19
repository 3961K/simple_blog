from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import PostCommentForm

User = get_user_model()


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
