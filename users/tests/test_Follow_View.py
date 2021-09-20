from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, override_settings

User = get_user_model()


@ override_settings(AXES_ENABLED=False)
class FollowViewTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        User.objects.create_user(username='follow_view_followee',
                                 email='follow_view_followee@test.com',
                                 password='f0ll0v1ew')
        User.objects.create_user(username='follow_view_follower',
                                 email='follow_view_follower@test.com',
                                 password='f0ll0v1ew')
        return super().setUpClass()

    # GETメソッドを利用した場合は302が返される
    def test_fail_get_method(self):
        response = self.client.get(reverse('users:follow',
                                           kwargs={'username': 'follow_view_followee'}))
        self.assertEqual(response.status_code, 302)

    # ログインせずにPOSTした場合は302が返される
    def test_fail_favorite_nologin(self):
        payload = {
            'follower': 'follow_view_follower'
        }

        url = reverse('users:follow', kwargs={
            'username': 'follow_view_followee'})
        response = self.client.post(url,
                                    payload,
                                    **{
                                        'Content-Type': 'application/json',
                                        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                    })
        self.assertEqual(response.status_code, 302)

    # followerからfolloweeに対するリレーションを作成する事と削除する事が出来る
    def test_success_follow(self):
        import json

        user = User.objects.get(username='follow_view_follower')
        self.client.force_login(user)

        payload = {
            'follower': user.username
        }
        url = reverse('users:follow', kwargs={
            'username': 'follow_view_followee'})

        # followerからfolloweeに対するフォローリレーションを作成する
        follow_response = self.client.post(url,
                                           payload,
                                           **{
                                               'Content-Type': 'application/json',
                                               'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                           })
        follow_response_json = json.loads(follow_response.content)
        follow_response_status = follow_response_json['data']['status']
        self.assertEquals(follow_response_status, 'follow')

        # followerからfolloweeに対するフォローリレーションを削除する
        unfollow_response = self.client.post(url,
                                             payload,
                                             **{
                                                 'Content-Type': 'application/json',
                                                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
                                             })
        unfollow_response_json = json.loads(unfollow_response.content)
        unfollow_response_status = unfollow_response_json['data']['status']
        self.assertEquals(unfollow_response_status, 'notfollow')
