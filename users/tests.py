from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, override_settings
from urllib.parse import urlencode

from .forms import FollowForm
from articles.models import Article
from authenticate.models import Relation
from .templatetags.is_follow import is_follow

# Create your tests here.

User = get_user_model()


class PostedArticleListView(TestCase):
    # 表示する記事を作成
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='posted_view',
                                 email='posted_view@test.com',
                                 password='t0pp0gev1ew')
        user = User.objects.get(username='posted_view')
        for i in range(1, 7):
            Article.objects.create(author=user,
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
            article = Article.objects.filter(title='test_title{}'.format(i))[0]
            article.save()

        return super().setUpClass()

    # posted_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:articles',
                                           kwargs={'username': 'posted_view'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:articles',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:articles',
                                           kwargs={'username': 'posted_view'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:articles',
                                                     kwargs={'username': 'posted_view'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:articles',
                                           kwargs={'username': 'posted_view'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class FavoriteListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='favorite_list_view',
                                 email='favorite_list_view@test.com',
                                 password='t0pp0gev1ew')
        user = User.objects.get(username='favorite_list_view')
        for i in range(1, 7):
            Article.objects.create(author=User.objects.first(),
                                   title='test_title{}'.format(i),
                                   content='test_content{}'.format(i))
            article = Article.objects.filter(title='test_title{}'.format(i))[0]
            article.favorite_users.add(user)
            article.save()

        return super().setUpClass()

    # favorite_list_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:favorites',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:favorites',
                                             kwargs={'username': 'favorite_list_view'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:favorites',
                                           kwargs={'username': 'favorite_list_view'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class FolloweeListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='followee_tester_{}'.format(i),
                                     email='followee_tester_{}@test.com'.format(i),
                                     password='f0ll0weetester')

        user1 = User.objects.filter(username='followee_tester_1').get()
        for i in range(2, 11):
            followee = User.objects.filter(username='followee_tester_{}'.format(i)).get()
            Relation.objects.create(followee=followee, follower=user1)

        return super().setUpClass()

    # favorite_list_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:followees',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:followees',
                                             kwargs={'username': 'followee_tester_1'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:followees',
                                           kwargs={'username': 'followee_tester_1'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class FollowerListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        for i in range(1, 11):
            User.objects.create_user(username='follower_tester_{}'.format(i),
                                     email='follower_tester_{}@test.com'.format(i),
                                     password='f0ll0wertester')

        user1 = User.objects.filter(username='follower_tester_1').get()
        for i in range(2, 11):
            follower = User.objects.filter(username='follower_tester_{}'.format(i)).get()
            Relation.objects.create(followee=user1, follower=follower)

        return super().setUpClass()

    # favorite_list_viewユーザのプロフィールにアクセスする事が出来る
    def test_success_access_page(self):
        response = self.client.get(reverse('users:followers',
                                           kwargs={'username': 'follower_tester_1'}))
        self.assertEqual(response.status_code, 200)

    # 存在しないユーザ名のプロフィールにアクセスしようとすると404が返される
    def test_fail_access_page(self):
        response = self.client.get(reverse('users:followers',
                                           kwargs={'username': 'not_exist'}))
        self.assertEqual(response.status_code, 404)

    # /?page=1・/?page=2にアクセスする事が出来る
    def test_success_access_page12(self):
        response = self.client.get(''.join([reverse('users:followers',
                                           kwargs={'username': 'follower_tester_1'}),
            '?', urlencode(dict(page='1'))]))
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get(''.join([reverse('users:followers',
                                             kwargs={'username': 'follower_tester_1'}),
                                             '?', urlencode(dict(page='2'))]))
        self.assertEqual(response2.status_code, 200)

    # /?page=6(存在しないページ)にアクセスする事が出来ない
    def test_fail_access_page_over(self):
        response = self.client.get(''.join([reverse('users:followers',
                                           kwargs={'username': 'follower_tester_1'}),
            '?', urlencode(dict(page='6'))]))
        self.assertEqual(response.status_code, 404)


class IsFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create_user(username='isfollow_followee',
                                 email='isfollow_followee@test.com',
                                 password='1sf0ll0w')
        User.objects.create_user(username='isfollow_follower',
                                 email='isfollow_follower@test.com',
                                 password='1sf0ll0w')
        return super().setUpClass()

    def test_check_status(self):
        followee = User.objects.get(username='isfollow_followee')
        follower = User.objects.get(username='isfollow_follower')

        self.assertFalse(is_follow(followee, follower))

        follower.followers.add(followee)
        follower.save()

        self.assertTrue(is_follow(followee, follower))


class FollowFormTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        User.objects.create_user(username='follow_form_tester',
                                 email='follow_form_tester@test.com',
                                 password='f0ll0f0rm')
        return super().setUpClass()

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
