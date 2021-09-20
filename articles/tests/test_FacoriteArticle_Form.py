from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import FavoriteArticleForm

User = get_user_model()


class FavoriteArticleFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='fav_tester',
                            email='fav_tester@test.com',
                            password='favtester')

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
