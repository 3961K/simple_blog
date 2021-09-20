from django.contrib.auth import get_user_model
from django.test import TestCase

from ..templatetags.is_follow import is_follow

User = get_user_model()


class IsFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='isfollow_followee',
                                 email='isfollow_followee@test.com',
                                 password='1sf0ll0w')
        User.objects.create_user(username='isfollow_follower',
                                 email='isfollow_follower@test.com',
                                 password='1sf0ll0w')

    # is_follow()によって適切にフォロー関係を取得する事ができるか
    def test_check_status(self):
        followee = User.objects.get(username='isfollow_followee')
        follower = User.objects.get(username='isfollow_follower')

        self.assertFalse(is_follow(followee, follower))

        follower.followers.add(followee)
        follower.save()

        self.assertTrue(is_follow(followee, follower))
