from django.test import TestCase

from ..forms import UpdateEmailForm


class UpdateEmailFormTest(TestCase):
    # 一般的なメールアドレスに近しい文字列はメールアドレスとして妥当である
    def test_valid(self):
        correct_data = {
            'email': 'ueftest@test.com'
        }
        form = UpdateEmailForm(correct_data)
        self.assertTrue(form.is_valid())

    # 一般的なメールアドレスからかけ離れている文字列と空文字はメールアドレスとして妥当である
    def test_invalid(self):
        wrong_data_list = [
            {
                'email': 'A'
            },
            {
                'email': ''
            }
        ]

        for wrong_data in wrong_data_list:
            form = UpdateEmailForm(wrong_data)
            self.assertFalse(form.is_valid())
