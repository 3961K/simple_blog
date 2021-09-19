from django.test import TestCase, override_settings

from ..models import User
from ..forms import LoginForm


@override_settings(AXES_ENABLED=False)
class LoginFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='loginformtester',
                                 email='loginform@test.com',
                                 password='l0g1nt3st3r')

    # 正しいユーザ名・パスワードは妥当な入力値である
    def test_valid_login(self):
        login_data = {
            'username': 'loginformtester',
            'password': 'l0g1nt3st3r'
        }
        form = LoginForm(data=login_data)
        # エラー
        self.assertTrue(form.is_valid())

    # 存在しないユーザ名は妥当な入力値ではない
    def test_invalid_notexist_username(self):
        login_data = {
            'username': 'notexistuseraname',
            'password': 'l0g1nt3st3r'
        }
        # エラー
        form = LoginForm(data=login_data)
        self.assertFalse(form.is_valid())

    # ユーザ名に対して誤ったパスワードは妥当な入力値ではない
    def test_invalid_wrong_password(self):
        login_data = {
            'username': 'loginformtester',
            'password': 'wrongpassword'
        }
        # エラー
        form = LoginForm(data=login_data)
        self.assertFalse(form.is_valid())
