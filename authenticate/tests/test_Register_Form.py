from django.test import TestCase

from ..models import User
from ..forms import RegisterForm


class RegisterFormTest(TestCase):
    # 正しい形式の値は妥当である
    def test_valid_form(self):
        register_info = {
            'username': 'formtester',
            'email': 'formtester@test.com',
            'password1': 'f0rmt3st3r0123',
            'password2': 'f0rmt3st3r0123'
        }
        form = RegisterForm(data=register_info)
        self.assertTrue(form.is_valid())

    # 必須フィールドが欠けた値は妥当でない
    def test_invalid_missed_required(self):
        missied_register_info_list = [
            {
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@test.com',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123'
            },
        ]

        for missied_register_info in missied_register_info_list:
            form = RegisterForm(data=missied_register_info)
            self.assertFalse(form.is_valid())

    # 誤った形式の値は妥当では無い
    def test_invalid_wrong_format(self):
        wrong_format_register_info_list = [
            {
                'username': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@a.a',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'formtester@a.a',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0124'
            }
        ]

        for wrong_format_register_info in wrong_format_register_info_list:
            form = RegisterForm(data=wrong_format_register_info)
            self.assertFalse(form.is_valid())

    # 重複が禁止されているため既に登録されているユーザ名・メールアドレスを含んだ値は妥当でない
    def test_invalid_duplicated(self):
        User(username='exited',
             email='exited@test.com',
             password='ex1te3dpass').save()

        exited_register_info_list = [
            {
                'username': 'exited',
                'email': 'formtester@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
            {
                'username': 'formtester',
                'email': 'exited@test.com',
                'password1': 'f0rmt3st3r0123',
                'password2': 'f0rmt3st3r0123'
            },
        ]

        for exited_register_info in exited_register_info_list:
            form = RegisterForm(data=exited_register_info)
            self.assertFalse(form.is_valid())
