from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
import tempfile

from .NeedImageTestMixin import NeedImageTestMixin

User = get_user_model()
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
@override_settings(AXES_ENABLED=False)
class UpdateProfileViewTest(NeedImageTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='updateprofileview_tester',
                                 email='updateprofileview@test.com',
                                 password='pr0f1le0123')

    # ログインしているユーザに関連している記事のページへアクセスする事が出来る
    def test_success_access(self):
        self.client.login(username='updateprofileview_tester',
                          password='pr0f1le0123')
        response = self.client.get(reverse('settings:profile'))
        self.assertEquals(response.status_code, 200)

    # ログインしていない状態ではアクセスする事が出来ない
    def test_fail_access_notlogin(self):
        response = self.client.get(reverse('settings:profile'))
        self.assertEquals(response.status_code, 302)

    # 縦幅・横幅1024px以下の画像と1000文字以下の文字列はアイコンとプロフィールによって更新する事が出来る
    def test_success_update_profile(self):
        self.client.login(username='updateprofileview_tester',
                          password='pr0f1le0123')

        correct_icon_dict = self.create_image_dict()
        correct_profile = {
            'icon': correct_icon_dict['icon'],
            'profile_message': 'A' * 1000,
        }
        response = self.client.post(reverse('settings:profile'),
                                    correct_profile,
                                    format='text/html')
        self.assertEquals(response.status_code, 302)

        user = User.objects.get(username='updateprofileview_tester')
        self.assertEquals(user.icon, 'images/test.png')
        self.assertEquals(user.profile_message, 'A' * 1000)
