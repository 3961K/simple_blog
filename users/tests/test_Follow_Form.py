from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import FollowForm

# Create your tests here.

User = get_user_model()


class FollowFormTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='follow_form_tester',
                                 email='follow_form_tester@test.com',
                                 password='f0ll0f0rm')

    # 30文字以下の存在するユーザのユーザ名は妥当である
    def test_valid_username(self):
        correct_test_data = {
            'follower': 'follow_form_tester'
        }
        form = FollowForm(correct_test_data)
        self.assertTrue(form.is_valid())

    # 30文字以上または存在しないユーザのユーザ名は妥当ではない
    def test_invalid_username(self):
        wrong_test_data_list = [
            {
                'follower': 'A' * 31
            },
            {
                'follower': 'notexist'
            },
        ]

        for wrong_test_data in wrong_test_data_list:
            form = FollowForm(wrong_test_data)
            self.assertFalse(form.is_valid())
