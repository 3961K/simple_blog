from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import UpdateUsernameForm

User = get_user_model()


class UpdateUsernameFormTest(TestCase):
    # 30文字以内の文字列はユーザ名として妥当である
    def test_valid(self):
        correct_data = {
            'username': 'A' * 30
        }
        form = UpdateUsernameForm(correct_data)
        self.assertTrue(form.is_valid())

    # 31文字以上の文字列及び空文字はユーザ名として妥当でない
    def test_invalid(self):
        wrong_data_list = [
            {
                'username': 'A' * 31
            },
            {
                'username': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateUsernameForm(wrong_data)
            self.assertFalse(form.is_valid())
