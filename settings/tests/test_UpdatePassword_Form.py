from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import UpdatePasswordForm

User = get_user_model()


class UpdatePasswordFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='update_password',
                                 email='updatepassword@test.com',
                                 password='update0123')

    # 正しい形式の現パスワードと新パスワードは妥当である
    def test_valid_form(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertTrue(form.is_valid())

    # 現在のパスワードが間違っている場合は妥当でない
    def test_invalid_wrong_password(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'updated0123',
            'new_password2': 'updated0123',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertFalse(form.is_valid())

    # 1つ目と2つ目の新しいパスワードが一致しない場合は妥当でない
    def test_invalid_mismatched_newpassword(self):
        user = User.objects.get(username='update_password')
        new_password_data = {
            'old_password': 'update0123',
            'new_password1': 'updated0123',
            'new_password2': 'updated01234',
        }
        form = UpdatePasswordForm(user, new_password_data)
        self.assertFalse(form.is_valid())
