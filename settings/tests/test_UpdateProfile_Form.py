from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import UpdateProfileForm
from .NeedImageTestMixin import NeedImageTestMixin

User = get_user_model()


class UpdateProfileFormTest(NeedImageTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='updateproileformtester',
                                 email='updateproileformtester@test.com',
                                 password='updatepr0f1le0123')

    # 縦幅・横幅1024px以下の画像と1000文字以下の文字列はアイコンとプロフィールとして妥当な値である
    def test_valid(self):
        user = User.objects.get(username='updateproileformtester')
        correct_icon_dict = self.create_image_dict()

        correct_profile = {
            'profile_message': 'A' * 1000,
        }

        form = UpdateProfileForm(user, correct_profile, correct_icon_dict)
        self.assertTrue(form.is_valid())

    # 縦幅・横幅1024px以上の画像もしくは1000文字以上の文字列はアイコンとプロフィールとして妥当な値ではない
    def test_invalid(self):
        correct_icon_dict = self.create_image_dict()
        wrong_icon_dict = self.create_image_dict(size=(1024, 1025))
        wrong_icon_dict2 = self.create_image_dict(size=(1025, 1024))

        correct_profile = {
            'profile_message': 'A' * 1000,
        }
        wrong_profile = {
            'profile_message': 'A' * 1001,
        }

        wrong_pattern_list = [
            {
                "profile": correct_profile,
                "icon": wrong_icon_dict
            },
            {
                "profile": correct_profile,
                "icon": wrong_icon_dict2
            },
            {
                "profile": wrong_profile,
                "icon": correct_icon_dict
            },
            {
                "profile": wrong_profile,
                "icon": wrong_icon_dict
            },
            {
                "profile": wrong_profile,
                "icon": wrong_icon_dict2
            }
        ]

        for wrong_pattern in wrong_pattern_list:
            form = UpdateProfileForm(wrong_pattern["profile"], wrong_pattern["icon"])
            self.assertFalse(form.is_valid())
